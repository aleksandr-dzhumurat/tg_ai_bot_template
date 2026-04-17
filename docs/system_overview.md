# System Overview

## Project Description
A Telegram AI bot that helps users find nearby venues (bars, restaurants, cafés, clubs, etc.) using Google Gemini and the Google Places API. The bot engages users in natural conversation to gather their location and preferences, then recommends a matching venue via a Google Maps link.

## Core Features

### 1. Telegram Bot Integration
- Built using `python-telegram-bot` library
- Supports commands:
  - `/start`: Greets the user
  - `/help`: Displays usage instructions
- Handles text messages and Telegram location shares
- Works in both **private chats** and **group/channel chats**

### 2. AI-Powered Conversation (ReAct Agent)
- Uses Google Gemini (`gemini-2.0-flash` by default, configurable in `src/configs/prod.yml`)
- Implements a ReAct (Reason + Act) agent loop via LangGraph:
  - `agent_node`: calls the LLM with bound tools
  - `ToolNode`: executes tool calls returned by the LLM
  - Loop continues until the LLM produces a final text response
- Collects through natural conversation:
  - City and country of the user
  - Venue type, cuisine, atmosphere, or any other preference
- In group chats, messages are prefixed with `@username` so the LLM can attribute preferences per participant

### 3. LangChain Tools
Two tools are registered with the model via `bind_tools`:

| Tool | Input | Output |
|------|-------|--------|
| `geocode_city` | `"City, Country"` string | `"lat,lng"` coordinates string |
| `find_venue` | `lat_lng`, `query` | HTML link `<a href="...">name</a>` |

Tools are defined in `src/tools.py` using LangChain's `@tool` decorator.

### 4. Message Persistence (SQLite)
- All messages stored in SQLite via `aiosqlite` (path configured in `src/configs/prod.yml`)
- Schema: `chat_id`, `username`, `channel`, `role`, `message_text`, `timestamp`
- `channel` column distinguishes messages from different Telegram groups/channels
- History is loaded per `chat_id` and reconstructed as LangChain message objects on each request
- No LangGraph checkpointer — history is managed entirely via SQLite

### 5. Location Sharing
- Users can share their Telegram location directly
- Bot reverse-geocodes coordinates to city/country via Google Places API
- Synthesizes a text input (`"I'm in City, Country"`) to feed the agent

### 6. Observability (Arize Phoenix + OpenTelemetry)
- Traces sent to Arize Phoenix via OTLP
- `register(auto_instrument=True)` automatically activates `LangChainInstrumentor`
- Captured spans:
  - `CHAIN` — full `graph.invoke()` execution
  - `LLM` — each Gemini model call
  - `TOOL` — each `geocode_city` / `find_venue` execution
- Phoenix runs as a Docker service; endpoint configured via `PHOENIX_COLLECTOR_ENDPOINT`

## Architecture

### Components
| File | Responsibility |
|------|----------------|
| `src/app.py` | Telegram bot handlers, routing private vs group messages |
| `src/ai_agent.py` | LangGraph ReAct agent, `dialog_router()` entry point |
| `src/tools.py` | LangChain `@tool` definitions |
| `src/prompts.py` | System prompt for the agent |
| `src/db.py` | SQLite message storage and retrieval |
| `src/config.py` | YAML config loader (`MODEL_NAME`, `BOT_USERNAME`, `DB_PATH`) |
| `src/google_api.py` | Google Places API integration (geocoding, reverse geocoding, venue search) |
| `src/configs/prod.yml` | Production configuration (DB path, bot username, model name) |
| `scripts/chat.py` | Console testing interface |
| `scripts/db_history.py` | Print message history from SQLite |

### Key Dependencies
- `python-telegram-bot`: Telegram API
- `langchain-google-genai`: Gemini model via LangChain
- `langchain`, `langchain-core`: LLM framework and tools
- `langgraph<1.0.0`: ReAct graph orchestration
- `aiosqlite`: Async SQLite for message persistence
- `openinference-instrumentation-langchain`: LangChain auto-instrumentation for Phoenix
- `arize-phoenix-otel`: Phoenix OTLP registration

### Environment Variables
| Variable | Purpose |
|----------|---------|
| `TG_BOT_TOKEN` | Telegram bot token |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GOOGLE_API_KEY` | Google Places API key |
| `PHOENIX_COLLECTOR_ENDPOINT` | Phoenix OTLP endpoint (default: `http://phoenix:6006`) |
| `ENV` | Config environment (`prod`) |
| `DATA_DIR` | SQLite data directory inside container |

### Deployment
- Docker-based: `Dockerfile` for the bot, `docker-compose.yml` for Phoenix
- `make build` — builds the bot image
- `make run` — starts Phoenix + bot container (joined to Phoenix network)
- `make chat` — starts Phoenix + interactive console session
- `make phoenix` — starts only the Phoenix observability service

## Usage Flow
1. User sends a message or shares location
2. Bot loads chat history from SQLite and reconstructs message context
3. LangGraph agent runs:
   - LLM decides whether to ask a follow-up question or call tools
   - If tools needed: `geocode_city` → `find_venue` → LLM formats final answer
4. Bot replies with text or HTML (venue link)
5. Both user message and bot reply are saved to SQLite
6. Full trace (LLM calls + tool calls) sent to Phoenix
