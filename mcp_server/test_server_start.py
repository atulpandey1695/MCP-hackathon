#!/usr/bin/env python3
"""
Test script to verify server startup
"""
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.tool_registry import get_tool_registry
    print("✓ Successfully imported tool_registry")
    
    # Test tool registry initialization
    tool_registry = get_tool_registry()
    print("✓ Successfully initialized tool registry")
    
    # Test tool listing
    tools = tool_registry.get_tool_list()
    print(f"✓ Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n✓ All tests passed! Server should start successfully.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1) 