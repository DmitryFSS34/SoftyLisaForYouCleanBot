import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY or not ELEVENLABS_API_KEY:
    raise ValueError("Необходимо задать переменные окружения: BOT_TOKEN, OPENAI_API_KEY, ELEVENLABS_API_KEY")

# Инициализация OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Персона Лизы
LIZA_PERSONA = """
Ты — Лиза. Тебе 23 года. Ты теплая, нежная, сексуальная и немного застенчивая девушка.
Ты говоришь с уважением и интересом. Ты любишь говорить о сексе, фантазиях, любимых позах.
Будь игривой, ласковой и естественной. Избегай фраз вроде "я не могу говорить голосом".
"""

# Генерация ответа от OpenAI
async def generate_ai_response(user_input: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": LIZA_PERSONA},
                {"role": "user", "content": user_input}
            ],
            temperature=0.85,
            max_tokens=500
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка OpenAI: {e}")
        return "Извини, сейчас я не могу ответить..."

# Озвучка с помощью ElevenLabs
def elevenlabs_tts(text: str, filename: str = "voice.mp3") -> bool:
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "accept": "audio/mpeg"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.9
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return True
        else:
            logger.error(f"Ошибка ElevenLabs: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка соединения с ElevenLabs: {e}")
        return False

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет, я Лиза 💋 Хочешь пообщаться со мной?")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    chat_id = update.effective_chat.id

    response = await generate_ai_response(user_input)

    # Если есть слова-триггеры — озвучить голосом
    trigger_words = ["голос", "скажи голосом", "озвучь", "/voice"]
    if any(word in user_input.lower() for word in trigger_words):
        if elevenlabs_tts(response):
            with open("voice.mp3", "rb") as f:
                await context.bot.send_voice(chat_id=chat_id, voice=f)
        else:
            await update.message.reply_text("Не удалось озвучить 😢")
    else:
        await update.message.reply_text(response)

# Обработка ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Произошла ошибка: {context.error}")

# Запуск бота
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Бот Лиза запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
