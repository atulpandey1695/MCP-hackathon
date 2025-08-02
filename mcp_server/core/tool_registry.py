"""
Tool registry and routing for MCP server
Maps tool names to implementations and handles tool discovery
"""
import importlib
import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# Refactored ToolRegistry to dynamically load tools.json and transform its structure
class ToolRegistry:
    def __init__(self, tools_config_path: str = None):
        self.tools = {}
        self.tool_functions = {}

        if tools_config_path:
            self.load_tools_from_config(tools_config_path)
        else:
            raise ValueError("tools.json configuration file is required")

    def load_tools_from_config(self, config_path: str):
        """Load tools from JSON configuration file"""
        with open(config_path, 'r') as f:
            tools_config = json.load(f)

        for tool_config in tools_config:
            self.register_tool_from_config(tool_config)

    def register_tool_from_config(self, tool_config: Dict[str, Any]):
        """Register a tool from configuration"""
        tool_name = tool_config["name"]
        module_path = tool_config["module"]
        description = tool_config.get("description", "")
        args_schema = tool_config.get("args_schema", {})

        # Import the module and get the function
        try:
            # Add parent directory to Python path for imports
            import sys
            parent_dir = str(Path(__file__).parent.parent.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            module = importlib.import_module(module_path)
            tool_function = getattr(module, tool_name)
            self.register_tool(tool_name, tool_function, description, args_schema)
        except (ImportError, AttributeError) as e:
            print(f"Failed to register tool {tool_name} from module {module_path}: {e}")

    def register_tool(self, name: str, function: Callable, description: str, args_schema: Dict[str, Any]):
        """Register a tool with the registry"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "args_schema": args_schema
        }
        self.tool_functions[name] = function

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool definition by name"""
        return self.tools.get(name)

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if name not in self.tool_functions:
            raise ValueError(f"Tool '{name}' not found")

        tool_function = self.tool_functions[name]
        return tool_function(**args)

# Global tool registry instance
tool_registry = None

# Updated get_tool_registry to locate tools.json in the root directory
def get_tool_registry() -> ToolRegistry:
    """Get global tool registry instance"""
    global tool_registry
    if tool_registry is None:
        config_path = Path(__file__).parent.parent.parent / "tools.json"
        if config_path.exists():
            tool_registry = ToolRegistry(str(config_path))
        else:
            raise FileNotFoundError("tools.json configuration file not found in the root directory")
    return tool_registry
