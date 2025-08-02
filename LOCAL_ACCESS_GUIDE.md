# Local Access Guide

## API Keys and Sensitive Files

- Your `settings.json` file contains sensitive information such as your OpenAI API key.
- This file is now included in `.gitignore` and will **not** be tracked by git. It will always remain in your local workspace.
- Do **not** share or commit `settings.json` to any public or shared repository.

## How to Use

1. **Keep your `settings.json` file in the project root.**
2. **Update your API key or model as needed in `settings.json`.**
3. **If you clone this repo elsewhere, you must manually create your own `settings.json` with your API key.**

### Example `settings.json`
```json
{
  "OPENAI_API_KEY": "sk-...",
  "MODEL": "gpt-4o-mini"
}
```

## Security Reminder
- Never share your API keys publicly.
- If you accidentally commit `settings.json`, remove it from git history and rotate your API key.

---

For any issues, contact your project admin.
