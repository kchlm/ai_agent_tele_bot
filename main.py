import os
import time
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.agents.main_agent import main_agent

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Global session service instance to avoid reallocation overhead
session_service = InMemorySessionService()

async def handle_telegram_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        user_id = str(update.message.from_user.id)

        sent_message = await update.message.reply_text("Processing...")

        # Safely attempt session creation; ignore if already initialized
        try:
            await session_service.create_session(app_name="telebot", user_id=user_id, session_id=user_id)
        except Exception:
            pass

        runner = Runner(agent=main_agent, app_name="telebot", session_service=session_service)

        content = types.Content(role='user', parts=[types.Part(text=user_text)])
        events = runner.run_async(user_id=user_id, session_id=user_id, new_message=content)

        accumulated_text = ""
        last_update_time = time.time()
        update_interval = 1.5

        async for event in events:
            if event.content and event.content.parts:
                part_text = event.content.parts[0].text
                if part_text and part_text != accumulated_text:
                    accumulated_text = part_text
                    
                    current_time = time.time()
                    if current_time - last_update_time > update_interval:
                        display_text = accumulated_text[:4000] if len(accumulated_text) > 4000 else accumulated_text
                        await sent_message.edit_text(display_text)
                        last_update_time = current_time

        if accumulated_text:
            display_text = accumulated_text[:4000] if len(accumulated_text) > 4000 else accumulated_text
            if sent_message.text != display_text:
                await sent_message.edit_text(display_text)
        else:
            await sent_message.edit_text("Agent returned an empty response.")

    except Exception as e:
        logging.error(f"Execution failure: {e}", exc_info=True)
        await update.message.reply_text(f"System Error: {str(e)}")

if __name__ == "__main__":
    tele_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not tele_token or not api_key:
        raise ValueError("TELEGRAM_BOT_TOKEN and GEMINI_API_KEY environment variables required in .env file.")

    app = Application.builder().token(tele_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))
    app.run_polling()