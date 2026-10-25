import asyncio
import logging
import os
import random
import time
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAHWYb30wS3F4vnnzWdB8MrH_50TTqnBRpE"
SUPABASE_URL = "https://cbypocbgeevwqhjahchy.supabase.co"
SUPABASE_KEY = "sb_publishable_zcF4S765sEmvXLIQegRkFg_1el4gZn_".strip()

ADMIN_USERNAMES = {"p0tat0777"}
DUEL_MUTE_TIME = 3

logging.basicConfig(level=logging.INFO)

# Инициализация бота и клиента Supabase
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 67 УРОВНЕЙ, ОПЫТ И ТИТУЛЫ ---
LEVELS = {
    1: {"xp": 0, "title": "Новичок"},
    2: {"xp": 125, "title": "Бродяга"},
    3: {"xp": 275, "title": "Пешка"},
    4: {"xp": 450, "title": "Деревенщина"},
    5: {"xp": 650, "title": "Искатель приключений"},
    6: {"xp": 875, "title": "Наемник"},
    7: {"xp": 1125, "title": "Ополченец"},
    8: {"xp": 1400, "title": "Стражник"},
    9: {"xp": 1700, "title": "Ветеран"},
    10: {"xp": 2025, "title": "Охотник на монстров"},
    11: {"xp": 2375, "title": "Следопыт"},
    12: {"xp": 2750, "title": "Рейнджер"},
    13: {"xp": 3150, "title": "Ветеран пустошей"},
    14: {"xp": 3575, "title": "Мастер меча"},
    15: {"xp": 4025, "title": "Рыцарь"},
    16: {"xp": 4500, "title": "Баронет"},
    17: {"xp": 5000, "title": "Барон"},
    18: {"xp": 5525, "title": "Виконт"},
    19: {"xp": 6075, "title": "Граф"},
    20: {"xp": 6650, "title": "Маркиз"},
    21: {"xp": 7250, "title": "Герцог"},
    22: {"xp": 7875, "title": "Принц"},
    23: {"xp": 8525, "title": "Король"},
    24: {"xp": 9200, "title": "Император"},
    25: {"xp": 9900, "title": "Владыка земель"},
    26: {"xp": 10625, "title": "Повелитель зверей"},
    27: {"xp": 11375, "title": "Заклинатель теней"},
    28: {"xp": 12150, "title": "Архимаг"},
    29: {"xp": 12950, "title": "Верховный жрец"},
    30: {"xp": 13775, "title": "Хранитель портала"},
    31: {"xp": 14625, "title": "Покоритель стихий"},
    32: {"xp": 15500, "title": "Титан"},
    33: {"xp": 16400, "title": "Колосс"},
    34: {"xp": 17325, "title": "Джаггернаут"},
    35: {"xp": 18275, "title": "Берсерк"},
    36: {"xp": 19250, "title": "Гладиатор"},
    37: {"xp": 20250, "title": "Чемпион арены"},
    38: {"xp": 21275, "title": "Легендарный боец"},
    39: {"xp": 22325, "title": "Непобедимый"},
    40: {"xp": 23400, "title": "Полубог"},
    41: {"xp": 24500, "title": "Аватар войны"},
    42: {"xp": 25625, "title": "Вестник хаоса"},
    43: {"xp": 26775, "title": "Повелитель кошмаров"},
    44: {"xp": 27950, "title": "Пожиратель душ"},
    45: {"xp": 29150, "title": "Князь тьмы"},
    46: {"xp": 30375, "title": "Драконоборец"},
    47: {"xp": 31625, "title": "Повелитель драконов"},
    48: {"xp": 32900, "title": "Древний страж"},
    49: {"xp": 34200, "title": "Страж времени"},
    50: {"xp": 35525, "title": "Временной странник"},
    51: {"xp": 36875, "title": "Повелитель галактик"},
    52: {"xp": 38250, "title": "Архитектор миров"},
    53: {"xp": 39650, "title": "Демиург"},
    54: {"xp": 41075, "title": "Создатель судеб"},
    55: {"xp": 42525, "title": "Всемогущий"},
    56: {"xp": 44000, "title": "Сущность света"},
    57: {"xp": 45500, "title": "Сущность пустоты"},
    58: {"xp": 47025, "title": "Абсолют"},
    59: {"xp": 48575, "title": "Бессмертный"},
    60: {"xp": 50150, "title": "Вечный"},
    61: {"xp": 51750, "title": "Владыка вселенной"},
    62: {"xp": 53375, "title": "Победитель реальности"},
    63: {"xp": 55025, "title": "Творец мультивселенной"},
    64: {"xp": 56700, "title": "Альфа и Омега"},
    65: {"xp": 58400, "title": "Трансцендентный"},
    66: {"xp": 60125, "title": "Божество"},
    67: {"xp": 61875, "title": "👑 Абсолютная Легенда"},
}

