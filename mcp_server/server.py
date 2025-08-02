"""
Main MCP Server implementation with Enhanced Monitoring
Handles MCP protocol communication and routes requests to tools
Includes detailed logging, analytics, and verification features
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
# import redis

from core.tool_registry import get_tool_registry
from mcp_server.mcp_sqlite_logger import MCPSQLiteLogger
# from monitoring import MCPLogger, MCPAnalytics, track_execution

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mcp-server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Development Assistant MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers with monitoring
# redis_client = redis.from_url("redis://localhost:6379")
tool_registry = get_tool_registry()

# Initialize monitoring
mcp_logger = MCPSQLiteLogger()
# mcp_analytics = MCPAnalytics(redis_client)

# Pydantic models
class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class MCPResponse(BaseModel):
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

# MCP Protocol handlers
class MCPHandler:
    def __init__(self):
        self.handlers = {
            "tools/list": self.list_tools,
            "tools/call": self.call_tool,
            "resources/list": self.list_resources,
            "prompts/list": self.list_prompts,
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request"""
        try:
            if request.method in self.handlers:
                result = await self.handlers[request.method](request.params)
                return MCPResponse(result=result, id=request.id)
            else:
                error = {"code": -32601, "message": f"Method not found: {request.method}"}
                return MCPResponse(error=error, id=request.id)
        
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            error = {"code": -32603, "message": f"Internal error: {str(e)}"}
            return MCPResponse(error=error, id=request.id)
    
    async def list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools"""
        tools = tool_registry.get_tool_list()
        
        return {"tools": tools}
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        try:
            result = tool_registry.execute_tool(tool_name, arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
        
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            raise ValueError(f"Tool execution failed: {str(e)}")
    
    async def list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available resources"""
        return {"resources": []}
    
    async def list_prompts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available prompts"""
        return {"prompts": []}

# Initialize MCP handler
mcp_handler = MCPHandler()

# REST API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Development Assistant MCP Server"}

@app.get("/tools")
async def list_tools_rest():
    """REST endpoint to list tools"""
    tools = tool_registry.get_tool_list()
    
    return {"tools": tools}

@app.post("/tools/execute")
async def execute_tool_rest(
    request: ToolExecutionRequest,
    http_request: Request
):
    """REST endpoint to execute a tool with enhanced monitoring"""
    start_time = time.time()
    
    # Extract client information
    client_info = {
        "client_ip": http_request.client.host,
        "user_agent": http_request.headers.get("user-agent", ""),
        "connection_type": "rest"
    }
    user_id = client_info.get("client_ip")  # Use client_ip as a stand-in for user_id
    try:
        # Execute tool
        result = tool_registry.execute_tool(request.tool_name, request.arguments)
        execution_time = time.time() - start_time
        
        # Log successful execution
        mcp_logger.log_tool_execution(
            request.tool_name,
            str(user_id),
            request.dict(),
            result,
            execution_time,
            client_info
        )
        
        logger.info(f"Tool '{request.tool_name}' executed successfully")
        
        return {"result": str(result), "status": "success", "execution_time": execution_time}
    
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        mcp_logger.log_error("tool_execution_error", str(e), str(user_id), client_info, {"tool_name": request.tool_name, "execution_time": execution_time})
        
        logger.error(f"Tool '{request.tool_name}' failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

# WebSocket endpoint for MCP protocol with monitoring
@app.websocket("/mcp")
async def mcp_websocket(websocket: WebSocket):
    """MCP WebSocket endpoint with enhanced monitoring"""
    await websocket.accept()
    
    # Log connection
    client_info = {
        "client_ip": websocket.client.host,
        "user_agent": websocket.headers.get("user-agent", ""),
        "connection_type": "websocket"
    }
    user_id = client_info.get("client_ip")
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            start_time = time.time()
            
            try:
                request_data = json.loads(message)
                mcp_request = MCPRequest(**request_data)
                response = await mcp_handler.handle_request(mcp_request)
                
                execution_time = time.time() - start_time
                
                # Log WebSocket tool execution
                if mcp_request.method == "tools/call":
                    tool_name = mcp_request.params.get("name", "unknown")
                    mcp_logger.log_tool_execution(
                        tool_name,
                        str(user_id),
                        request_data,
                        response.result,
                        execution_time,
                        client_info
                    )
                    
                    logger.info(f"WebSocket tool '{tool_name}' executed")
                
                # Send response
                await websocket.send_text(response.model_dump_json())
                
            except json.JSONDecodeError:
                error_response = MCPResponse(
                    error={"code": -32700, "message": "Parse error"}
                )
                await websocket.send_text(error_response.model_dump_json())
            
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"WebSocket error: {e}")
                
                # Log WebSocket error
                mcp_logger.log_error("websocket_error", str(e), str(user_id), client_info, {"execution_time": execution_time})
                
                error_response = MCPResponse(
                    error={"code": -32603, "message": f"Internal error: {str(e)}"}
                )
                await websocket.send_text(error_response.model_dump_json())
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        mcp_logger.log_error("websocket_connection_error", str(e), str(user_id), client_info)
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
