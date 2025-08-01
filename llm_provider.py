import os
import json
import pathlib

class LLMProvider:
    def __init__(self, provider="openai"):
        self.provider = provider
        self.api_key = self._get_api_key()

        if provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        elif provider == "mistral":
            from mistralai.client import MistralClient
            self.client = MistralClient(api_key=self.api_key)
        else:
            raise ValueError("Unsupported provider")

    def _get_api_key(self):
        env_key = os.environ.get("OPENAI_API_KEY") if self.provider == "openai" else os.environ.get("MISTRAL_API_KEY")
        if env_key:
            return env_key
        root = pathlib.Path(__file__).parent
        settings_path = root / "settings.json"
        if settings_path.exists():
            with open(settings_path, "r", encoding="utf-8") as s:
                cfg = json.load(s)
                key_name = "OPENAI_API_KEY" if self.provider == "openai" else "MISTRAL_API_KEY"
                return cfg.get(key_name)
        raise RuntimeError(f"{self.provider} API key not found.")

    def chat_completion(self, messages, model="gpt-4o", temperature=0.2, max_tokens=2000, functions=None, function_call=None):
        if self.provider == "openai":
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if functions is not None:
                kwargs["functions"] = functions
            if function_call is not None:
                kwargs["function_call"] = function_call
            response = self.client.chat.completions.create(**kwargs)
            # If function_call is used, return the full response for agentic workflows
            if function_call:
                return response
            # Otherwise, return content and token info for single-step executor
            content = response.choices[0].message.content.strip()
            usage = getattr(response, "usage", None)
            if usage:
                token_info = {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            else:
                token_info = None
            return content, token_info
        elif self.provider == "mistral":
            # Example for mistral, adjust as needed
            response = self.client.chat(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content.strip()
            # Mistral API may not provide usage info; adjust if available
            return content, None