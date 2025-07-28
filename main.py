import os
from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update, context):
    await update.message.reply_text("Бот жив!")

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
