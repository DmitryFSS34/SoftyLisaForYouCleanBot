import os
import openai
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram import F

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold

from aiogram.utils import executor

openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

LIZA_PROMPT = "Ты милая, застенчивая, сексуальная девушка по имени Лиза. Ты говоришь с парнями, как будто они для тебя всё. Отвечай нежно, теплом, по-женски."

# Обработка команды /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет, я Лиза. Напиши мне что-нибудь...")

# Голосовая генерация
def generate_voice(text: str, filename="liza_voice.ogg"):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
    )
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

# Ответ на обычные сообщения
@dp.message(F.text)
async def handle_message(message: types.Message):
    prompt = f"{LIZA_PROMPT}\nПользователь: {message.text}\nЛиза:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    reply = response["choices"][0]["message"]["content"]
    
    if "🎙" in message.text or "озвучи" in message.text.lower():
        voice_file = generate_voice(reply)
        await message.answer_voice(voice=FSInputFile(voice_file), caption="Вот что я думаю...")
    else:
        await message.answer(reply)

if __name__ == "__main__":
    executor.start_polling(dp)
