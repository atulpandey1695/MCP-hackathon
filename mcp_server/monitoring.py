"""
Enhanced logging and monitoring for MCP server
Provides detailed insights into tool usage, client connections, and performance
"""
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
import redis
from fastapi import Request
import asyncio

class MCPLogger:
    def __init__(self, redis_client, log_level=logging.INFO):
        self.redis_client = redis_client
        self.logger = logging.getLogger("mcp_server")
        self.setup_logging(log_level)
        
    def setup_logging(self, log_level):
        """Configure detailed logging"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # File handler
        file_handler = logging.FileHandler('logs/mcp-server.log')
        file_handler.setFormatter(formatter)
        
        self.logger.setLevel(log_level)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def log_connection(self, client_info: Dict[str, Any]):
        """Log client connection details"""
        connection_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "client_connected",
            "client_ip": client_info.get("client_ip"),
            "user_agent": client_info.get("user_agent"),
            "ide_type": self.detect_ide(client_info.get("user_agent", "")),
            "user_id": client_info.get("user_id"),
            "connection_type": client_info.get("connection_type")  # websocket/rest
        }
        
        # Log to file
        self.logger.info(f"Client Connected: {json.dumps(connection_data)}")
        
        # Store in Redis for analytics
        self.redis_client.lpush("mcp:connections", json.dumps(connection_data))
        self.redis_client.ltrim("mcp:connections", 0, 1000)  # Keep last 1000 connections
    
    def log_tool_execution(self, tool_name: str, user_id: str, 
                          request_data: Dict[str, Any], 
                          response_data: Any, execution_time: float,
                          client_info: Dict[str, Any]):
        """Log detailed tool execution"""
        execution_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "tool_executed",
            "tool_name": tool_name,
            "user_id": user_id,
            "client_ip": client_info.get("client_ip"),
            "ide_type": self.detect_ide(client_info.get("user_agent", "")),
            "execution_time_ms": execution_time * 1000,
            "request_size": len(str(request_data)),
            "response_size": len(str(response_data)),
            "success": True,
            "arguments": request_data.get("arguments", {}),
            "response_preview": str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
        }
        
        # Log to file
        self.logger.info(f"Tool Executed: {json.dumps(execution_data)}")
        
        # Store in Redis for analytics
        self.redis_client.lpush("mcp:executions", json.dumps(execution_data))
        self.redis_client.ltrim("mcp:executions", 0, 10000)  # Keep last 10000 executions
        
        # Update tool usage statistics
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.redis_client.hincrby(f"mcp:stats:{today}", f"tool:{tool_name}", 1)
        self.redis_client.hincrby(f"mcp:stats:{today}", f"user:{user_id}", 1)
        self.redis_client.hincrby(f"mcp:stats:{today}", "total_executions", 1)
    
    def log_error(self, error_type: str, error_message: str, 
                 user_id: str, client_info: Dict[str, Any], 
                 additional_data: Dict[str, Any] = None):
        """Log errors with context"""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "user_id": user_id,
            "client_ip": client_info.get("client_ip"),
            "ide_type": self.detect_ide(client_info.get("user_agent", "")),
            "additional_data": additional_data or {}
        }
        
        self.logger.error(f"Error: {json.dumps(error_data)}")
        self.redis_client.lpush("mcp:errors", json.dumps(error_data))
        self.redis_client.ltrim("mcp:errors", 0, 1000)
    
    def detect_ide(self, user_agent: str) -> str:
        """Detect IDE type from user agent"""
        user_agent_lower = user_agent.lower()
        
        if "vscode" in user_agent_lower or "visual studio code" in user_agent_lower:
            return "vscode"
        elif "intellij" in user_agent_lower or "idea" in user_agent_lower:
            return "intellij"
        elif "visual studio" in user_agent_lower and "code" not in user_agent_lower:
            return "visual_studio"
        elif "sublime" in user_agent_lower:
            return "sublime"
        elif "vim" in user_agent_lower or "neovim" in user_agent_lower:
            return "vim"
        elif "emacs" in user_agent_lower:
            return "emacs"
        elif "atom" in user_agent_lower:
            return "atom"
        else:
            return "unknown"

class MCPAnalytics:
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    def get_usage_stats(self, date: str = None) -> Dict[str, Any]:
        """Get usage statistics for a specific date"""
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        stats_key = f"mcp:stats:{date}"
        raw_stats = self.redis_client.hgetall(stats_key)
        
        stats = {}
        tool_stats = {}
        user_stats = {}
        
        for key, value in raw_stats.items():
            key_str = key.decode() if isinstance(key, bytes) else key
            value_int = int(value.decode() if isinstance(value, bytes) else value)
            
            if key_str.startswith("tool:"):
                tool_name = key_str[5:]  # Remove "tool:" prefix
                tool_stats[tool_name] = value_int
            elif key_str.startswith("user:"):
                user_id = key_str[5:]  # Remove "user:" prefix
                user_stats[user_id] = value_int
            else:
                stats[key_str] = value_int
        
        return {
            "date": date,
            "total_executions": stats.get("total_executions", 0),
            "tool_usage": tool_stats,
            "user_activity": user_stats
        }
    
    def get_active_connections(self) -> List[Dict[str, Any]]:
        """Get recent active connections"""
        connections = self.redis_client.lrange("mcp:connections", 0, 50)
        return [json.loads(conn.decode() if isinstance(conn, bytes) else conn) 
                for conn in connections]
    
    def get_recent_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent tool executions"""
        executions = self.redis_client.lrange("mcp:executions", 0, limit - 1)
        return [json.loads(exec.decode() if isinstance(exec, bytes) else exec) 
                for exec in executions]
    
    def get_error_summary(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors"""
        errors = self.redis_client.lrange("mcp:errors", 0, limit - 1)
        return [json.loads(err.decode() if isinstance(err, bytes) else err) 
                for err in errors]

# Decorator for tracking tool executions
def track_execution(mcp_logger: MCPLogger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log successful execution
                # (Implementation would extract relevant data from args/kwargs)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log error
                # (Implementation would extract relevant data from args/kwargs)
                
                raise e
        return wrapper
    return decorator
