import asyncio
import logging
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAH-5pSNsC4gV7vVSMoa6oyC6GHAGQgoh_w"
SUPABASE_URL = "https://cbypocbgeevwqhjahchy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNicXBvY2JnZWV3cWhqYWhjaHkiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTczMDM1MTM3MiwiZXhwIjoyMDQ1OTExMzcyfQ.B2kKt2EeYidQ0a78EcZF83oJgOVE4gi1qlVnDUr4u34"

ADMIN_USERNAMES = {"p0tat0777"}
DUEL_MUTE_TIME = 3

logging.basicConfig(level=logging.INFO)

# Инициализация бота и клиента Supabase
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def is_admin(user: types.User) -> bool:
  if not user or not user.username:
    return False
  return user.username.lower() in {u.lower() for u in ADMIN_USERNAMES}


def get_profile(user: types.User):
  uid = str(user.id)
  response = supabase.table("users").select("*").eq("user_id", uid).execute()
  if response.data:
    return response.data[0]

  # Создаем профиль по умолчанию, если его нет в базе
  new_user = {
      "user_id": uid,
      "username": user.username or user.first_name,
      "coins": 100,
      "xp": 0,
      "level": 1,
      "respect": 0,
  }
  res = supabase.table("users").insert(new_user).execute()
  return res.data[0] if res.data else new_user


# --- ГЛАВНОЕ МЕНЮ И КОМАНДЫ ---
@dp.message(Command(commands=["start", "help", "commands", "all_commands"]))
async def cmd_all_commands(message: types.Message):
  get_profile(message.from_user)

  admin_block = ""
  if is_admin(message.from_user):
    admin_block = (
        "\n\n🛡 **АДМИНСКИЕ КОМАНДЫ:**\n"
        "• `/add_xp`, `/remove_xp`, `/set_xp`\n"
        "• `/add_coins`, `/remove_coins`, `/set_coins`\n"
        "• `/set_level`, `/clear_inv`, `/reset_user`"
    )

  text = (
      "📋 **КОМАНДЫ RPG БОТА:**\n\n"
      "👤 **Основные:** `/me`, `/shop`, `/buy <id>`, `/inv`, `/pay <сумма>`,"
      " `/top`, `/loot`, `+` (ответом на сообщение)\n"
      "⚔️ **Развлечения:** `/duel`, `/casino <ставка>`, `/roulette`,"
      " `/ball <вопрос>`\n"
      "💍 **Отношения:** `/marry`, `/divorce`, `/partner`"
      f"{admin_block}"
  )
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


# --- ПРОФИЛЬ И ЭКОНОМИКА ---
@dp.message(Command("me"))
async def cmd_me(message: types.Message):
  p = get_profile(message.from_user)
  text = (
      f"👤 **Профиль: {p.get('username')}**\n"
      f"⭐ Уровень: `{p.get('level')}`\n"
      f"✨ Опыт (XP): `{p.get('xp')}`\n"
      f"🪙 Монеты: `{p.get('coins')}`\n"
      f"❤️ Респект: `{p.get('respect')}`"
  )
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("top"))
async def cmd_top(message: types.Message):
  res = (
      supabase.table("users")
      .select("username, level, coins")
      .order("level", desc=True)
      .limit(10)
      .execute()
  )
  if not res.data:
    await message.answer("В базе пока нет игроков.")
    return

  text = "🏆 **ТОП-10 ИГРОКОВ:**\n\n"
  for i, u in enumerate(res.data, 1):
    text += f"{i}. **{u.get('username')}** — Уровень: `{u.get('level')}` (🪙 {u.get('coins')})\n"
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
  args = message.text.split()
  if len(args) < 2 or not message.reply_to_message:
    await message.answer(
        "Использование: ответьте на сообщение пользователя командой `/pay"
        " <сумма>`",
        parse_mode=ParseMode.MARKDOWN,
    )
    return

  try:
    amount = int(args[1])
    if amount <= 0:
      raise ValueError()
  except ValueError:
    await message.answer("Укажите корректную сумму для перевода.")
    return

  sender = get_profile(message.from_user)
  if sender.get("coins", 0) < amount:
    await message.answer("У вас недостаточно монет для перевода!")
    return

  receiver_user = message.reply_to_message.from_user
  if receiver_user.id == message.from_user.id:
    await message.answer("Нельзя переводить монеты самому себе.")
    return

  receiver = get_profile(receiver_user)

  # Обновляем балансы
  supabase.table("users").update(
      {"coins": sender["coins"] - amount}
  ).eq("user_id", sender["user_id"]).execute()
  supabase.table("users").update(
      {"coins": receiver["coins"] + amount}
  ).eq("user_id", receiver["user_id"]).execute()

  await message.answer(
      f"💸 **{sender['username']}** успешно перевел `{amount}` монет"
      f" **{receiver['username']}**!",
      parse_mode=ParseMode.MARKDOWN,
  )


