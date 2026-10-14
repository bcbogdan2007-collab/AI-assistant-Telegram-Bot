# 🤖 Telegram Bot with Google Gemini

A demo project with a focused set of features: integration of the **Telegram Bot API** (aiogram 3) with **Google Gemini** artificial intelligence.

The user sends a message, the bot forwards it to Gemini, and returns the response.

## Features

- answers questions and explains complex topics;
- consultations, recommendations, and project ideas;
- help with learning, text generation, and planning;
- “typing…” indicator while a response is being generated;
- automatic splitting of long responses (Telegram limit: 4,096 characters);
- API error handling with clear messages for users.

## Privacy

- conversation history is **not stored**: each message is processed separately;
- no **database or files** are used to store user data;
- message text is **not logged** (logs contain only service information);
- no user data is saved after a response is sent.

> Important: requests are sent to the Google Gemini API and processed according to Google's policies.

## Tech Stack

- Python 3.11+
- [aiogram 3.x](https://docs.aiogram.dev/)
- [Google Gen AI SDK (`google-genai`)](https://ai.google.dev/gemini-api/docs)
- python-dotenv, logging

## Project Structure

```text
project/
├── main.py            # bot code
├── requirements.txt   # dependencies
├── .env.example       # example environment variables
└── README.md
```

## Installation and Usage

1. **Get a Telegram bot token**: message [@BotFather](https://t.me/BotFather) and use the `/newbot` command.
2. **Get a Gemini API key** from [Google AI Studio](https://aistudio.google.com/apikey).
3. **Install the dependencies** (using a virtual environment is recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** from the example and enter your keys:

   ```bash
   cp .env.example .env            # Windows: copy .env.example .env
   ```

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Start the bot**:

   ```bash
   python main.py
   ```

6. Open the bot in Telegram, send `/start`, and ask any question.

## Configuration

| Setting | Where |
|---|---|
| Gemini model | `GEMINI_MODEL` variable in `.env` (default: `gemini-flash-latest`) |
| Response behavior and style | `SYSTEM_PROMPT` constant in `main.py` |
| Response creativity | `temperature` parameter in `generate_response()` |
| Greeting message | `WELCOME_TEXT` constant in `main.py` |

Current list of models: <https://ai.google.dev/gemini-api/docs/models>

## Troubleshooting

- **“TELEGRAM_BOT_TOKEN and/or GEMINI_API_KEY not set”** — make sure the `.env` file is located next to `main.py`.
- **Error 429** — the Gemini API free-tier limits have been exceeded. Wait or check your quotas in AI Studio.
- **Error 404 / model not found** — specify a current model name in `GEMINI_MODEL`.
- **The bot does not respond** — make sure another instance of the bot is not running with the same token.

## Security

Do not publish the `.env` file or commit it to your repository. Add `.env` to `.gitignore`.

---

💼 To order a custom bot for any task with full support, contact me on Telegram: @dark_baga7
