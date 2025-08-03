"""
Multi-agent workflow using OpenAI Agentic SDK for autonomous tool selection and chaining.
Parses user prompt, selects tools from tools.json, and executes multi-step workflows.
Enhanced with approval handling, context persistence, and intelligent data passing.
"""
import json
import pathlib
import importlib
import sys
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

from langchain_openai import OpenAI
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from llm_provider import LLMProvider
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

sys.path.append(str(pathlib.Path(__file__).parent))
TOOLS_PATH = pathlib.Path(__file__).parent / "tools.json"
CONTEXT_PATH = pathlib.Path(__file__).parent / "output" / "workflow_context.json"

# Load tool definitions
with open(TOOLS_PATH, "r", encoding="utf-8") as f:
    tools_config = json.load(f)

# Build OpenAI function definitions from tools.json
openai_functions = []
for tool in tools_config:
    openai_functions.append({
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["args_schema"]
    })

# Initialize tool_map with tools from tools.json
tool_map = {}
for tool in tools_config:
    module_path = tool.get("module")
    func_name = tool["name"]
    
    # Handle modules in main folder vs tools folder
    if module_path.startswith("tools."):
        import_path = module_path
    else:
        # For modules in main folder like chatbot
        import_path = module_path
    
    mod = importlib.import_module(import_path)
    tool_map[func_name] = getattr(mod, func_name)

# Initialize tools
from langchain.agents import Tool, AgentExecutor
from tools.development.jira_tools import jira_ticket_summarizer

tools = [
    Tool(
        name="jira_ticket_summarizer",
        func=jira_ticket_summarizer,
        description="Fetch JIRA tickets, summarize them into a PRD, and save the context in JSON format."
    )
]

# Initialize memory
memory = ConversationBufferMemory()

# Initialize LLM
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    # Try to read from settings.json
    settings_path = pathlib.Path(__file__).parent / "settings.json"
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
                openai_api_key = settings.get("OPENAI_API_KEY")
            except Exception:
                openai_api_key = None
    if not openai_api_key:
        openai_api_key = input("Enter your OpenAI API key: ").strip()
llm = OpenAI(model="gpt-4", openai_api_key=openai_api_key)

# Create a prompt for the agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful multi-agent assistant. Use tools as needed to solve the user's request. {agent_scratchpad}"),
    ("user", "{input}")
])
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)

# Helper: Save workflow context
def save_context(context):
    CONTEXT_PATH.parent.mkdir(exist_ok=True)
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

# Helper: Load workflow context
def load_context():
    if CONTEXT_PATH.exists():
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"execution_history": [], "data_context": {}}

# Helper: Dynamically import and call a tool
def call_tool(tool_name, args):
    tool = next((t for t in tools_config if t["name"] == tool_name), None)
    if not tool:
        raise ValueError(f"Tool {tool_name} not found in tools.json.")
    module_path = tool.get("module")
    if not module_path:
        raise ValueError(f"Tool {tool_name} missing 'module' in tools.json.")
    func_name = module_path.split(".")[-1]
    
    # Handle modules in main folder vs tools folder
    if module_path.startswith("tools."):
        import_path = module_path
    else:
        # For modules in main folder like chatbot
        import_path = module_path
    
    mod = importlib.import_module(import_path)
    func = getattr(mod, func_name)
    return func(**args)

# Enhanced multi-agent execution with intent analysis and fallback
class MultiAgent:
    def __init__(self, provider="openai", functions=None):
        self.llm_provider = LLMProvider(provider=provider)
        self.functions = functions or {}

    def run(self, user_prompt):
        print(f"[AGENT LOG] Received user prompt: {user_prompt}")
        print(f"[AGENT LOG] tool_map keys: {list(tool_map.keys())}")
        try:
            JIRA_PARAM = os.getenv("JIRA_PARAM")
            # Check for jira_ticket_summarizer
            if "jira_ticket_summarizer" in tool_map:
                tool_func = tool_map["jira_ticket_summarizer"]
                result = tool_func.invoke({
                    "domain": "https://talentica-mcp-hackathon.atlassian.net",
                    "user": "vinay.dahat@talentica.com",
                    "token": JIRA_PARAM,
                    "query": "created >=-20d"
                })
                print(f"[AGENT LOG] Tool result: {result}")
            else:
                print("[AGENT LOG] Tool 'jira_ticket_summarizer' not found in tool_map.")

            # Check for fetch_remote_git_history
            if "fetch_remote_git_history" in tool_map:
                tool_func = tool_map["fetch_remote_git_history"]
                # Call directly as a normal function
                result = tool_func.invoke({"repo_url": "https://github.com/atulpandey1695/MCP-hackathon.git"})
                print(f"[AGENT LOG] Tool result: {result}")
            else:
                print("[AGENT LOG] Tool 'fetch_remote_git_history' not found in tool_map.")

            # Check for train_agent_on_github_repo
            if "train_agent_on_github_repo" in tool_map:
                tool_func = tool_map["train_agent_on_github_repo"]
                result = tool_func(repo_url="https://github.com/atulpandey1695/MCP-hackathon.git")
                print(f"[AGENT LOG] Tool result: {result}")
            else:
                print("[AGENT LOG] Tool 'train_agent_on_github_repo' not found in tool_map.")

            # for tool in tools:
            #     try:
            #         result = tool.func.invoke(user_prompt)
            #         print(f"[AGENT LOG] Tool '{tool.name}' result: {result}")
            #     except Exception as tool_error:
            #         print(f"[AGENT LOG] Error executing '{tool.name}': {tool_error}")
        except Exception as e:
            print(f"[AGENT LOG] Error executing question_answering: {e}")
            # If tool fails, store as context
            context = load_context()
            context["data_context"][user_prompt] = user_prompt
            save_context(context)

# Example usage
def run_agent(user_input):
    return agent_executor.run(user_input)

if __name__ == "__main__":
    # Setup LLMProvider with a valid provider
    llm = LLMProvider(provider="openai")
    agent = MultiAgent(provider="openai", functions=openai_functions)
    print("Enter your prompt for the multi-agent system. Type 'exit' or 'quit' to leave.")
    while True:
        user_prompt = input("User Input: ").strip()
        if user_prompt.lower() in ("exit", "quit"):
            print("Exiting multi-agent. Goodbye!")
            break
        if not user_prompt:
            continue
        agent.run(user_prompt)