# --- СИСТЕМА РЕСПЕКТА (+) ---
@dp.message(F.text == "+")
async def give_respect(message: types.Message):
  if not message.reply_to_message:
    return
  target_user = message.reply_to_message.from_user
  if target_user.id == message.from_user.id:
    await message.answer("Нельзя повышать респект самому себе.")
    return

  p = get_profile(target_user)
  new_respect = p.get("respect", 0) + 1
  supabase.table("users").update({"respect": new_respect}).eq(
      "user_id", str(target_user.id)
  ).execute()
  await message.answer(
      f"👍 **{message.from_user.first_name}** повысил респект"
      f" **{target_user.first_name}**! (Всего: `{new_respect}`)",
      parse_mode=ParseMode.MARKDOWN,
  )


# --- МАГАЗИН И ИВЕНТЫ ---
@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
  text = (
      "🛒 **МАГАЗИН ПРЕДМЕТОВ:**\n\n"
      "1. `1` — Меч новичка (Цена: 150 монет)\n"
      "2. `2` — Щит защиты (Цена: 300 монет)\n"
      "3. `3` — Зелье опыта (Цена: 100 монет)\n\n"
      "Купить предмет: `/buy <номер>`"
  )
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
  args = message.text.split()
  if len(args) < 2:
    await message.answer("Укажите номер товара: `/buy <id>`", parse_mode=ParseMode.MARKDOWN)
    return

  items = {"1": ("Меч новичка", 150), "2": ("Щит защиты", 300), "3": ("Зелье опыта", 100)}
  item_id = args[1]
  if item_id not in items:
    await message.answer("Такого товара не существует.")
    return

  name, price = items[item_id]
  p = get_profile(message.from_user)
  if p.get("coins", 0) < price:
    await message.answer("Недостаточно монет для покупки!")
    return

  # Списываем монеты
  supabase.table("users").update({"coins": p["coins"] - price}).eq(
      "user_id", p["user_id"]
  ).execute()
  await message.answer(
      f"✅ Вы успешно приобрели **{name}** за `{price}` монет!",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("inv"))
async def cmd_inv(message: types.Message):
  p = get_profile(message.from_user)
  await message.answer(
      f"🎒 Инвентарь игрока **{p.get('username')}** пуст (или находится в разработке).",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("loot"))
async def cmd_loot(message: types.Message):
  coins_won = random.randint(10, 50)
  p = get_profile(message.from_user)
  supabase.table("users").update({"coins": p.get("coins", 0) + coins_won}).eq(
      "user_id", p["user_id"]
  ).execute()
  await message.answer(
      f"🎁 Вы нашли сундук и заработали `{coins_won}` монет!",
      parse_mode=ParseMode.MARKDOWN,
  )


