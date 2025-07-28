import os
import asyncio
import logging
import requests
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Токены и ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

# Инициализация клиентов
bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Генерация речи через ElevenLabs
def generate_voice(text: str, voice_id: str = ELEVENLABS_VOICE_ID) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        filepath = "voice_response.mp3"
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath
    else:
        raise Exception("Failed to generate voice")

# Генерация ответа через ChatGPT
async def generate_reply(prompt: str) -> str:
    chat_completion = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    return chat_completion.choices[0].message.content.strip()

# Обработчик текстовых сообщений
@dp.message(F.text)
async def handle_message(message: types.Message):
    user_input = message.text.strip()

    is_voice = user_input.lower().startswith("голос:")
    prompt = user_input[6:].strip() if is_voice else user_input

    try:
        reply = await generate_reply(prompt)

        if is_voice:
            audio_file_path = generate_voice(reply)
            voice = FSInputFile(audio_file_path)
            await message.answer_voice(voice)
        else:
            await message.answer(reply)

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("⚠️ Упс, что-то пошло не так...")

# Старт бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
