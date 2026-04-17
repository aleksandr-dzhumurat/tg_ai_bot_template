# Kick Start Guide

## 1. Fork & Setup

1. Fork [tg_ai_bot_template](https://github.com/aleksandr-dzhumurat/tg_ai_bot_template) on GitHub.
2. Follow the [README.md](../README.md) setup instructions — covers environment variables, Docker, and running the bot locally.
3. Copy [env.template](../env.template) to `.env` and fill in the required keys:
   - **Telegram Bot Token** — generated via BotFather. See [docs/telegram.md](telegram.md).
   - **Gemini API Key** — get one at [Google AI Studio](https://aistudio.google.com/api-key).
   - **Google API Key** — for Maps/Places integration used in [src/google_api.py](../src/google_api.py).

## 2. Run the Bot

```bash
make build   # build Docker image
make run     # start the Telegram bot
make chat    # test the chat interface locally (scripts/chat.py)
make history # inspect stored conversation history (scripts/db_history.py)
```

See [Makefile](../Makefile), [Dockerfile](../Dockerfile), and [docker-compose.yml](../docker-compose.yml).

## 3. Choose Your LLM

The bot defaults to Gemini via `ChatGoogleGenerativeAI`. The model is initialized in [src/ai_agent.py#L21](../src/ai_agent.py#L21):

```python
model = ChatGoogleGenerativeAI(model=MODEL_NAME, ...)
```

To use a different LLM (OpenAI, Anthropic, Mistral, etc.), replace this line with the corresponding LangChain chat model. Model name is configured in [src/configs/prod.yml](../src/configs/prod.yml) and loaded via [src/config.py](../src/config.py).

## 4. Adjust the System Prompt

Edit [src/prompts.py](../src/prompts.py) to change the bot's persona, conversation flow, or group-chat aggregation logic. The current prompt instructs the bot to collect location and venue preferences, then call tools to find a match.

## 5. Extend the Tools

The active tools are registered in [src/ai_agent.py#L20](../src/ai_agent.py#L20) and implemented in [src/tools.py](../src/tools.py):

| Tool | Description |
|---|---|
| `geocode_city` | Converts a city name to lat/lng via Google Maps |
| `find_venue` | Finds a venue via Google Places and returns an HTML link |

### Ideas for new tools

- **Event retrieval** — build a RAG tool over this [JSONL events database](https://drive.google.com/file/d/159Cj_XzRrVdtrCK83TvsSMb6J12scYWf/view?usp=sharing).
- **Web search** — integrate [Tavily](https://tavily.com), [Perplexity](https://www.perplexity.ai), or [Google Custom Search](https://programmablesearchengine.google.com/).

Add new tools to [src/tools.py](../src/tools.py), then register them in the `tools` list in [src/ai_agent.py](../src/ai_agent.py).

## 6. Group Recommender Background

The bot aggregates preferences from multiple users in a group chat. For the theory behind group recommendation, see the [group recommender papers](https://github.com/aleksandr-dzhumurat/ai_product_engineer/blob/main/slides/ml_projects/group_recommender_papers.md).

---

For architecture details see [docs/system_overview.md](system_overview.md).