# --- МИНИ-ИГРЫ И РАЗВЛЕЧЕНИЯ ---
@dp.message(Command("casino"))
async def cmd_casino(message: types.Message):
  args = message.text.split()
  if len(args) < 2:
    await message.answer("Укажите ставку: `/casino <ставка>`", parse_mode=ParseMode.MARKDOWN)
    return

  try:
    bet = int(args[1])
    if bet <= 0:
      raise ValueError()
  except ValueError:
    await message.answer("Некорректная ставка.")
    return

  p = get_profile(message.from_user)
  if p.get("coins", 0) < bet:
    await message.answer("У вас нет столько монет для ставки!")
    return

  if random.random() > 0.5:
    new_coins = p["coins"] + bet
    supabase.table("users").update({"coins": new_coins}).eq(
        "user_id", p["user_id"]
    ).execute()
    await message.answer(
        f"🎰 Поздравляем! Вы выиграли и получили `{bet}` монет! Баланс: `{new_coins}`",
        parse_mode=ParseMode.MARKDOWN,
    )
  else:
    new_coins = p["coins"] - bet
    supabase.table("users").update({"coins": new_coins}).eq(
        "user_id", p["user_id"]
    ).execute()
    await message.answer(
        f"🎰 Увы! Вы проиграли `{bet}` монет. Баланс: `{new_coins}`",
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(Command("roulette"))
async def cmd_roulette(message: types.Message):
  await message.answer(
      "🎯 Рулетка запущена! (Функция мини-игры доступна для кастомизации)."
  )


@dp.message(Command("ball"))
async def cmd_ball(message: types.Message):
  answers = ["Да", "Нет", "Скорее всего да", "Точно нет", "Спроси позже", "Определенно да"]
  await message.answer(f"🎱 Шар говорит: *{random.choice(answers)}*", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("duel"))
async def cmd_duel(message: types.Message):
  if not message.reply_to_message:
    await message.answer(
        "⚔️ Чтобы вызвать на дуэль, ответьте на сообщение противника командой"
        " `/duel`",
        parse_mode=ParseMode.MARKDOWN,
    )
    return
  winner = random.choice([message.from_user, message.reply_to_message.from_user])
  await message.answer(
      f"⚔️ Дуэль завершена! Победитель: **{winner.first_name}**!",
      parse_mode=ParseMode.MARKDOWN,
  )


# --- ОТНОШЕНИЯ ---
@dp.message(Command("marry"))
async def cmd_marry(message: types.Message):
  if not message.reply_to_message:
    await message.answer("💍 Ответьте на сообщение пользователя, которому хотите сделать предложение.")
    return
  await message.answer(
      f"💍 **{message.from_user.first_name}** делает предложение"
      f" **{message.reply_to_message.from_user.first_name}**!",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message):
  await message.answer("💔 Вы успешно расторгли брак.")


@dp.message(Command("partner"))
async def cmd_partner(message: types.Message):
  await message.answer("💍 У вас пока нет партнера.")


# --- АДМИНСКИЕ КОМАНДЫ ---
@dp.message(Command("add_coins"))
async def admin_add_coins(message: types.Message):
  if not is_admin(message.from_user):
    return
  args = message.text.split()
  if len(args) < 2 or not message.reply_to_message:
    return
  amount = int(args[1])
  target = get_profile(message.reply_to_message.from_user)
  new_coins = target["coins"] + amount
  supabase.table("users").update({"coins": new_coins}).eq(
      "user_id", target["user_id"]
  ).execute()
  await message.answer(f"🛡 Админ добавил `{amount}` монет игроку {target['username']}.")


@dp.message(Command("set_level"))
async def admin_set_level(message: types.Message):
  if not is_admin(message.from_user):
    return
  args = message.text.split()
  if len(args) < 2 or not message.reply_to_message:
    return
  lvl = int(args[1])
  target = get_profile(message.reply_to_message.from_user)
  supabase.table("users").update({"level": lvl}).eq("user_id", target["user_id"]).execute()
  await message.answer(f"🛡 Уровень игрока {target['username']} изменен на `{lvl}`.")


# --- НАЧИСЛЕНИЕ XP ЗА СООБЩЕНИЯ ---
@dp.message(F.text)
async def process_message_xp(message: types.Message):
  if message.text.startswith("/"):
    return  # Игнорируем команды

  uid = str(message.from_user.id)
  p = get_profile(message.from_user)

  new_xp = p.get("xp", 0) + 5
  new_level = p.get("level", 1)

  if new_xp >= new_level * 100:
    new_level += 1
    await message.answer(
        f"🎉 Поздравляем, {message.from_user.first_name}! У вас повысился уровень до **{new_level}**!",
        parse_mode=ParseMode.MARKDOWN,
    )

  supabase.table("users").update({"xp": new_xp, "level": new_level}).eq(
      "user_id", uid
  ).execute()


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_ping(request):
  return web.Response(text="Бот успешно работает и запущен!")


async def web_server():
  app = web.Application()
  app.router.add_get("/", handle_ping)
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.environ.get("PORT", 10000))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()
  print(f"Веб-сервер запущен на порту {port}")


# --- ЗАПУСК БОТА ---
async def main():
  # Установка выпадающего меню команд в Telegram
  await bot.set_my_commands([
      BotCommand(command="start", description="Запустить бота и меню"),
      BotCommand(command="me", description="Мой профиль"),
      BotCommand(command="shop", description="Магазин предметов"),
      BotCommand(command="inv", description="Инвентарь"),
      BotCommand(command="top", description="Топ игроков"),
      BotCommand(command="duel", description="Дуэль с игроком"),
      BotCommand(command="casino", description="Сыграть в казино"),
      BotCommand(command="marry", description="Создать пару"),
      BotCommand(command="help", description="Все команды бота"),
  ])

  asyncio.create_task(web_server())
  print("Бот запущен и ожидает сообщения...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
