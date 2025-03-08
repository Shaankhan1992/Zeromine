import logging
import requests
from aiogram import Bot, Dispatcher, executor, types

# Bot का Token (BotFather से प्राप्त करें)
API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# FastAPI backend का URL (उदाहरण: यदि आपके FastAPI server को local machine पर चल रहे हैं, तो "http://127.0.0.1:9000" होगा;
# लेकिन अगर आप इसे public server पर चला रहे हैं या Ngrok का उपयोग कर रहे हैं, तो उसका URL डालें)
API_BASE_URL = 'http://127.0.0.1:9000'

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "Welcome to ZeroMine Bot!\n\n"
        "Available Commands:\n"
        "/register <username> [referral_code] - Register a new user\n"
        "/startmining <username> - Start your daily mining session\n"
        "/mine <username> - Mine coins\n"
        "/balance <username> - Check your coin balance"
    )
    await message.reply(welcome_text)

@dp.message_handler(commands=['register'])
async def handle_register(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("Usage: /register <username> [referral_code]")
            return
        username = parts[1]
        referral_code = parts[2] if len(parts) >= 3 else ""
        url = f"{API_BASE_URL}/register/?username={username}&referral_code={referral_code}"
        response = requests.post(url)
        result = response.json()
        await message.reply(f"Registration Response:\n{result}")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@dp.message_handler(commands=['startmining'])
async def handle_start_mining(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("Usage: /startmining <username>")
            return
        username = parts[1]
        url = f"{API_BASE_URL}/start_mining/?username={username}"
        response = requests.post(url)
        result = response.json()
        await message.reply(f"Start Mining Response:\n{result}")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@dp.message_handler(commands=['mine'])
async def handle_mine(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("Usage: /mine <username>")
            return
        username = parts[1]
        url = f"{API_BASE_URL}/mine/?username={username}"
        response = requests.post(url)
        result = response.json()
        await message.reply(f"Mine Response:\n{result}")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@dp.message_handler(commands=['balance'])
async def handle_balance(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("Usage: /balance <username>")
            return
        username = parts[1]
        url = f"{API_BASE_URL}/balance/?username={username}"
        response = requests.get(url)
        result = response.json()
        await message.reply(f"Balance:\n{result}")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
