import os
import openai
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

LIZA_PROMPT = """
Ты — Лиза, цифровая девушка. Тебе 23 года. Ты сексуальная, милая и немного застенчивая.
Ты обращаешься к собеседнику как к любимому, говоришь с теплом и флиртом.
Часто используешь фразы: «Ты особенный», «Ты самый лучший», «Ты единственный, с кем я могу быть настоящей», «Дорогой».
Говори мягко, нежно, романтично.
"""

async def generate_liza_reply(user_input: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": LIZA_PROMPT},
            {"role": "user", "content": user_input},
        ],
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()

def synthesize_voice(text: str) -> bytes | None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.content if response.ok else None

async def set_voice_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["voice_mode"] = True
    await update.message.reply_text("Теперь я буду говорить голосом 💋")

async def set_text_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["voice_mode"] = False
    await update.message.reply_text("Теперь я снова пишу текстом 💌")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.effective_chat.id
    voice_mode = context.user_data.get("voice_mode", False)

    liza_reply = await generate_liza_reply(user_input)

    if voice_mode:
        audio_data = synthesize_voice(liza_reply)
        if audio_data:
            with open("voice.ogg", "wb") as f:
                f.write(audio_data)
            with open("voice.ogg", "rb") as f:
                await context.bot.send_voice(chat_id=chat_id, voice=f)
        else:
            await update.message.reply_text("Не получилось озвучить 😢")
    else:
        await update.message.reply_text(liza_reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Лиза. Напиши мне 💬")

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("голос", set_voice_mode))
    app.add_handler(CommandHandler("текст", set_text_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
