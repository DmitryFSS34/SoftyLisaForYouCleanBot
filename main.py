import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils.markdown import hbold
from openai import OpenAI
import aiohttp

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def generate_voice(text: str, filename: str = "voice.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 0.75
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Failed to generate voice: {await response.text()}")
            with open(filename, "wb") as f:
                f.write(await response.read())

@dp.message()
async def handle_message(message: types.Message):
    prompt = message.text.strip()
    is_voice = "скажи голосом" in prompt.lower()

    prompt_cleaned = prompt.lower().replace("скажи голосом", "").strip()
    if not prompt_cleaned:
        prompt_cleaned = "Скажи что-нибудь приятное."

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_cleaned}],
            temperature=0.9
        )
        reply = completion.choices[0].message.content.strip()

        if is_voice:
            await generate_voice(reply)
            voice = FSInputFile("voice.mp3")
            await message.answer_voice(voice)
        else:
            await message.answer(reply)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    print("🚀 Бот запущен и работает.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
