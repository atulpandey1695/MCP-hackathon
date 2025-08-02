import json
import importlib
from pathlib import Path
from langchain.tools import Tool

TOOLS_PATH = Path(__file__).parent.parent / "tools.json"

class ToolRegistry:
    def __init__(self):
        with open(TOOLS_PATH, "r", encoding="utf-8") as f:
            self.tools_config = json.load(f)
        self.tools = self._load_tools()

    def _load_tools(self):
        tools = []
        for tool in self.tools_config:
            module_path = tool["module"]
            func_name = tool["name"]
            mod = importlib.import_module(module_path)
            func = getattr(mod, func_name)
            tools.append(Tool(name=tool["name"], func=func, description=tool["description"]))
        return tools

    def get_tool_list(self):
        return [t.name for t in self.tools]

    def execute_tool(self, tool_name, arguments):
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        return tool.invoke(arguments)

def get_tool_registry():
    return ToolRegistry()