WORK_COOLDOWNS = {}

JOBS = {
    "1": {
        "name": "⛏ Шахтёр",
        "min_coins": 40,
        "max_coins": 90,
        "xp": 10,
        "desc": "Добыча руды и драгоценных камней в глубоких шахтах.",
    },
    "2": {
        "name": "🛡 Стражник",
        "min_coins": 60,
        "max_coins": 130,
        "xp": 15,
        "desc": "Патрулирование городских стен и защита жителей от монстров.",
    },
    "3": {
        "name": "🧪 Алхимик",
        "min_coins": 90,
        "max_coins": 180,
        "xp": 22,
        "desc": "Создание редких зелий и изучение древних манускриптов.",
    },
    "4": {
        "name": "🐉 Охотник на чудовищ",
        "min_coins": 130,
        "max_coins": 260,
        "xp": 30,
        "desc": "Опасная работа по уничтожению диких тварей на окраинах.",
    },
}

SHOP_ITEMS = {
    "1": {
        "name": "🪵 Деревянный меч",
        "price": 150,
        "effect_type": "xp",
        "value": 30,
        "desc": "Базовое оружие для тренировок. Дает +30 XP.",
    },
    "2": {
        "name": "⚔️ Железный меч",
        "price": 350,
        "effect_type": "xp",
        "value": 90,
        "desc": "Надежный клинок опытного бойца. Дает +90 XP.",
    },
    "3": {
        "name": "🛡 Кожаная броня",
        "price": 250,
        "effect_type": "respect",
        "value": 2,
        "desc": "Защищает в стычках и добавляет солидности (+2 респекта).",
    },
    "4": {
        "name": "🧪 Зелье здоровья",
        "price": 120,
        "effect_type": "xp",
        "value": 45,
        "desc": "Быстро восстанавливает силы и дает +45 XP.",
    },
    "5": {
        "name": "💍 Руническое кольцо",
        "price": 600,
        "effect_type": "respect",
        "value": 6,
        "desc": "Древний артефакт, вызывающий уважение у других (+6 респекта).",
    },
    "6": {
        "name": "📜 Фолиант магии",
        "price": 800,
        "effect_type": "xp",
        "value": 350,
        "desc": "Книга забытых заклинаний. Мощный толчок к развитию (+350 XP).",
    },
    "7": {
        "name": "👑 Корона воина",
        "price": 2000,
        "effect_type": "respect",
        "value": 15,
        "desc": "Атрибут истинного лидера. Сразу поднимает ваш авторитет (+15 респекта).",
    },
}


def is_admin(user: types.User) -> bool:
  if not user or not user.username:
    return False
  return user.username.lower() in {u.lower() for u in ADMIN_USERNAMES}


def get_profile(user: types.User):
  uid = str(user.id)
  response = supabase.table("users").select("*").eq("user_id", uid).execute()
  if response.data:
    return response.data[0]

  new_user = {
      "user_id": uid,
      "username": user.username or user.first_name,
      "coins": 100,
      "xp": 0,
      "level": 1,
      "respect": 0,
      "partner_id": 0,
      "partner_name": "EMPTY",
  }
  res = supabase.table("users").insert(new_user).execute()
  return res.data[0] if res.data else new_user


