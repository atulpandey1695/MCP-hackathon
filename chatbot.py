from llm_provider import LLMProvider
import os
import json

class Chatbot:
    def __init__(self, provider="openai", model="gpt-4"):
        self.llm_provider = LLMProvider(provider=provider)
        self.model = model
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
        self.context.append({"role": "assistant", "content": bot_response})
        self._save_context()

    def chat(self, user_message):
        # Add user message to context
        self.context.append({"role": "user", "content": user_message})

        # Call LLMProvider for chat completion
        bot_response, _ = self.llm_provider.chat_completion(
            messages=self.context,
            model=self.model
        )

        # Add bot response to context
        self.add_to_context(user_message, bot_response)

        return bot_response

def question_answering(query):
    chatbot = Chatbot(provider="openai")
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
