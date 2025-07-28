import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from openai import AsyncOpenAI
from elevenlabs import generate, save, set_api_key
from tempfile import NamedTemporaryFile

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # по умолчанию Eva

# Инициализация
bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
set_api_key(ELEVENLABS_API_KEY)

# Флаг: озвучивать или нет
user_voice_enabled = {}

# Команда запуска
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет, я Лиза! ❤️ Напиши что-нибудь.")

# Команда включения голоса
@dp.message(lambda msg: msg.text.lower() == "озвучивай")
async def enable_voice(message: types.Message):
    user_voice_enabled[message.from_user.id] = True
    await message.answer("Хорошо, теперь я буду отвечать голосом. 💋")

# Команда отключения голоса
@dp.message(lambda msg: msg.text.lower() == "не озвучивай")
async def disable_voice(message: types.Message):
    user_voice_enabled[message.from_user.id] = False
    await message.answer("Хорошо, теперь я буду писать только текстом. ✍️")

# Обработка всех сообщений
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    prompt = message.text.strip()

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )
        reply = response.choices[0].message.content.strip()

        if user_voice_enabled.get(user_id):
            audio = generate(
                text=reply,
                voice=ELEVENLABS_VOICE_ID,
                model="eleven_monolingual_v1",
                stream=False
            )
            with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                save(audio, f.name)
                voice = FSInputFile(f.name)
                await message.answer_voice(voice)
        else:
            await message.answer(reply)

    except Exception as e:
        logging.exception("Ошибка при обработке сообщения:")
        await message.answer("Что-то пошло не так. Попробуй ещё раз.")

# Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
