# AI Email Agent

A simple AI agent built with Python, LangGraph, and Ollama that reads your recent Gmail inbox and answers questions about it in a chat. Everything runs locally, so your emails never go to a cloud model.

Built to learn how LLM tool-calling and agent loops work under the hood.

## What it does

- Fetches your most recent emails (sender and subject) from Gmail over IMAP
- Lets you chat with a local LLM, for example "Summarize my latest emails"
- Remembers the conversation, so follow-ups like "Which one looks most important?" work

## How it works

1. **Tool**: `fetch_recent_emails` connects to Gmail with `IMAPClient` and returns the sender and subject of the latest emails as text.
2. **Model**: `ChatOllama` runs a local model and is bound to the tool, so it can decide when to call it.
3. **Graph**: LangGraph runs the loop automatically. The model is asked, and if it requests a tool, the tool runs and its result goes back to the model. This repeats until the model gives a final answer.

5. **Memory**: A `MemorySaver` checkpointer stores the conversation per thread ID, so the agent keeps context between questions.

```
User -> agent (model) -> needs a tool? -> yes -> tools -> back to agent
                                        -> no  -> final answer
```

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Create a `.env` file (see `.env.example`):
   ```
   IMAP_USER=your_email@gmail.com
   IMAP_PASS=your_app_password
   ```
   > Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your real password.
3. Make sure [Ollama](https://ollama.com) is running with a model pulled:
   ```bash
   ollama pull llama3.2
   ```
4. Run the agent:
   ```bash
   py main.py
   ```

Type your questions at the `You:` prompt, and type `quit` or `exit` to stop.

