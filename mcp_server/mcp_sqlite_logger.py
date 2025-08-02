import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional

class MCPSQLiteLogger:
    def __init__(self, db_path='logs/mcp-server.db', log_level=logging.INFO):
        self.db_path = db_path
        self.logger = logging.getLogger("mcp_server")
        self.setup_logging(log_level)
        self._init_db()

    def setup_logging(self, log_level):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        file_handler = logging.FileHandler('logs/mcp-server.log')
        file_handler.setFormatter(formatter)
        self.logger.setLevel(log_level)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tool_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event TEXT,
            tool_name TEXT,
            user_id TEXT,
            client_ip TEXT,
            ide_type TEXT,
            execution_time_ms REAL,
            request_size INTEGER,
            response_size INTEGER,
            success INTEGER,
            arguments TEXT,
            response_preview TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event TEXT,
            error_type TEXT,
            error_message TEXT,
            user_id TEXT,
            client_ip TEXT,
            ide_type TEXT,
            additional_data TEXT
        )''')
        conn.commit()
        conn.close()

    def log_tool_execution(self, tool_name: str, user_id: str, request_data: Dict[str, Any], response_data: Any, execution_time: float, client_info: Dict[str, Any]):
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
            "arguments": json.dumps(request_data.get("arguments", {})),
            "response_preview": str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
        }
        self.logger.info(f"Tool Executed: {json.dumps(execution_data)}")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO tool_executions (timestamp, event, tool_name, user_id, client_ip, ide_type, execution_time_ms, request_size, response_size, success, arguments, response_preview) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (execution_data["timestamp"], execution_data["event"], execution_data["tool_name"], execution_data["user_id"], execution_data["client_ip"], execution_data["ide_type"], execution_data["execution_time_ms"], execution_data["request_size"], execution_data["response_size"], int(execution_data["success"]), execution_data["arguments"], execution_data["response_preview"]))
        conn.commit()
        conn.close()

    def log_error(self, error_type: str, error_message: str, user_id: str, client_info: Dict[str, Any], additional_data: Dict[str, Any] = None):
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "user_id": user_id,
            "client_ip": client_info.get("client_ip"),
            "ide_type": self.detect_ide(client_info.get("user_agent", "")),
            "additional_data": json.dumps(additional_data or {})
        }
        self.logger.error(f"Error: {json.dumps(error_data)}")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO errors (timestamp, event, error_type, error_message, user_id, client_ip, ide_type, additional_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (error_data["timestamp"], error_data["event"], error_data["error_type"], error_data["error_message"], error_data["user_id"], error_data["client_ip"], error_data["ide_type"], error_data["additional_data"]))
        conn.commit()
        conn.close()

    def detect_ide(self, user_agent: str) -> str:
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
