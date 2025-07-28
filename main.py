import os
import asyncio
import openai
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from elevenlabs import generate, save, set_api_key

# ENV переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

# Конфигурация
openai.api_key = OPENAI_API_KEY
set_api_key(ELEVEN_API_KEY)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Команда /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, я Лиза 💕")

# Обработка сообщений
@dp.message(F.text)
async def handle_message(message: Message):
    prompt = message.text.strip()

    if "говори голосом" in prompt.lower():
        await send_voice_response(message, prompt)
    else:
        response = await chatgpt_response(prompt)
        await message.answer(response)

# Получение текста от GPT
async def chatgpt_response(prompt: str) -> str:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    return chat_completion.choices[0].message.content.strip()

# Генерация и отправка голоса
async def send_voice_response(message: Message, prompt: str):
    text = await chatgpt_response(prompt)

    audio = generate(
        text=text,
        voice=ELEVEN_VOICE_ID,
        model="eleven_monolingual_v1",
        stream=False,
    )

    file_path = "response.mp3"
    save(audio, file_path)

    with open(file_path, "rb") as voice_file:
        await message.answer_voice(voice_file)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
