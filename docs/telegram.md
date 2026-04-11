# Telegram Bot Setup

## Create a Bot and Get a Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Enter a display name (e.g. `Beer Finder Bot`)
4. Enter a username — must end in `bot` (e.g. `beer_finder_bot`)
5. BotFather replies with your token:
   ```
   Use this token to access the HTTP API:
   1234567890:AAF_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
6. Copy the token into your `.env`:
   ```
   TG_BOT_TOKEN=1234567890:AAF_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

> Keep the token secret — anyone with it can control your bot.

---

## Private vs Group Chats

A bot works in both modes simultaneously.

**Private (DM):** users write directly to the bot — works out of the box.

**Group chat:** invite the bot to the group. By default bots only see `/` commands.
To read **all** messages in a group, disable privacy mode in BotFather:

```
/mybots → choose bot → Bot Settings → Group Privacy → Turn off
```

### Handling both in code

```python
@dp.message()
async def handle_message(message: Message):
    if message.chat.type == "private":
        # personal message
    elif message.chat.type in ["group", "supergroup"]:
        # group message
```

The `chat.type` field tells you where the message came from — one bot, one codebase handles both.
