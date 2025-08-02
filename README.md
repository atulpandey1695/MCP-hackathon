# MCP Server (LangChain Edition)

This project is a Multi-Agent Control Plane (MCP) server using [LangChain](https://github.com/langchain-ai/langchain), [FastAPI](https://fastapi.tiangolo.com/), and dynamic tool orchestration.

## Features
- **LangChain Tool Integration**: All tools are defined as LangChain-compatible Python functions and loaded dynamically from `tools.json`.
- **REST API**: Exposes `/tools` (list tools) and `/tools/execute` (run a tool) endpoints.
- **SQLite Logging**: Tool executions and errors are logged to SQLite.
- **Agentic Workflows**: Ready for multi-agent and LLM-based orchestration.

## Quickstart
1. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
2. **Run the server**
   ```sh
   python -m uvicorn mcp_server.server:app --reload --port 8000
   ```
3. **List available tools**
   ```sh
   curl http://127.0.0.1:8000/tools
   ```
4. **Execute a tool**
   ```sh
   curl -X POST http://127.0.0.1:8000/tools/execute -H "Content-Type: application/json" -d '{"tool_name": "scan_codebase", "arguments": {"query": "python patterns"}}'
   ```

## Project Structure
- `mcp_server/` - FastAPI server, logger, and tests
- `core/tool_registry.py` - Loads and manages LangChain tools
- `tools/` - All tool implementations (must use `@tool` from LangChain)
- `tools.json` - Tool registry/configuration

## Requirements
- Python 3.9+
- See `requirements.txt` for all dependencies

## Notes
- All tools must be decorated with `@tool` from LangChain.
- The server expects `tools.json` to define each tool's name, module, and description.
- For custom tools, add your Python file to `tools/` and update `tools.json`.

---
For more, see the code and comments in each file.