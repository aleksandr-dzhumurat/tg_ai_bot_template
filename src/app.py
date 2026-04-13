import logging
import os

from telegram import __version__ as TG_VER

from .ai_agent import dialog_router
from .db import init_db
from .google_api import place_recommender

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ['TG_BOT_TOKEN']

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Use /help for help",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    response = [
        "Ask me to find nearest craft beer point: tell where are you"
    ]
    for i in response:
        await update.message.reply_text(i)


def _get_chat_context(update: Update) -> tuple[str | None, str | None]:
    """Return (chat_id, channel) for group/supergroup/channel chats, (None, None) for private."""
    chat = update.effective_chat
    if chat and chat.type in ("group", "supergroup", "channel"):
        return str(chat.id), chat.title or chat.username
    return None, None


def _get_user(update: Update) -> dict:
    """Return user dict, handling anonymous/channel senders where effective_user is None."""
    user_tg = update.effective_user
    if user_tg is None:
        chat = update.effective_chat
        return {'user_id': None, 'user_name': getattr(chat, 'username', None) or getattr(chat, 'title', None)}
    return {'user_id': user_tg.id, 'user_name': user_tg.username}


async def bot_dialog(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update)
    chat_id, channel = _get_chat_context(update)
    logger.info("bot_dialog: user=%s chat_id=%s channel=%s", user['user_name'], chat_id or "private", channel)
    bot_response = await dialog_router(update.message.text, user, chat_id=chat_id, channel=channel)
    if bot_response['is_html']:
        await update.message.reply_html(bot_response['answer'])
    else:
        await update.message.reply_text(bot_response['answer'])


async def bot_location(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update)
    chat_id, channel = _get_chat_context(update)
    loc = update.message.location
    logger.info("User %s sent location: lat=%s lng=%s", user['user_name'], loc.latitude, loc.longitude)
    place = place_recommender.reverse_geocode(loc.latitude, loc.longitude)
    if place is None:
        logger.warning("Reverse geocode failed for lat=%s lng=%s", loc.latitude, loc.longitude)
        await update.message.reply_text("Sorry, I couldn't determine your location. Please type your city and country.")
        return
    logger.info("Resolved location: %s, %s", place['city'], place['country'])
    synthetic_input = f"I'm in {place['city']}, {place['country']}"
    raw_input = f"📍 {loc.latitude}, {loc.longitude}"
    bot_response = await dialog_router(synthetic_input, user, raw_input=raw_input, chat_id=chat_id, channel=channel)
    if bot_response['is_html']:
        await update.message.reply_html(bot_response['answer'])
    else:
        await update.message.reply_text(bot_response['answer'])


async def post_init(_application: Application) -> None:
    await init_db()


def main() -> None:
    """Start the bot."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.LOCATION, bot_location))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_dialog))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()