import os
import openai
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from tempfile import NamedTemporaryFile

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Голос Евы по умолчанию

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# === Голосовой триггер (русские фразы) ===
VOICE_TRIGGERS = ["скажи это голосом", "ответь голосом", "озвучь", "голосом пожалуйста", "скажи голосом"]

# === Генерация текста с OpenAI ===
async def generate_text(prompt: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты Лиза — сексуальная, нежная, стеснительная девушка, 23 года."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.85
    )
    return response.choices[0].message.content.strip()

# === Синтез речи через ElevenLabs ===
async def synthesize_speech(text: str) -> str | None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.85
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                        f.write(await response.read())
                        return f.name
    except Exception as e:
        print("Ошибка синтеза речи:", e)

    return None  # Ничего не отправляем, если не удалось

# === Обработка входящих сообщений ===
@dp.message(F.text)
async def handle_message(message: types.Message):
    prompt = message.text.lower()

    is_voice = any(trigger in prompt for trigger in VOICE_TRIGGERS)

    text = await generate_text(message.text)

    if is_voice:
        audio_path = await synthesize_speech(text)
        if audio_path:
            voice = FSInputFile(audio_path)
            await message.answer_voice(voice)
    else:
        await message.answer(text)

# === Стартуем бота ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
