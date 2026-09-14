# AI Email Agent

A simple AI agent built with Python, LangChain, and Ollama that can read and summarize your recent Gmail inbox using natural language.

## What it does

- Connects to Gmail via IMAP to fetch recent emails (sender + subject)
- Uses a local LLM (via Ollama) to understand requests like "list me my latest emails"
- The model decides when to call the email-fetching tool, retrieves the real data, then responds in plain, conversational language

## How it works

1. **Tool** — `fetch_recent_emails` connects to Gmail via `IMAPClient`, fetches the most recent messages, and returns their sender/subject as text.
2. **Model** — `ChatOllama` (running locally via Ollama) is bound to the tool with `.bind_tools()`, so it can request the tool when relevant.
3. **Loop** — When the model asks to use the tool, the code runs it manually, then feeds the result back to the model as a `ToolMessage` so it can generate a natural-language summary.

## Setup

1. Install dependencies:
```bash
   uv sync
```
2. Create a `.env` file (see `.env.example`) with your Gmail credentials:

IMAP_USER=your_email@gmail.com
IMAP_PASS=your_app_password

   > Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your real password.
3. Make sure [Ollama](https://ollama.com) is running locally with a model pulled (e.g. `llama3.2`).
4. Run the agent:
```bash
   py main.py
```

## Status

Currently a manual proof-of-concept for the model → tool → model loop. Next step: automate this flow using LangGraph.