import os
import openai
import aiohttp
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ✅ Инициализация
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Можно оставить дефолт

openai.api_key = OPENAI_API_KEY

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# 🔊 Распознавание ключевой фразы для озвучки
def needs_voice(message: str) -> bool:
    message = message.lower()
    return any(
        phrase in message
        for phrase in ["скажи это голосом", "ответь голосом", "голосом", "озвучи", "озвучь"]
    )


# 🎤 Озвучка через ElevenLabs
async def text_to_speech(text: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                return await resp.read()
            else:
                raise Exception(f"ElevenLabs error {resp.status}: {await resp.text()}")


# 🤖 Обработка входящих сообщений
@dp.message(F.text)
async def handle_message(message: Message):
    user_text = message.text.strip()

    # 🔍 Проверяем, хочет ли пользователь голос
    use_voice = needs_voice(user_text)

    # 💬 Получаем ответ от ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты — милая и застенчивая девушка по имени Лиза. Отвечай тепло и немного флиртуя, по-русски."},
            {"role": "user", "content": user_text}
        ],
        temperature=0.9,
    )
    reply_text = response["choices"][0]["message"]["content"]

    if use_voice:
        try:
            voice_data = await text_to_speech(reply_text)
            await message.answer_voice(voice_data)
        except Exception as e:
            await message.answer("Произошла ошибка с озвучкой 😢")
    else:
        await message.answer(reply_text)


# 🚀 Старт
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