@dp.message(Command(commands=["start", "help", "commands", "all_commands"]))
async def cmd_all_commands(message: types.Message):
  get_profile(message.from_user)

  admin_block = ""
  if is_admin(message.from_user):
    admin_block = (
        "\n\n🛡 **АДМИНСКИЕ КОМАНДЫ (в ответ на сообщение):**\n"
        "• `/add_xp <кол-во>` — добавить опыт\n"
        "• `/remove_xp <кол-во>` — забрать опыт\n"
        "• `/set_xp <кол-во>` — установить точный опыт\n"
        "• `/add_coins <сумма>` — добавить монеты\n"
        "• `/remove_coins <сумма>` — забрать монеты\n"
        "• `/set_coins <сумма>` — установить баланс монет\n"
        "• `/set_level <ур>` — установить уровень (1-67)"
    )

  text = (
      "📋 **КОМАНДЫ RPG БОТА:**\n\n"
      "👤 **Основные:** `/me`, `/shop`, `/buy <id>`, `/inv`, `/pay <сумма>`, `/top`, `/loot`, `/work`, `/levels`, `+` (ответом на сообщение)\n"
      "⚔️ **Развлечения:** `/duel`, `/casino <ставка>`, `/roulette`, `/ball <вопрос>`\n"
      "💍 **Отношения:** `/marry`, `/accept`, `/reject`, `/divorce`, `/partner`"
      f"{admin_block}"
  )
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("me"))
async def cmd_me(message: types.Message):
  p = get_profile(message.from_user)
  current_lvl = p.get("level", 1)
  title = LEVELS.get(current_lvl, {}).get("title", "Воин")

  partner_id = p.get("partner_id")
  partner_name = p.get("partner_name")
  if (
      partner_id
      and str(partner_id) != "0"
      and partner_name
      and partner_name != "EMPTY"
  ):
    marriage_status = f"💍 В браке с: **{partner_name}**"
  else:
    marriage_status = "💍 Статус: Свободен"

  text = (
      f"👤 **Профиль: {p.get('username')}**\n"
      f"⭐ Уровень: `{current_lvl}` / 67 (*{title}*)\n"
      f"✨ Опыт (XP): `{p.get('xp')}`\n"
      f"🪙 Монеты: `{p.get('coins')}`\n"
      f"❤️ Респект: `{p.get('respect')}`\n"
      f"{marriage_status}"
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
    lvl = u.get("level", 1)
    title = LEVELS.get(lvl, {}).get("title", "")
    text += (
        f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙"
        f" `{u.get('coins')}`\n"
    )
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("levels"))
async def cmd_levels(message: types.Message):
  guide_text = (
      "📈 **ГАЙД ПО ПОВЫШЕНИЮ УРОВНЯ:**\n\n"
      "• 💬 **Общение в чате:** каждое текстовое сообщение дает `+5 XP`.\n"
      "• 💼 **Работа:** выполняйте смены через команду `/work <номер>`, чтобы"
      " получать опыт и монеты.\n"
      "• 🛒 **Магазин:** покупайте фолианты и артефакты через `/shop` для"
      " мгновенного прироста XP.\n\n"
      "⭐ **ТИПУЛЫ И УРОВНИ (1-67):**"
  )
  await message.answer(guide_text, parse_mode=ParseMode.MARKDOWN)

  chunk = ""
  for lvl in range(1, 68):
    data = LEVELS[lvl]
    chunk += f"⭐ Ур. `{lvl}` [{data['title']}]: `{data['xp']} XP`\n"

    if lvl % 15 == 0:
      await message.answer(chunk, parse_mode=ParseMode.MARKDOWN)
      chunk = ""

  if chunk:
    await message.answer(chunk, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("work"))
