"""
MCP Server Testing and Verification Script
Demonstrates local access, monitoring, and tool call verification
"""
import requests
import json
import time
import asyncio
import websockets
from typing import Dict, Any

class MCPServerTester:
    def __init__(self, base_url="http://localhost:8000", api_key="dev-test-key"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def test_server_health(self):
        """Test server health and connectivity"""
        print("Testing server health...")
        try:
            response = requests.get(f"{self.base_url}/")
            print(f"Server Status: {response.json()}")
            
            # Detailed health check
            response = requests.get(f"{self.base_url}/admin/health")
            health_data = response.json()
            print(f"Detailed Health: {json.dumps(health_data, indent=2)}")
            
            return True
        except Exception as e:
            print(f"Server connection failed: {e}")
            return False
    
    def test_tool_listing(self):
        """Test tool listing endpoint"""
        print("\nTesting tool listing...")
        try:
            response = requests.get(f"{self.base_url}/tools", headers=self.headers)
            tools = response.json()
            print(f"Available tools: {json.dumps(tools, indent=2)}")
            return tools.get("tools", [])
        except Exception as e:
            print(f"Tool listing failed: {e}")
            return []
    
    def test_tool_execution(self, tool_name="scan_codebase", arguments=None):
        """Test tool execution with monitoring"""
        if arguments is None:
            arguments = {"query": "python patterns"}
        print(f"\nTesting tool execution: {tool_name}")
        try:
            payload = {
                "tool_name": tool_name,
                "arguments": arguments
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/tools/execute", 
                headers=self.headers, 
                json=payload
            )
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"Tool executed successfully in {execution_time:.2f}s")
                print(f"Result preview: {str(result.get('result', ''))[:200]}...")
                return result
            else:
                print(f"Tool execution failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Tool execution error: {e}")
            return None
    
    def test_verification_endpoint(self):
        """Test tool call verification"""
        print("\nTesting tool call verification...")
        try:
            response = requests.get(f"{self.base_url}/verify/tools", headers=self.headers)
            verification = response.json()
            
            print(f"Verification Status: {verification.get('verification_status')}")
            print(f"Total calls tracked: {verification.get('total_calls')}")
            print(f"IDE breakdown: {verification.get('ide_breakdown')}")
            print(f"Tool breakdown: {verification.get('tool_breakdown')}")
            
            return verification
        except Exception as e:
            print(f"Verification failed: {e}")
            return None
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("\nTesting analytics...")
        try:
            # Get usage stats
            response = requests.get(f"{self.base_url}/admin/analytics/stats", headers=self.headers)
            stats = response.json()
            print(f"Usage Stats: {json.dumps(stats, indent=2)}")
            
            # Get recent executions
            response = requests.get(f"{self.base_url}/admin/analytics/executions?limit=5", headers=self.headers)
            executions = response.json()
            print(f"Recent Executions: {len(executions.get('executions', []))} found")
            
            for i, execution in enumerate(executions.get('executions', [])[:3]):
                print(f"  {i+1}. {execution.get('tool_name')} from {execution.get('ide_type')} at {execution.get('timestamp')}")
            
            return stats, executions
        except Exception as e:
            print(f"Analytics failed: {e}")
            return None, None
    
    async def test_websocket_connection(self):
        """Test WebSocket MCP protocol"""
        print("\nTesting WebSocket MCP connection...")
        try:
            uri = f"ws://localhost:8000/mcp"
            
            async with websockets.connect(uri) as websocket:
                # Send MCP request
                request = {
                    "method": "tools/list",
                    "params": {},
                    "id": "test-1",
                    "apiKey": self.api_key
                }
                
                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                
                result = json.loads(response)
                print(f"WebSocket response: {json.dumps(result, indent=2)}")
                
                return result
        except Exception as e:
            print(f"WebSocket test failed: {e}")
            return None
    
    def run_comprehensive_test(self):
        """Run all tests to verify MCP server functionality"""
        print("Starting Comprehensive MCP Server Test Suite")
        print("=" * 60)
        
        # Test 1: Server Health
        if not self.test_server_health():
            print("Server not accessible. Make sure it's running on localhost:8000")
            return
        
        # Test 2: Tool Listing
        tools = self.test_tool_listing()
        if not tools:
            print("No tools available")
        
        # Test 3: Tool Execution (demo/dummy data)
        print("\nTesting demo/dummy data for key tools...")
        demo_tools = [
            ("check_git_conventions", {"query": "demo"}),
            ("analyze_git_history", {"query": "demo"}),
            ("scan_codebase", {"query": "demo"})
        ]
        for tool_name, arguments in demo_tools:
            print(f"\n--- Testing {tool_name} with demo data ---")
            result = self.test_tool_execution(tool_name, arguments)
            if result and "demo" in str(result.get("result", "")).lower():
                print(f"{tool_name} demo response verified.")
            else:
                print(f"{tool_name} did not return expected demo response.")
        
        # Test 4: Verification
        self.test_verification_endpoint()
        
        # Test 5: Analytics
        self.test_analytics()
        
        # Test 6: WebSocket (async)
        print("\nTesting WebSocket...")
        try:
            asyncio.run(self.test_websocket_connection())
        except Exception as e:
            print(f"WebSocket test failed: {e}")
        
        print("\n" + "=" * 60)
        print("Test suite completed!")
        print("Check the MCP server logs to see detailed monitoring output")

if __name__ == "__main__":
    # Create tester instance
    tester = MCPServerTester()
    
    # Run comprehensive test
    tester.run_comprehensive_test()
    
    print("\n" + "Quick Test Commands:")
    print("# Test specific tool")
    print(f"curl -X POST {tester.base_url}/tools/execute \\")
    print(f"  -H 'X-API-Key: {tester.api_key}' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"tool_name\": \"scan_codebase\", \"arguments\": {\"query\": \"test\"}}'")
    
    print("\n# Check verification")
    print(f"curl -X GET {tester.base_url}/verify/tools \\")
    print(f"  -H 'X-API-Key: {tester.api_key}'")
    
    print("\n# View analytics")
    print(f"curl -X GET {tester.base_url}/admin/analytics/stats \\")
    print(f"  -H 'X-API-Key: {tester.api_key}'")
