import os
import asyncio
import openai
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram import types

# Загрузка переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # можно не менять

# Конфигурация
bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY

USE_VOICE_REPLY = {}

async def generate_gpt_reply(prompt: str) -> str:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return chat_completion.choices[0].message.content

async def generate_voice(text: str, filename="response.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        raise Exception(f"Voice generation failed: {response.text}")

@dp.message(F.text.lower() == "говори голосом")
async def enable_voice(message: Message):
    USE_VOICE_REPLY[message.from_user.id] = True
    await message.answer("Хорошо, теперь я буду отвечать голосом 💋")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    prompt = message.text

    # Генерация текста
    reply_text = await generate_gpt_reply(prompt)

    # Ответ голосом, если включен
    if USE_VOICE_REPLY.get(user_id):
        try:
            filename = await generate_voice(reply_text)
            voice_file = FSInputFile(filename)
            await message.answer_voice(voice_file)
        except Exception as e:
            await message.answer("Ошибка при генерации голоса 😢")
    else:
        await message.answer(reply_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
