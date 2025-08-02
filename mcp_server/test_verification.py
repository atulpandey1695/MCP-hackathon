"""
Quick verification that MCP server tools can be accessed locally
"""
import requests
import json

def test_local_access():
    base_url = "http://localhost:8000"
    api_key = "dev-test-key"
    headers = {"X-API-Key": api_key}
    
    print("🔍 Testing local MCP server access...")
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server reachable: {response.json()}")
    except Exception as e:
        print(f"❌ Server not running. Start with: python server.py")
        return False
    
    # Test 2: List tools
    try:
        response = requests.get(f"{base_url}/tools", headers=headers)
        tools_json = response.json()
        print("\nFull /tools JSON response:")
        print(json.dumps(tools_json, indent=2))
    except Exception as e:
        print(f"⚠️ Tool listing failed: {e}")
    
    # Test 3: Execute a tool
    try:
        payload = {
            "tool_name": "scan_codebase",
            "arguments": {"query": "python patterns"}
        }
        response = requests.post(f"{base_url}/tools/execute", headers=headers, json=payload)
        result = response.json()
        print(f"⚡ Tool execution: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"⚠️ Tool execution test failed: {e}")
    
    return True

if __name__ == "__main__":
    test_local_access()
