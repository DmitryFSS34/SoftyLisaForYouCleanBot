import os
import asyncio
import openai
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils.markdown import hquote

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY

USE_VOICE = set()  # ID пользователей, кто включил голосовой режим

async def send_voice(chat_id: int, text: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.7
        }
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        with open("response.mp3", "wb") as f:
            f.write(response.content)
        voice = FSInputFile("response.mp3")
        await bot.send_voice(chat_id, voice)
    else:
        await bot.send_message(chat_id, "Ошибка озвучивания.")

@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет, я Лиза. Напиши мне что-нибудь ❤️")

@dp.message(commands=["голос"])
async def enable_voice(message: types.Message):
    USE_VOICE.add(message.from_user.id)
    await message.answer("Хорошо, теперь я буду отвечать голосом 🎙️")

@dp.message(commands=["текст"])
async def disable_voice(message: types.Message):
    USE_VOICE.discard(message.from_user.id)
    await message.answer("Хорошо, теперь я буду писать только текстом ✍️")

@dp.message()
async def handle_message(message: types.Message):
    prompt = message.text.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        reply = response.choices[0].message["content"].strip()

        if message.from_user.id in USE_VOICE:
            await send_voice(message.chat.id, reply)
        else:
            await message.answer(hquote(reply))
    except Exception as e:
        await message.answer("Произошла ошибка. Попробуй позже.")
        print(e)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