async def cmd_work(message: types.Message):
  args = message.text.split()
  uid = str(message.from_user.id)
  p = get_profile(message.from_user)

  now = time.time()
  last_time = WORK_COOLDOWNS.get(uid, 0)
  cooldown = 60
  if now - last_time < cooldown:
    remaining = int(cooldown - (now - last_time))
    await message.answer(
        f"⏳ Вы еще не отдохнули после прошлой смены! Подождите еще"
        f" `{remaining}` сек.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return

  if len(args) < 2 or args[1] not in JOBS:
    text = "💼 **БИРЖА ТРУДА И ПРОФЕССИЙ:**\n\nВыберите кем поработать:\n\n"
    for j_id, j_data in JOBS.items():
      text += (
          f"🔹 **[{j_id}] {j_data['name']}**\n"
          f"   └ 🪙 Зарплата: `{j_data['min_coins']}–{j_data['max_coins']}"
          " монет`\n"
          f"   └ ✨ Опыт: `+{j_data['xp']} XP`\n"
          f"   └ 📝 *Описание:* {j_data['desc']}\n\n"
      )
    text += "👉 Для работы введите: `/work <номер>` (например, `/work 1`)"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)
    return

  job_id = args[1]
  job = JOBS[job_id]

  earned_coins = random.randint(job["min_coins"], job["max_coins"])
  earned_xp = job["xp"]

  WORK_COOLDOWNS[uid] = now

  new_coins = p.get("coins", 0) + earned_coins
  new_xp = p.get("xp", 0) + earned_xp
  current_level = p.get("level", 1)

  new_level = current_level
  for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
    if new_xp >= data["xp"]:
      new_level = lvl

  supabase.table("users").update(
      {"coins": new_coins, "xp": new_xp, "level": new_level}
  ).eq("user_id", uid).execute()

  level_up_msg = ""
  if new_level > current_level:
    title = LEVELS[new_level]["title"]
    level_up_msg = (
        f"\n\n🎉 **Поздравляем! Ваш уровень повысился до {new_level}"
        f" (*{title}*)!**"
    )

  await message.answer(
      f"✅ Вы успешно отработали смену как **{job['name']}**!\n"
      f"🪙 Заработано: `{earned_coins}` монет\n"
      f"✨ Получено опыта: `+{earned_xp} XP`"
      f"{level_up_msg}",
      parse_mode=ParseMode.MARKDOWN,
  )


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

  supabase.table("users").update({"coins": sender["coins"] - amount}).eq(
      "user_id", sender["user_id"]
  ).execute()
  supabase.table("users").update({"coins": receiver["coins"] + amount}).eq(
      "user_id", receiver["user_id"]
  ).execute()

  await message.answer(
      f"💸 **{sender['username']}** успешно перевел `{amount}` монет"
      f" **{receiver['username']}**!",
      parse_mode=ParseMode.MARKDOWN,
  )


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


@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
  text = "🛒 **МАГАЗИН ЭКИПИРОВКИ И АРТЕФАКТОВ:**\n\n"
  for item_id, data in SHOP_ITEMS.items():
    text += (
        f"🔹 **[{item_id}] {data['name']}** — 🪙 `{data['price']}` монет\n"
        f"   └ 📝 *Эффект:* {data['desc']}\n\n"
    )
  text += "Купить предмет: `/buy <номер>`"
  await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
  args = message.text.split()
  if len(args) < 2:
    await message.answer(
        "Укажите номер товара: `/buy <id>`", parse_mode=ParseMode.MARKDOWN
    )
    return

  item_id = args[1]
  if item_id not in SHOP_ITEMS:
    await message.answer("Такого товара не существует в магазине.")
    return

  item = SHOP_ITEMS[item_id]
  p = get_profile(message.from_user)

  if p.get("coins", 0) < item["price"]:
    await message.answer("Недостаточно монет для покупки этого предмета!")
    return

  new_coins = p["coins"] - item["price"]
  new_xp = p.get("xp", 0)
  new_respect = p.get("respect", 0)

  if item["effect_type"] == "xp":
    new_xp += item["value"]
  elif item["effect_type"] == "respect":
    new_respect += item["value"]

  current_level = p.get("level", 1)
  new_level = current_level
  for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
    if new_xp >= data["xp"]:
      new_level = lvl

  supabase.table("users").update(
      {
          "coins": new_coins,
          "xp": new_xp,
          "respect": new_respect,
          "level": new_level,
      }
  ).eq("user_id", p["user_id"]).execute()

  await message.answer(
      f"✅ Вы успешно приобрели **{item['name']}** за `{item['price']}` монет!\n"
      f"✨ *Эффект применен:* {item['desc']}",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("inv"))
