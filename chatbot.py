from llm_provider import LLMProvider
import os
import pathlib
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import json

class Chatbot:
    def __init__(self, model="gpt-4"):
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
        self.llm = ChatOpenAI(model=model, openai_api_key=openai_api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Here is the conversation so far: {context}"),
            ("user", "{user_message}")
        ])
        self.chain = self.prompt | self.llm
        self.context = []
        self.context_file = "chatbot_context.json"
        self._load_context()

    def _load_context(self):
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, "r", encoding="utf-8") as f:
                    self.context = json.load(f)
            except json.JSONDecodeError:
                self.context = []
        else:
            self.context = []

    def _save_context(self):
        with open(self.context_file, "w", encoding="utf-8") as f:
            json.dump(self.context, f, indent=2)

    def add_to_context(self, user_message, bot_response):
        self.context.append({"role": "user", "content": user_message})
        # Always extract the string content for the assistant's response
        content = None
        if hasattr(bot_response, "content"):
            content = bot_response.content
        elif isinstance(bot_response, dict) and "content" in bot_response:
            content = bot_response["content"]
        elif isinstance(bot_response, str):
            content = bot_response
        else:
            content = str(bot_response)
        self.context.append({"role": "assistant", "content": content})
        self._save_context()

    def chat(self, user_message):
        # Add user message to context
        self.context.append({"role": "user", "content": user_message})

        # Generate bot response using LangChain's new invoke API
        bot_response = self.chain.invoke({"context": self.context, "user_message": user_message})
        # Always extract the string content for the output
        if hasattr(bot_response, "content"):
            response_text = bot_response.content
        elif isinstance(bot_response, dict) and "content" in bot_response:
            response_text = bot_response["content"]
        elif isinstance(bot_response, str):
            response_text = bot_response
        else:
            response_text = str(bot_response)

        # Add bot response to context
        self.add_to_context(user_message, response_text)

        return response_text

def question_answering(query):
    chatbot = Chatbot()
    return chatbot.chat(query)

if __name__ == "__main__":
    print("Chatbot is ready! Type your messages below. Type 'exit' to quit.")
    chatbot = Chatbot()
    while True:
        user_message = input("You: ")
        if user_message.lower() == "exit":
            print("Goodbye!")
            break
        bot_response = chatbot.chat(user_message)
        print(f"Bot: {bot_response}")
