import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# ВСТАВЬ СЮДА ТОКЕН ОТ @BotFather
BOT_TOKEN = "8844907899:AAGGqIQscoqCFCYNt9F-ESOGaeyHOoo4YdI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временная база данных в памяти (словарь: user_id -> {'name': str, 'karma': int})
karma_db = {}

TITLES = [
    "Красавчик дня ✨",
    "Главный душнила 🤓",
    "Король рофлов 🤡",
    "Мастер прокрастинации 🛌",
    "Душа компании 🥳",
    "Скрытый гений 🧠"
]

# --- КОМАНДЫ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Привет всем!** Я развлекательный бот для этой группы.\n\n"
        "**Что я умею:**\n"
        "• Ответьте `+` или `спасибо` на сообщение, чтобы поднять карму пользователю.\n"
        "• `/top` — рейтинг репутации в чате.\n"
        "• `/who` — узнать, кто сегодня главный в чате.\n"
        "• `/dice` или `/darts` — бросить кубик или дротик.\n",
        parse_mode=ParseMode.MARKDOWN
    )

# Команда: Выбор «Героя дня»
@dp.message(Command("who"))
async def cmd_who(message: types.Message):
    title = random.choice(TITLES)
    target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.answer(f"🎉 Сегодня **{target_user.first_name}** получает титул: **{title}**!", parse_mode=ParseMode.MARKDOWN)

# Команда: Посмотреть ТОП репутации
@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    if not karma_db:
        await message.answer("📊 В этом чате пока никто не earned карму. Отвечайте `+` на сообщения друг друга!")
        return

    sorted_karma = sorted(karma_db.values(), key=lambda x: x['karma'], reverse=True)[:10]
    
    text = "🏆 **Топ участников по репутации:**\n\n"
    for idx, user in enumerate(sorted_karma, 1):
        text += f"{idx}. **{user['name']}** — {user['karma']} ⭐\n"
        
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

# Команды: Игры (Кубик и Дартс)
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")

@dp.message(Command("darts"))
async def cmd_darts(message: types.Message):
    await message.answer_dice(emoji="🎯")

# --- СИСТЕМА РЕПУТАЦИИ (Плюсики в карму) ---

TRIGGER_WORDS = ["+", "+1", "спасибо", "респект", "thx", "thanks", "спб"]

@dp.message(F.reply_to_message)
async def handle_karma(message: types.Message):
    text = message.text.strip().lower() if message.text else ""
    
    # Проверяем, есть ли триггерное слово
    if any(text == word or text.startswith(word + " ") for word in TRIGGER_WORDS):
        target_user = message.reply_to_message.from_user
        from_user = message.from_user

        # Защита: нельзя давать карму самому себе
        if target_user.id == from_user.id:
            await message.reply("❌ Нельзя поднимать репутацию самому себе!")
            return
            
        # Защита: нельзя давать карму ботам
        if target_user.is_bot:
            await message.reply("🤖 Ботам репутация не нужна!")
            return

        # Начисление кармы
        user_data = karma_db.get(target_user.id, {"name": target_user.first_name, "karma": 0})
        user_data["karma"] += 1
        user_data["name"] = target_user.first_name
        karma_db[target_user.id] = user_data

        await message.answer(
            f"👍 **{from_user.first_name}** поднял репутацию **{target_user.first_name}**!\n"
            f"Теперь у него ⭐ **{user_data['karma']}** респектов.",
            parse_mode=ParseMode.MARKDOWN
        )

# --- ЗАПУСК БОТА ---

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
