#!/usr/bin/env python3
"""
Professional MCP Tools Suite
Enterprise-grade tool execution and management platform
"""

import streamlit as st
import json
import os
import sys
import importlib
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
import hashlib

# Add tools directory to Python path
sys.path.append('tools')
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Try to import chatbot components with graceful fallback
try:
    from chatbot import Chatbot, question_answering
    CHATBOT_AVAILABLE = True
except ImportError as e:
    CHATBOT_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import bot.py for chat functionality
try:
    from bot import chat_with_bot
    BOT_AVAILABLE = True
except ImportError as e:
    BOT_AVAILABLE = False
    BOT_IMPORT_ERROR = str(e)
    
    # Fallback function
    def chat_with_bot(user_input):
        return "Bot is not available. Please ensure bot.py is properly configured with OpenAI API key and FAISS index."
    
    # Fallback classes for demo mode
    class Chatbot:
        def __init__(self, **kwargs):
            pass
        def chat(self, message):
            return "System in demo mode. Install dependencies for full functionality: pip install langchain-openai langchain"
    
    def question_answering(query):
        return "System in demo mode. Install dependencies for full functionality."

# Configure Streamlit with professional settings
st.set_page_config(
    page_title="AI Powered Org Level Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling with business-standard design
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary-navy: #1a365d;
        --secondary-blue: #2b77d9;
        --accent-teal: #319795;
        --success-green: #38a169;
        --warning-amber: #d69e2e;
        --danger-red: #e53e3e;
        --neutral-50: #f7fafc;
        --neutral-100: #edf2f7;
        --neutral-200: #e2e8f0;
        --neutral-300: #cbd5e0;
        --neutral-700: #4a5568;
        --neutral-800: #2d3748;
        --neutral-900: #1a202c;
    }
    
    /* Hide Streamlit branding for professional appearance */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1rs6os {visibility: hidden;}
    .css-17ziqus {visibility: hidden;}
    
    /* Main application header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-blue) 100%);
        padding: 2rem 3rem 1.5rem 3rem;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 8px 32px rgba(26, 54, 93, 0.15);
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .brand-section {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .brand-icon {
        width: 48px;
        height: 48px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .brand-text h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.025em;
    }
    
    .brand-text .tagline {
        font-size: 0.95rem;
        opacity: 0.85;
        font-weight: 400;
        margin: 0;
    }
    
    .system-status {
        display: flex;
        align-items: center;
        background: rgba(56, 161, 105, 0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        background: #38a169;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Tool cards with professional styling */
    .tool-card {
        background: white;
        border: 1px solid var(--neutral-200);
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        border-left: 4px solid var(--accent-teal);
    }
    
    .tool-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
        border-left-color: var(--secondary-blue);
    }
    
    .tool-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .tool-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--neutral-800);
        margin: 0;
    }
    
    .tool-category {
        background: var(--neutral-100);
        color: var(--neutral-700);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .tool-description {
        color: var(--neutral-700);
        line-height: 1.6;
        margin: 0 0 1.5rem 0;
    }
    
    .tool-status {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.875rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .status-available {
        background: rgba(56, 161, 105, 0.1);
        color: var(--success-green);
        border: 1px solid rgba(56, 161, 105, 0.2);
    }
    
    .status-error {
        background: rgba(229, 62, 62, 0.1);
        color: var(--danger-red);
        border: 1px solid rgba(229, 62, 62, 0.2);
    }
    
    .status-warning {
        background: rgba(214, 158, 46, 0.1);
        color: var(--warning-amber);
        border: 1px solid rgba(214, 158, 46, 0.2);
    }
    
    /* Execution interface styling */
    .execution-panel {
        background: var(--neutral-50);
        border: 1px solid var(--neutral-200);
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .execution-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--neutral-800);
        margin: 0 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--neutral-200);
    }
    
    .parameter-group {
        margin-bottom: 1.5rem;
    }
    
    .parameter-label {
        display: block;
        font-weight: 600;
        color: var(--neutral-700);
        margin-bottom: 0.5rem;
    }
    
    .required-indicator {
        color: var(--danger-red);
        margin-left: 0.25rem;
    }
    
    /* Results display */
    .result-container {
        background: white;
        border: 1px solid var(--neutral-200);
        border-radius: 12px;
        overflow: hidden;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .result-header {
        background: var(--neutral-100);
        padding: 1rem 1.5rem;
        border-bottom: 1px solid var(--neutral-200);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .result-title {
        font-weight: 600;
        color: var(--neutral-800);
        margin: 0;
    }
    
    .execution-time {
        font-size: 0.875rem;
        color: var(--neutral-700);
        background: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        border: 1px solid var(--neutral-300);
    }
    
    .result-content {
        padding: 1.5rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Professional buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-blue) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.025em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(43, 119, 217, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(43, 119, 217, 0.3);
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: var(--neutral-100);
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        color: var(--neutral-700);
        font-weight: 500;
        border: none;
        padding: 0 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: var(--primary-navy);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--neutral-50);
    }
    
    /* Metrics and statistics */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        text-align: center;
        border-top: 3px solid var(--accent-teal);
        margin: 0.75rem 0;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--primary-navy);
        margin: 0;
    }
    
    .metric-label {
        color: var(--neutral-700);
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* ChatGPT-like interface styling */
    .mode-info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    }
    
    .mode-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .mode-icon {
        font-size: 1.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    .mode-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }
    
    .mode-description {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    
    .mode-tools {
        font-size: 0.85rem;
        opacity: 0.8;
        font-style: italic;
    }
    
    .welcome-message {
        background: linear-gradient(135deg, var(--neutral-50), var(--neutral-100));
        border: 1px solid var(--neutral-200);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }
    
    .welcome-content {
        font-size: 1.1rem;
        color: var(--neutral-700);
        line-height: 1.6;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Enhanced chat messages */
    .chat-message {
        margin: 1.5rem 0;
        padding: 0;
        border-radius: 16px;
        max-width: 85%;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        margin-left: auto;
        border-radius: 16px 16px 4px 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
        max-width: 70%;
    }
    
    .assistant-message {
        background: white;
        color: var(--neutral-800);
        border: 1px solid var(--neutral-200);
        border-radius: 16px 16px 16px 4px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        max-width: 80%;
        margin-right: auto;
    }
    
    .assistant-avatar {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--accent-teal), var(--success-green));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
        margin-top: 0.25rem;
        box-shadow: 0 2px 8px rgba(49, 151, 149, 0.3);
    }
    
    .message-content {
        flex: 1;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .user-message .message-content {
        margin: 0;
    }
    
    .assistant-message .message-content {
        margin-left: 0.5rem;
    }
    
    /* Quick actions styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-blue) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(43, 119, 217, 0.2);
        border-left: 4px solid var(--accent-teal);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(43, 119, 217, 0.3);
        border-left-color: var(--success-green);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(43, 119, 217, 0.2);
    }
    
    /* Chat input enhancement */
    .stChatInput > div > div > div > div {
        border-radius: 24px;
        border: 2px solid var(--neutral-200);
        background: white;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stChatInput > div > div > div > div:focus-within {
        border-color: var(--secondary-blue);
        box-shadow: 0 4px 16px rgba(43, 119, 217, 0.15);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > div {
        background: white;
        border: 2px solid var(--neutral-200);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > div:focus-within {
        border-color: var(--secondary-blue);
        box-shadow: 0 4px 16px rgba(43, 119, 217, 0.15);
    }
    
    /* Conversation history styling */
    .conversation-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background: var(--neutral-50);
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: var(--neutral-100);
        border-radius: 12px;
        margin: 1rem 0;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* Session information */
    .session-card {
        background: white;
        border: 1px solid var(--neutral-200);
        border-radius: 10px;
        padding: 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .session-header {
        font-weight: 600;
        color: var(--neutral-800);
        margin: 0 0 0.75rem 0;
    }
    
    .session-detail {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
    
    .session-label {
        color: var(--neutral-700);
        font-weight: 500;
    }
    
    .session-value {
        color: var(--neutral-800);
    }
    
    /* Alert messages */
    .custom-alert {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 4px solid;
        font-weight: 500;
    }
    
    .alert-info {
        background: rgba(43, 119, 217, 0.1);
        border-color: var(--secondary-blue);
        color: var(--secondary-blue);
    }
    
    .alert-warning {
        background: rgba(214, 158, 46, 0.1);
        border-color: var(--warning-amber);
        color: #9c4221;
    }
    
    .alert-success {
        background: rgba(56, 161, 105, 0.1);
        border-color: var(--success-green);
        color: var(--success-green);
    }
    
    /* Loading states */
    .loading-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: var(--neutral-50);
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Export functionality */
    .export-section {
        background: white;
        border: 1px solid var(--neutral-200);
        border-radius: 10px;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    .export-header {
        font-weight: 600;
        color: var(--neutral-800);
        margin: 0 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load tools configuration
@st.cache_data
def load_tools_config():
    """Load tools configuration from tools.json"""
    try:
        with open("tools.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading tools configuration: {e}")
        return []

class ProfessionalToolManager:
    """Enterprise-grade tool execution and management system"""
    
    def __init__(self):
        self.tools_config = load_tools_config()
        self.loaded_tools = {}
        self.execution_log = []
        self.session_stats = {
            "tools_executed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0
        }
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize and validate all available tools"""
        for tool_config in self.tools_config:
            try:
                module_path = tool_config["module"]
                tool_name = tool_config["name"]
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Get the function
                if hasattr(module, tool_name):
                    tool_func = getattr(module, tool_name)
                    self.loaded_tools[tool_name] = {
                        "function": tool_func,
                        "config": tool_config,
                        "status": "available",
                        "executions": 0,
                        "last_executed": None
                    }
                else:
                    self.loaded_tools[tool_name] = {
                        "function": None,
                        "config": tool_config,
                        "status": "function_not_found",
                        "executions": 0,
                        "last_executed": None
                    }
                    
            except ImportError as e:
                self.loaded_tools[tool_name] = {
                    "function": None,
                    "config": tool_config,
                    "status": f"import_error: {str(e)}",
                    "executions": 0,
                    "last_executed": None
                }
            except Exception as e:
                self.loaded_tools[tool_name] = {
                    "function": None,
                    "config": tool_config,
                    "status": f"error: {str(e)}",
                    "executions": 0,
                    "last_executed": None
                }
    
    def get_available_tools(self) -> List[str]:
        """Get list of successfully loaded tools"""
        return [name for name, info in self.loaded_tools.items() 
                if info["status"] == "available"]
    
    def get_all_tools(self) -> Dict[str, Dict]:
        """Get all tools with their status"""
        return self.loaded_tools
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get tool configuration"""
        if tool_name in self.loaded_tools:
            return self.loaded_tools[tool_name]["config"]
        return {}
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with comprehensive error handling and logging"""
        if tool_name not in self.loaded_tools:
            return self._create_error_result(tool_name, "Tool not found", arguments)
        
        tool_info = self.loaded_tools[tool_name]
        if tool_info["status"] != "available":
            return self._create_error_result(tool_name, f"Tool unavailable: {tool_info['status']}", arguments)
        
        start_time = datetime.now()
        
        try:
            tool_func = tool_info["function"]
            
            # Check if this is a LangChain tool (has 'invoke' method)
            if hasattr(tool_func, 'invoke'):
                # For LangChain tools, use invoke method
                result = tool_func.invoke(arguments)
            elif hasattr(tool_func, 'run'):
                # Alternative LangChain method
                if len(arguments) == 1 and "query" in arguments:
                    result = tool_func.run(arguments["query"])
                else:
                    result = tool_func.run(**arguments)
            else:
                # Execute the tool based on its parameter signature
                if len(arguments) == 1 and "query" in arguments:
                    result = tool_func(arguments["query"])
                else:
                    result = tool_func(**arguments)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update statistics
            self.session_stats["tools_executed"] += 1
            self.session_stats["successful_executions"] += 1
            self.session_stats["total_execution_time"] += execution_time
            self.loaded_tools[tool_name]["executions"] += 1
            self.loaded_tools[tool_name]["last_executed"] = start_time.isoformat()
            
            execution_result = {
                "success": True,
                "result": str(result),
                "tool": tool_name,
                "arguments": arguments,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
            
            self.execution_log.append(execution_result)
            return execution_result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update statistics
            self.session_stats["tools_executed"] += 1
            self.session_stats["failed_executions"] += 1
            self.session_stats["total_execution_time"] += execution_time
            
            error_result = {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "arguments": arguments,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat(),
                "traceback": traceback.format_exc()
            }
            
            self.execution_log.append(error_result)
            return error_result
    
    def _create_error_result(self, tool_name: str, error: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            "success": False,
            "error": error,
            "tool": tool_name,
            "arguments": arguments,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        stats = self.session_stats.copy()
        
        if stats["tools_executed"] > 0:
            stats["success_rate"] = (stats["successful_executions"] / stats["tools_executed"]) * 100
            stats["average_execution_time"] = stats["total_execution_time"] / stats["tools_executed"]
        else:
            stats["success_rate"] = 0
            stats["average_execution_time"] = 0
        
        return stats

# Session management functions
def init_session_state():
    """Initialize all session state variables"""
    if "tool_manager" not in st.session_state:
        st.session_state.tool_manager = ProfessionalToolManager()
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None
    if "execution_history" not in st.session_state:
        st.session_state.execution_history = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = Chatbot()
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "session_name" not in st.session_state:
        st.session_state.session_name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M')}"
    if "session_metadata" not in st.session_state:
        st.session_state.session_metadata = {
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0
        }

def load_conversation_history():
    """Load conversation history from file"""
    try:
        if os.path.exists("chatbot_context.json"):
            with open("chatbot_context.json", "r", encoding="utf-8") as f:
                context = json.load(f)
                return context
    except:
        pass
    return []

def save_conversation_history(history):
    """Save conversation history to file"""
    try:
        # Update metadata
        st.session_state.session_metadata["last_activity"] = datetime.now().isoformat()
        st.session_state.session_metadata["message_count"] = len(history)
        
        # Save to main context file
        with open("chatbot_context.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        # Save session backup
        session_file = f"sessions/session_{st.session_state.session_id}.json"
        os.makedirs("sessions", exist_ok=True)
        session_data = {
            "session_id": st.session_state.session_id,
            "session_name": st.session_state.session_name,
            "metadata": st.session_state.session_metadata,
            "conversation": history
        }
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

def render_professional_header():
    """Render professional application header"""
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="brand-section">
                <div class="brand-icon">🏢</div>
                <div class="brand-text">
                    <h1>AI Powered Org Level Assistant</h1>
                    <div class="tagline">Empowering Developers, Product Owners & Teams with Intelligent Insights</div>
                </div>
            </div>
            <div class="system-status">
                <div class="status-indicator"></div>
                Organization AI Ready
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chatgpt_interface():
    """Render ChatGPT-like interface with intelligent conversation"""
    
    # Show AI integration status
    if BOT_AVAILABLE:
        st.markdown("""
        <div class="custom-alert alert-success">
            <strong>Organization AI Engine Active:</strong> Comprehensive assistance for development teams and product management
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="custom-alert alert-warning">
            <strong>Organization AI Engine Unavailable:</strong> {BOT_IMPORT_ERROR}
        </div>
        """, unsafe_allow_html=True)

    # Debug: Show available tools in sidebar (for development)
    with st.sidebar:
        st.markdown("### 🔧 Tool Debug Info")
        tool_manager = st.session_state.tool_manager
        available_tools = tool_manager.get_available_tools()
        all_tools = tool_manager.get_all_tools()
        
        st.markdown(f"**Available Tools:** {len(available_tools)}")
        for tool in available_tools:
            st.success(f"✅ {tool}")
        
        st.markdown(f"**Total Tools:** {len(all_tools)}")
        for tool_name, info in all_tools.items():
            if info["status"] != "available":
                st.error(f"❌ {tool_name}: {info['status']}")

    # Collapsible Multi-Agent Tool Selection Interface
    with st.expander("Organization Intelligence & Analytics Hub", expanded=False):
        st.markdown("**Enterprise-Level Analysis Tools for Development Teams & Product Management**")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Get available tools
            tool_manager = st.session_state.tool_manager
            available_tools = tool_manager.get_available_tools()
            
            # Define three main organizational tools
            org_tools = {
                "JIRA Project Analysis": "jira_ticket_summarizer",
                "Git Repository Analysis": "fetch_remote_git_history", 
                "Codebase Intelligence": "train_agent_on_github_repo"
            }
            
            # Filter to only show available tools
            available_org_tools = {name: tool for name, tool in org_tools.items() 
                                 if tool in available_tools}
            
            if not available_org_tools:
                st.warning("No organizational analysis tools are currently available. Please check tool configuration.")
                available_org_tools = {"Demo Mode": "demo_tool"}
            
            selected_analysis = st.selectbox(
                "Choose Organization Analysis:",
                ["None"] + list(available_org_tools.keys()),
                help="Select the type of organizational analysis you need",
                key="selected_analysis_dropdown"
            )
        
        with col2:
            # Tool execution interface
            if selected_analysis and selected_analysis != "None":
                if selected_analysis in available_org_tools:
                    actual_tool = available_org_tools[selected_analysis]
                    
                    # JIRA Project Analysis - 4 specific fields
                    if selected_analysis == "JIRA Project Analysis":
                        st.markdown("**📊 JIRA Configuration & Analysis**")
                        
                        jira_domain = st.text_input(
                            "JIRA Domain URL:",
                            placeholder="https://yourcompany.atlassian.net",
                            help="Your JIRA instance URL (e.g., https://company.atlassian.net)",
                            key="jira_domain"
                        )
                        
                        jira_username = st.text_input(
                            "JIRA Username/Email:",
                            placeholder="your.email@company.com",
                            help="Your JIRA account username or email address",
                            key="jira_username"
                        )
                        
                        jira_token = st.text_input(
                            "JIRA API Token:",
                            type="password",
                            placeholder="Your JIRA API token",
                            help="Generate API token from JIRA Account Settings > Security > API Tokens",
                            key="jira_token"
                        )
                        
                        jira_query = st.text_area(
                            "Analysis Query:",
                            placeholder="Describe what you want to analyze: project metrics, sprint performance, issue patterns, team productivity, etc.",
                            help="Specify what insights you need from your JIRA data",
                            height=100,
                            key="jira_query_area"
                        )
                        
                        if st.button(f"Analyze JIRA Project Data", type="primary", key="execute_jira_btn"):
                            if all([jira_domain.strip(), jira_username.strip(), jira_token.strip(), jira_query.strip()]):
                                with st.spinner(f"Connecting to JIRA and analyzing data..."):
                                    try:
                                        # Pass JIRA parameters using keyword arguments directly to the function
                                        result = tool_manager.execute_tool(actual_tool, {
                                            "domain": jira_domain,
                                            "user": jira_username, 
                                            "token": jira_token,
                                            "query": jira_query
                                        })
                                        
                                        if result["success"]:
                                            st.success(f"JIRA analysis completed successfully!")
                                            with st.expander("JIRA Project Intelligence Report", expanded=True):
                                                st.markdown(f"**Analysis Type:** {selected_analysis}")
                                                st.markdown(f"**JIRA Instance:** {jira_domain}")
                                                st.markdown(f"**Analysis Duration:** {result['execution_time']:.2f} seconds")
                                                st.code(result["result"], language="text")
                                                
                                                if st.button("Discuss JIRA Insights with Organization AI", key="send_jira_to_chat"):
                                                    tool_summary = f"JIRA Analysis from {jira_domain}\nQuery: {jira_query}\nInsights: {result['result'][:500]}..."
                                                    st.session_state.tool_results_for_chat = tool_summary
                                                    st.success("JIRA insights prepared for organization-level discussion!")
                                        else:
                                            st.error(f"JIRA analysis failed: {result.get('error', 'Unknown error')}")
                                            st.info("💡 **Tip:** Verify your JIRA credentials and domain URL are correct.")
                                    except Exception as e:
                                        st.error(f"JIRA connection error: {str(e)}")
                                        st.info("💡 **Tip:** Check your JIRA domain URL, username, and API token.")
                            else:
                                st.warning("Please fill in all JIRA configuration fields.")
                    
                    # Git Repository Analysis - Original format
                    elif selected_analysis == "Git Repository Analysis":
                        tool_query = st.text_area(
                            "Organization Data & Context:",
                            value="",
                            placeholder=f"Describe your project status, team metrics, development progress, or provide relevant data for {selected_analysis.lower()}...",
                            help="Enter project information, team data, development metrics, or organizational context for comprehensive analysis",
                            height=120,
                            key="git_tool_input_area"
                        )
                        
                        if st.button(f"Generate Organization Insights", type="primary", key="execute_git_btn"):
                            if tool_query.strip():
                                with st.spinner(f"Analyzing organizational data..."):
                                    try:
                                        result = tool_manager.execute_tool(actual_tool, {"repo_url": tool_query})
                                        
                                        if result["success"]:
                                            st.success(f"Organization insights generated successfully!")
                                            with st.expander("Organization Intelligence Report", expanded=True):
                                                st.markdown(f"**Analysis Type:** {selected_analysis}")
                                                st.markdown(f"**Analysis Duration:** {result['execution_time']:.2f} seconds")
                                                st.code(result["result"], language="text")
                                                
                                                if st.button("Discuss Insights with Organization AI", key="send_git_to_chat"):
                                                    tool_summary = f"Organization Analysis: {selected_analysis}\nData Context: {tool_query}\nInsights: {result['result'][:500]}..."
                                                    st.session_state.tool_results_for_chat = tool_summary
                                                    st.success("Insights prepared for organization-level discussion!")
                                        else:
                                            st.error(f"Organization analysis failed: {result.get('error', 'Unknown error')}")
                                            st.info("💡 **Tip:** Try providing more specific information or check if the tool supports your query format.")
                                    except Exception as e:
                                        st.error(f"Analysis execution error: {str(e)}")
                                        st.info("💡 **Tip:** Please verify your input format and try again.")
                            else:
                                st.warning("Please provide organizational data or context for comprehensive analysis.")
                    
                    # Codebase Intelligence - Original format
                    elif selected_analysis == "Codebase Intelligence":
                        tool_query = st.text_area(
                            "Organization Data & Context:",
                            value="",
                            placeholder=f"Describe your project status, team metrics, development progress, or provide relevant data for {selected_analysis.lower()}...",
                            help="Enter project information, team data, development metrics, or organizational context for comprehensive analysis",
                            height=120,
                            key="codebase_tool_input_area"
                        )
                        
                        if st.button(f"Generate Organization Insights", type="primary", key="execute_codebase_btn"):
                            if tool_query.strip():
                                with st.spinner(f"Analyzing organizational data..."):
                                    try:
                                        result = tool_manager.execute_tool(actual_tool, {"query": tool_query})
                                        
                                        if result["success"]:
                                            st.success(f"Organization insights generated successfully!")
                                            with st.expander("Organization Intelligence Report", expanded=True):
                                                st.markdown(f"**Analysis Type:** {selected_analysis}")
                                                st.markdown(f"**Analysis Duration:** {result['execution_time']:.2f} seconds")
                                                st.code(result["result"], language="text")
                                                
                                                if st.button("Discuss Insights with Organization AI", key="send_codebase_to_chat"):
                                                    tool_summary = f"Organization Analysis: {selected_analysis}\nData Context: {tool_query}\nInsights: {result['result'][:500]}..."
                                                    st.session_state.tool_results_for_chat = tool_summary
                                                    st.success("Insights prepared for organization-level discussion!")
                                        else:
                                            st.error(f"Organization analysis failed: {result.get('error', 'Unknown error')}")
                                            st.info("💡 **Tip:** Try providing more specific information or check if the tool supports your query format.")
                                    except Exception as e:
                                        st.error(f"Analysis execution error: {str(e)}")
                                        st.info("💡 **Tip:** Please verify your input format and try again.")
                            else:
                                st.warning("Please provide organizational data or context for comprehensive analysis.")
                else:
                    st.info("Please select an analysis type to proceed.")
    
    st.markdown("---")
    
    # Main Chat Interface - Always uses advanced AI
    st.markdown("### AI Powered Organization Assistant")
    
    # Load main conversation history (not mode-specific)
    if "main_conversation" not in st.session_state:
        st.session_state.main_conversation = []
    
    conversation_history = st.session_state.main_conversation
    
    # Chat container with ChatGPT-like styling
    chat_container = st.container()
    
    with chat_container:
        if not conversation_history:
            # Welcome message for main chat
            st.markdown(f"""
            <div class="welcome-message">
                <div class="welcome-content">
                    Welcome to your AI Powered Organization Level Assistant! I provide comprehensive support for development teams and product management.
                    <br><br>
                    <strong>For Developers:</strong> Code analysis, architecture insights, Git workflows, and technical documentation
                    <br><br>
                    <strong>For Product Owners:</strong> Project estimates, sprint progress tracking, delivery timelines, and team productivity insights
                    <br><br>
                    <strong>For Teams:</strong> JIRA analytics, workflow optimization, collaboration patterns, and organizational metrics
                    <br><br>
                    Ask questions about your development projects, team performance, or organizational processes for intelligent, data-driven insights.
                    <br><br>
                    <strong>Need specific organizational analysis? Use the Organization Intelligence Hub above.</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Display conversation history
    for i, message in enumerate(conversation_history):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="assistant-avatar">AI</div>
                <div class="message-content">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Check if tool results should be auto-added to chat
    if "tool_results_for_chat" in st.session_state:
        auto_message = f"Please analyze these organizational insights:\n\n{st.session_state.tool_results_for_chat}"
        del st.session_state.tool_results_for_chat
        st.rerun()
    
    # Chat input - always powered by advanced AI
    if prompt := st.chat_input("Ask about development progress, team metrics, project estimates, or any organizational insights..."):
        # Add user message
        user_message = {"role": "user", "content": prompt}
        conversation_history.append(user_message)
        
        # Get AI response using advanced intelligence
        with st.spinner("Processing organizational request with AI intelligence..."):
            if BOT_AVAILABLE:
                response = chat_with_bot(prompt)
            else:
                response = f"**Organization AI Assistant** *(AI Engine Unavailable)*\n\nRegarding: '{prompt}'\n\n{BOT_IMPORT_ERROR}\n\nPlease ensure:\n• Organization AI engine is properly configured\n• API access is available\n• Knowledge base is accessible\n\nThis assistant is designed to provide intelligent organizational insights for development teams and product management."
        
        # Add assistant response
        assistant_message = {"role": "assistant", "content": response}
        conversation_history.append(assistant_message)
        
        # Save conversation
        st.session_state.main_conversation = conversation_history
        save_conversation_history(conversation_history, "Organization Chat")
        
        # Rerun to show new messages
        st.rerun()

def load_conversation_history():
    """Load conversation history from file"""
    try:
        if os.path.exists("chatbot_context.json"):
            with open("chatbot_context.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def save_conversation_history(history, mode="AI Assistant"):
    """Save conversation history to file with mode context"""
    try:
        # Update metadata
        if "session_metadata" in st.session_state:
            st.session_state.session_metadata["last_activity"] = datetime.now().isoformat()
            st.session_state.session_metadata["message_count"] = len(history)
        
        # Save to main context file (for bot.py compatibility)
        with open("chatbot_context.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        # Save mode-specific session backup
        session_file = f"sessions/session_{st.session_state.session_id}_{mode.lower().replace(' ', '_')}.json"
        os.makedirs("sessions", exist_ok=True)
        session_data = {
            "session_id": st.session_state.session_id,
            "session_name": st.session_state.session_name,
            "mode": mode,
            "metadata": st.session_state.get("session_metadata", {}),
            "conversation": history,
            "bot_integration": BOT_AVAILABLE,
            "last_saved": datetime.now().isoformat()
        }
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

def get_mode_specific_response(mode: str, user_message: str, available_tools: List[str]) -> str:
    """Get mode-specific AI response"""
    try:
        mode_contexts = {
            "JIRA Tools": f"""
            You are a JIRA specialist assistant. Focus on project management and issue tracking.
            Available tools: {', '.join(available_tools)}
            
            Help with:
            - JIRA project analysis
            - Issue tracking workflows
            - Project history analysis
            - Development process optimization
            
            USER REQUEST: {user_message}
            """,
            
            "Git Tools": f"""
            You are a Git and version control specialist.
            Available tools: {', '.join(available_tools)}
            
            Help with:
            - Git repository analysis
            - Code conventions and standards
            - Version control best practices
            - Repository management
            
            USER REQUEST: {user_message}
            """,
            
            "Multi-Agent": f"""
            You are a multi-agent coordinator for the professional tool suite.
            Available tools: {', '.join(available_tools)}
            
            Help with:
            - Complex multi-step workflows
            - Cross-platform integrations
            - Comprehensive analysis
            - Advanced automation
            
            USER REQUEST: {user_message}
            """
        }
        
        enhanced_prompt = mode_contexts.get(mode, mode_contexts["Multi-Agent"])
        
        if CHATBOT_AVAILABLE:
            response = question_answering(enhanced_prompt)
        else:
            # Fallback responses for demo mode
            fallback_responses = {
                "JIRA Tools": f"**JIRA Tools Assistant** *(Demo Mode)*\n\nFor JIRA-related query: '{user_message}'\n\n• Use analyze_jira_history tool for project analysis\n• Review issue tracking patterns\n• Analyze development workflows",
                
                "Git Tools": f"**Git Tools Assistant** *(Demo Mode)*\n\nFor Git-related query: '{user_message}'\n\n• Use check_git_conventions tool for repository analysis\n• Review commit patterns\n• Analyze code standards compliance",
                
                "Multi-Agent": f"**Multi-Agent Coordinator** *(Demo Mode)*\n\nFor multi-tool query: '{user_message}'\n\n• Coordinate multiple specialized tools\n• Execute complex workflows\n• Provide comprehensive analysis"
            }
            response = fallback_responses.get(mode, fallback_responses["Multi-Agent"])
        
        return response
        
    except Exception as e:
        return f"I encountered an error processing your {mode.lower()} request: {str(e)}"

def auto_execute_tool_if_applicable(mode: str, user_message: str) -> str:
    """Auto-execute relevant tools based on mode and message content"""
    tool_manager = st.session_state.tool_manager
    
    # Define tool mappings for each mode
    mode_tool_mapping = {
        "JIRA Tools": {
            "analyze_jira_history": ["jira", "project", "issue", "history", "analyze"]
        },
        "Git Tools": {
            "check_git_conventions": ["git", "repository", "commit", "convention", "standard"]
        }
    }
    
    message_lower = user_message.lower()
    
    # Check if any keywords match for auto-execution
    if mode in mode_tool_mapping:
        for tool_name, keywords in mode_tool_mapping[mode].items():
            if any(keyword in message_lower for keyword in keywords):
                try:
                    # Auto-execute the tool with the user message as query
                    result = tool_manager.execute_tool(tool_name, {"query": user_message})
                    
                    if result["success"]:
                        return f"✅ **{tool_name}** executed successfully:\n\n{result['result']}"
                    else:
                        return f"❌ **{tool_name}** execution failed: {result['error']}"
                        
                except Exception as e:
                    return f"❌ Error auto-executing {tool_name}: {str(e)}"
    
    return None

def main():
    """Main application entry point"""
    init_session_state()
    
    # Professional header at the top
    render_professional_header()
    
    # Show system status if dependencies are missing
    if not BOT_AVAILABLE:
        st.markdown(f"""
        <div class="custom-alert alert-warning">
            <strong>Organization AI Engine Functionality Limited:</strong> {BOT_IMPORT_ERROR}<br>
            Please ensure the organization AI engine is configured with proper API access and knowledge base for comprehensive organizational insights.
        </div>
        """, unsafe_allow_html=True)
    elif not CHATBOT_AVAILABLE:
        st.markdown("""
        <div class="custom-alert alert-info">
            <strong>Note:</strong> Using advanced organization AI engine for intelligent responses. 
            For additional organizational features, enhanced capabilities are available with full system setup.
        </div>
        """, unsafe_allow_html=True)
    
    # Main content - Intelligent ChatGPT-like interface
    render_chatgpt_interface()

if __name__ == "__main__":
    main()