async def cmd_inv(message: types.Message):
  p = get_profile(message.from_user)
  await message.answer(
      f"🎒 Инвентарь игрока **{p.get('username')}** пуст.",
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


@dp.message(Command("casino"))
async def cmd_casino(message: types.Message):
  args = message.text.split()
  if len(args) < 2:
    await message.answer(
        "Укажите ставку: `/casino <ставка>`", parse_mode=ParseMode.MARKDOWN
    )
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
        f"🎰 Поздравляем! Вы выиграли и получили `{bet}` монет! Баланс:"
        f" `{new_coins}`",
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
  await message.answer("🎯 Рулетка запущена!")


@dp.message(Command("ball"))
async def cmd_ball(message: types.Message):
  answers = [
      "Да",
      "Нет",
      "Скорее всего да",
      "Точно нет",
      "Спроси позже",
      "Определенно да",
  ]
  await message.answer(
      f"🎱 Шар говорит: *{random.choice(answers)}*", parse_mode=ParseMode.MARKDOWN
  )


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


# --- ОТНОШЕНИЯ И БРАКИ ---
@dp.message(Command("marry"))
async def cmd_marry(message: types.Message):
  if not message.reply_to_message:
    await message.answer(
        "💍 Чтобы сделать предложение, ответьте на сообщение пользователя"
        " командой `/marry`.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return

  target_user = message.reply_to_message.from_user
  if target_user.id == message.from_user.id:
    await message.answer("Нельзя заключить брак с самим собой! 😄")
    return

  sender = get_profile(message.from_user)
  if sender.get("partner_id") and str(sender.get("partner_id")) != "0":
    await message.answer(
        "💍 Вы уже состоите в браке! Сначала нужно развестись (`/divorce`)."
    )
    return

  target = get_profile(target_user)
  if target.get("partner_id") and str(target.get("partner_id")) != "0":
    await message.answer("💍 Этот пользователь уже состоит в браке!")
    return

  await message.answer(
      f"💍 **{message.from_user.first_name}** делает предложение руки и сердца"
      f" **{target_user.first_name}**!\n\n✅ Чтобы принять, ответьте на это"
      " сообщение командой `/accept`\n❌ Чтобы отказаться, ответьте на это"
      " сообщение командой `/reject`",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("accept"))
async def cmd_accept(message: types.Message):
  if not message.reply_to_message:
    await message.answer(
        "💍 Чтобы принять предложение, ответьте на сообщение с предложением"
        " командой `/accept`.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return

  proposer_user = message.reply_to_message.from_user
  accepter_user = message.from_user

  if proposer_user.id == accepter_user.id:
    await message.answer("Нельзя принимать предложения самому себе.")
    return

  proposer = get_profile(proposer_user)
  accepter = get_profile(accepter_user)

  if proposer.get("partner_id") and str(proposer.get("partner_id")) != "0":
    await message.answer("Этот пользователь уже занят!")
    return
  if accepter.get("partner_id") and str(accepter.get("partner_id")) != "0":
    await message.answer("Вы уже состоите в браке!")
    return

  supabase.table("users").update(
      {"partner_id": str(accepter_user.id), "partner_name": accepter_user.first_name}
  ).eq("user_id", str(proposer_user.id)).execute()

  supabase.table("users").update(
      {"partner_id": str(proposer_user.id), "partner_name": proposer_user.first_name}
  ).eq("user_id", str(accepter_user.id)).execute()

  await message.answer(
      f"🎉 Горько! 🥂 **{proposer_user.first_name}** и"
      f" **{accepter_user.first_name}** официально поженились! 💍❤️",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("reject"))
async def cmd_reject(message: types.Message):
  if not message.reply_to_message:
    await message.answer(
        "💍 Чтобы отклонить предложение, ответьте на сообщение с предложением"
        " командой `/reject`.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return

  proposer_user = message.reply_to_message.from_user
  rejecter_user = message.from_user

  await message.answer(
      f"💔 **{rejecter_user.first_name}** отклонил(а) предложение руки и сердца"
      f" от **{proposer_user.first_name}**. Эх...",
      parse_mode=ParseMode.MARKDOWN,
  )


@dp.message(Command("partner"))
async def cmd_partner(message: types.Message):
  p = get_profile(message.from_user)
  partner_id = p.get("partner_id")
  partner_name = p.get("partner_name")

  if (
      not partner_id
      or str(partner_id) == "0"
      or not partner_name
      or partner_name == "EMPTY"
  ):
    await message.answer(
        "💍 У вас пока нет партнера. Сделайте кому-нибудь предложение через"
        " `/marry`!",
        parse_mode=ParseMode.MARKDOWN,
    )
  else:
    await message.answer(
        f"💍 Ваша вторая половинка: **{partner_name}** ❤️",
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message):
  p = get_profile(message.from_user)
  partner_id = p.get("partner_id")

  if not partner_id or str(partner_id) == "0":
    await message.answer("💔 Вы и так не состоите в браке.")
    return

  supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY"}).eq(
      "user_id", str(partner_id)
  ).execute()

  supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY"}).eq(
      "user_id", p["user_id"]
  ).execute()

  await message.answer(
      "💔 Вы успешно расторгли брак.", parse_mode=ParseMode.MARKDOWN
  )


# --- ПОЛНОЦЕННЫЕ АДМИНСКИЕ КОМАНДЫ ---


async def verify_admin(message: types.Message) -> bool:
  if not is_admin(message.from_user):
    await message.answer("❌ У вас нет прав администратора.")
    return False
  if not message.reply_to_message:
    await message.answer(
        "⚠️ Сделайте реплай (ответ) на сообщение игрока, к которому хотите"
        " применить команду!"
    )
    return False
  return True


@dp.message(Command("add_coins"))
async def admin_add_coins(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    amount = int(args[1])
  except ValueError:
    return

  target = get_profile(message.reply_to_message.from_user)
  new_coins = target["coins"] + amount
  supabase.table("users").update({"coins": new_coins}).eq(
      "user_id", target["user_id"]
  ).execute()
  await message.answer(
      f"🛡 Админ добавил `{amount}` монет игроку **{target['username']}**."
  )


@dp.message(Command("remove_coins"))
async def admin_remove_coins(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    amount = int(args[1])
  except ValueError:
    return

  target = get_profile(message.reply_to_message.from_user)
  new_coins = max(0, target["coins"] - amount)
  supabase.table("users").update({"coins": new_coins}).eq(
      "user_id", target["user_id"]
  ).execute()
  await message.answer(
      f"🛡 Админ забрал `{amount}` монет у игрока **{target['username']}**."
  )


@dp.message(Command("set_coins"))
async def admin_set_coins(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    amount = int(args[1])
  except ValueError:
    return

  target = get_profile(message.reply_to_message.from_user)
  supabase.table("users").update({"coins": amount}).eq(
      "user_id", target["user_id"]
  ).execute()
  await message.answer(
      f"🛡 У игрока **{target['username']}** баланс монет установлен на"
      f" `{amount}`."
  )


@dp.message(Command("add_xp"))
async def admin_add_xp(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    amount = int(args[1])
  except ValueError:
    return

  target = get_profile(message.reply_to_message.from_user)
  new_xp = target.get("xp", 0) + amount

  new_level = target.get("level", 1)
  for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
    if new_xp >= data["xp"]:
      new_level = lvl

  supabase.table("users").update({"xp": new_xp, "level": new_level}).eq(
      "user_id", target["user_id"]
  ).execute()
  title = LEVELS[new_level]["title"]
  await message.answer(
      f"🛡 Админ добавил `+{amount} XP` игроку **{target['username']}**"
      f" (Уровень: `{new_level}` — *{title}*)."
  )


@dp.message(Command("remove_xp"))
async def admin_remove_xp(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    amount = int(args[1])
  except ValueError:
    return

  target = get_profile(message.reply_to_message.from_user)
  new_xp = max(0, target.get("xp", 0) - amount)

  new_level = 1
  for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
    if new_xp >= data["xp"]:
      new_level = lvl

  supabase.table("users").update({"xp": new_xp, "level": new_level}).eq(
      "user_id", target["user_id"]
  ).execute()
  title = LEVELS[new_level]["title"]
  await message.answer(
      f"🛡 Админ забрал `{amount} XP` у игрока **{target['username']}**"
      f" (Уровень: `{new_level}` — *{title}*)."
  )


@dp.message(Command("set_xp"))
async def admin_set_xp(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    amount = int(args[1])
  except ValueError:
    return

  target = get_profile(message.reply_to_message.from_user)
  new_xp = amount

  new_level = 1
  for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
    if new_xp >= data["xp"]:
      new_level = lvl

  supabase.table("users").update({"xp": new_xp, "level": new_level}).eq(
      "user_id", target["user_id"]
  ).execute()
  title = LEVELS[new_level]["title"]
  await message.answer(
      f"🛡 У игрока **{target['username']}** установлено точно `{amount} XP`"
      f" (Уровень: `{new_level}` — *{title}*)."
  )


@dp.message(Command("set_level"))
async def admin_set_level(message: types.Message):
  if not await verify_admin(message):
    return
  args = message.text.split()
  if len(args) < 2:
    return
  try:
    lvl = int(args[1])
  except ValueError:
    return

  if lvl not in LEVELS:
    await message.answer("❌ Такого уровня не существует (от 1 до 67).")
    return

  target = get_profile(message.reply_to_message.from_user)
  required_xp = LEVELS[lvl]["xp"]

  supabase.table("users").update({"level": lvl, "xp": required_xp}).eq(
      "user_id", target["user_id"]
  ).execute()
  title = LEVELS[lvl]["title"]
  await message.answer(
      f"🛡 Уровень игрока **{target['username']}** изменен на `{lvl}`"
      f" (*{title}*), а опыт автоматически подогнан под порог (`{required_xp}"
      " XP`)."
  )


# --- НАЧИСЛЕНИЕ XP ЗА СООБЩЕНИЯ И ПОВЫШЕНИЕ УРОВНЕЙ ---
@dp.message(F.text)
async def process_message_xp(message: types.Message):
  if message.text.startswith("/"):
    return

  uid = str(message.from_user.id)
  p = get_profile(message.from_user)

  new_xp = p.get("xp", 0) + 5
  current_level = p.get("level", 1)

  new_level = current_level
  for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
    if new_xp >= data["xp"]:
      new_level = lvl

  if new_level > current_level:
    title = LEVELS[new_level]["title"]
    await message.answer(
        f"🎉 Поздравляем, {message.from_user.first_name}! У вас повысился"
        f" уровень до **{new_level} (*{title}*)**!",
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
  await bot.set_my_commands([
      BotCommand(command="start", description="Запустить бота и меню"),
      BotCommand(command="me", description="Мой профиль"),
      BotCommand(command="shop", description="Магазин предметов"),
      BotCommand(command="inv", description="Инвентарь"),
      BotCommand(command="top", description="Топ игроков"),
      BotCommand(command="levels", description="Таблица уровней и гайд"),
      BotCommand(command="work", description="Биржа труда (работа)"),
      BotCommand(command="duel", description="Дуэль с игроком"),
      BotCommand(command="casino", description="Сыграть в казино"),
      BotCommand(command="marry", description="Сделать предложение"),
      BotCommand(command="partner", description="Моя вторая половинка"),
      BotCommand(command="help", description="Все команды бота"),
  ])

  asyncio.create_task(web_server())
  print("Бот запущен и ожидает сообщения...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
