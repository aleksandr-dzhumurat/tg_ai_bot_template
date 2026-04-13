# Postgres Persistence & Telegram Messages — Architecture Notes

## How `ai_agent.py` works with memory

Two separate memory systems are used:

1. **`MemorySaver` (checkpointer)** — stores the full conversation state (messages list) per `thread_id`. Thread ID = `user_name`. Every `graph.invoke()` call loads the previous messages from this checkpoint, appends the new human + AI messages, and saves a new checkpoint. This is what gives the bot "memory" across turns.

2. **`InMemoryStore` (store)** — stores extracted user preferences (country, city, craft_option) under the namespace `(user_id, "preferences")`. This is separate from conversation history — it's structured semantic memory.

**Problem**: both are in-memory and die when the process restarts. No Postgres yet.

---

## LangGraph's checkpoint schema (what PostgresSaver creates)

Four tables:
- `checkpoints` — JSONB snapshot of graph state per `thread_id` / `checkpoint_id`
- `checkpoint_blobs` — **pickled Python objects** (including the `messages` list of `HumanMessage`/`AIMessage`) stored as `BYTEA`
- `checkpoint_writes` — intermediate scratchpad
- `checkpoint_migrations` — schema versioning

**Critical constraint**: the chat messages are stored as Python pickle blobs in `checkpoint_blobs` — completely opaque to SQL. You can't JOIN into them or query message content directly.

---

## Can you use your Telegram messages table as LangGraph's store?

**Short answer: No, not directly.** LangGraph's serialization format (pickle) is tightly coupled to its internal types.

---

## Three options for production

### Option A (Recommended) — Separate tables, load history on init

Keep your Telegram messages table for display/history. When invoking the graph, reconstruct the messages from your table and pass them in:

```python
# Load telegram history → inject as initial messages
history = load_from_telegram_table(user_id)  # your query
messages = [HumanMessage(m.text) if m.role == "user" else AIMessage(m.text) for m in history]

graph.invoke({"messages": messages + [HumanMessage(new_input)]}, config=config)
```

No JOIN needed — LangGraph's checkpoint serves as cache, your table is the source of truth.

### Option B — LangGraph PostgresSaver + thin Telegram metadata table

Use `langgraph-checkpoint-postgres` for conversation state. Create a separate `telegram_messages` table with columns like `(thread_id, tg_message_id, chat_id, timestamp)` and link on `thread_id`. LangGraph owns the message content, your table owns Telegram metadata.

```
telegram_messages
  thread_id      → matches LangGraph's thread_id (= user_name / chat_id)
  tg_message_id  → Telegram's message ID
  chat_id
  timestamp
```

### Option C — Custom `BaseCheckpointSaver`

Subclass `BaseCheckpointSaver` and implement `put`, `get_tuple`, `list`, `put_writes` using your own schema. Doable but requires handling serialization yourself.

```python
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple

class MyPostgresSaver(BaseCheckpointSaver):
    def put(self, config, checkpoint, metadata, new_versions): ...
    def get_tuple(self, config) -> CheckpointTuple: ...
    def list(self, config, **kwargs): ...
    def put_writes(self, config, writes, task_id): ...
```

---

## Recommendation

**Option A is cleanest** for this project:
- Telegram table = source of truth for display, analytics, audit
- LangGraph `PostgresSaver` = conversation state cache (opaque but fast)
- They share `thread_id` (= `user_name` or `chat_id`)

No JOIN needed — they serve different purposes.

---

## References

- [Internals of LangGraph Postgres Checkpointer](https://blog.lordpatil.com/posts/langgraph-postgres-checkpointer/)
- [LangGraph v0.2 announcement](https://blog.langchain.com/langgraph-v0-2/)
- [How to implement custom BaseCheckpointSaver](https://forum.langchain.com/t/how-to-implement-custom-basecheckpointsaver/1606)
- [langgraph-checkpoint-postgres PyPI](https://pypi.org/project/langgraph-checkpoint-postgres/)
