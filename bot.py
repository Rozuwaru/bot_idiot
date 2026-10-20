import asyncio
import random
import logging
import time
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from supabase import create_client, Client

# --- КОНФИГУРАЦИЯ И ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ЮЗЕРНЕЙМЫ АДМИНОВ БОТА (без @, регистр не имеет значения)
ADMIN_USERNAMES = {"rozuwaru", "sanya_g", "nekit", "kostya", "amir"}
DUEL_MUTE_TIME = 5 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

active_duels = {}
marry_requests = {}

# --- МАГАЗИН ПРЕДМЕТОВ ---
SHOP_ITEMS = {
    1: {"name": "🛡 Щит Афины", "price": 500, "type": "shield", "bonus_win": 15, "desc": "+15% к шансу победы в дуэли"},
    2: {"name": "🗡 Меч Хаоса", "price": 750, "type": "weapon", "bonus_win": 20, "desc": "+20% к шансу победы в дуэли"},
    3: {"name": "🎨 Премиум Рамка", "price": 300, "type": "aura", "bonus_win": 0, "desc": "Визуальный эффект в /me"},
    4: {"name": "👑 Корона Чата", "price": 1500, "type": "crown", "bonus_win": 5, "desc": "VIP статус +5% к дуэлям"}
}

LEVEL_TITLES = {
    1: "💡 Новичок",
    3: "🔫 Главарь",
    5: "👑 Легенда чата",
    10: "🌌 Повелитель байтов",
    20: "💎 Бессмертный",
    30: "👑 Абсолютный Властелин",
    50: "🌌 Бог Чата"
}

BALL_ANSWERS = [
    "Бесспорно! 🔮", "Мне кажется — да 👍", "Даже не думай ❌",
    "Знаки говорят — нет 🛑", "Спроси позже, я сплю 🛌",
    "100% да! ✨", "Звезды против этого 🌌"
]

# --- РАБОТА С БАЗОЙ SUPABASE ---

def get_profile(user: types.User):
    uid = user.id
    response = supabase.table("users").select("*").eq("user_id", uid).execute()
    
    if response.data and len(response.data) > 0:
        data = response.data[0]
        if "coins" not in data or data["coins"] is None: data["coins"] = 100
        if "items" not in data or data["items"] is None: data["items"] = []
        return data
    else:
        new_user = {
            "user_id": uid,
            "name": user.first_name,
            "xp": 0,
            "level": 1,
            "coins": 100,
            "items": [],
            "last_loot": 0.0,
            "wins": 0,
            "msgs": 0,
            "partner_id": 0,
            "partner_name": ""
        }
        supabase.table("users").insert(new_user).execute()
        return new_user

def update_profile(uid: int, data: dict):
    supabase.table("users").update(data).eq("user_id", uid).execute()

def add_xp_and_coins(user_data, xp_amount=0, coins_amount=0):
    user_data['xp'] = max(0, user_data['xp'] + xp_amount)
    user_data['coins'] = max(0, user_data.get('coins', 0) + coins_amount)
    
    current_xp = user_data['xp']
    calculated_level = 1
    xp_needed = 100
    
    while current_xp >= xp_needed:
        current_xp -= xp_needed
        calculated_level += 1
        xp_needed = int(xp_needed * 1.15)
        
    user_data['level'] = calculated_level
    
    update_profile(user_data['user_id'], {
        "xp": user_data['xp'],
        "coins": user_data['coins'],
        "level": user_data['level']
    })

def is_admin(user: types.User) -> bool:
    if not user.username:
        return False
    return user.username.lower() in {u.lower() for u in ADMIN_USERNAMES}

# --- ПОЛНЫЙ СПИСОК КОМАНД (ДЛЯ ВСЕХ И АДМИНОВ) ---

@dp.message(Command("start"))
@dp.message(Command("help"))
@dp.message(Command("commands"))
@dp.message(Command("all_commands"))
async def cmd_all_commands(message: types.Message):
    admin_block = ""
    if is_admin(message.from_user):
        admin_block = (
            "\n\n🛡 **АДМИНСКИЕ КОМАНДЫ (Управление игроками):**\n"
            "*(Применять ответом на сообщение пользователя)*\n"
            "• `/add_xp <кол-во>` — Выдать XP.\n"
            "• `/remove_xp <кол-во>` — Забрать XP.\n"
            "• `/set_xp <кол-во>` — Установить точный XP.\n"
            "• `/add_coins <кол-во>` — Выдать монеты 🪙.\n"
            "• `/remove_coins <кол-во>` — Забрать монеты 🪙.\n"
            "• `/set_coins <кол-во>` — Установить точный баланс монет.\n"
            "• `/set_level <лвл>` — Изменить уровень игрока.\n"
            "• `/clear_inv` — Очистить инвентарь игрока.\n"
            "• `/reset_user` — Полный сброс всего прогресса игрока."
        )

    text = (
        "📋 **ПОЛНЫЙ СПИСОК КОМАНД БОТА:**\n\n"
        "👤 **Профиль и Экономика:**\n"
        "• `/me` — Твой профиль, баланс монет 🪙 и снаряжение.\n"
        "• `/shop` — Магазин оружия, щитов и титулов.\n"
        "• `/buy <id>` — Купить предмет по номеру из магазина.\n"
        "• `/inv` — Просмотр своего инвентаря.\n"
        "• `/pay <сумма>` (ответом) — Перевести монеты другому игроку.\n"
        "• `/top` — Таблица лучших и самых богатых игроков.\n"
        "• `/loot` — Ежедневный забор бесплатных XP и монет.\n"
        "• Ответь `+` на сообщение — Повысить репутацию игроку.\n\n"
        "⚔️ **Игры и Ивенты:**\n"
        "• `/duel` (ответом) — Вызвать на дуэль с мутом (предметы дают преимущество!).\n"
        "• `/casino <ставка>` — Сыграть в казино на монеты 🪙.\n"
        "• `/roulette` — Русская рулетка (риск мута за +100 XP).\n"
        "• `/ball <вопрос>` — Задать вопрос шар судьбы.\n\n"
        "💍 **Брак и Отношения:**\n"
        "• `/marry` (ответом) — Сделать предложение человеку.\n"
        "• `/divorce` — Развестись.\n"
        "• `/partner` — Посмотреть свою половинку."
        f"{admin_block}"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

# --- ОБРАБОТЧИК СООБЩЕНИЙ ЧАТА ---

@dp.message(F.chat.type.in_({"group", "supergroup"}), ~F.text.startswith("/"))
async def process_message_xp(message: types.Message):
    user_data = get_profile(message.from_user)
    user_data['msgs'] += 1
    user_data['coins'] = user_data.get('coins', 0) + 1
    update_profile(user_data['user_id'], {"msgs": user_data['msgs'], "coins": user_data['coins']})
    
    if random.random() < 0.05:
        add_xp_and_coins(user_data, xp_amount=5, coins_amount=10)

@dp.message(F.reply_to_message, F.text.strip() == "+")
async def handle_rep(message: types.Message):
    target_user = message.reply_to_message.from_user
    from_user = message.from_user

    if target_user.id == from_user.id or target_user.is_bot:
        return

    target_data = get_profile(target_user)
    add_xp_and_coins(target_data, xp_amount=15, coins_amount=25)
    await message.answer(f"🤝 **{from_user.first_name}** респектнул **{target_user.first_name}**!\n+15 XP и +25 🪙 монет.")

# --- ЭКОНОМИКА И МАГАЗИН ---

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    text = "🛒 **МАГАЗИН СНАРЯЖЕНИЯ И ПРИКОЛОВ:**\n\n"
    for item_id, item in SHOP_ITEMS.items():
        text += f"`[{item_id}]` **{item['name']}** — `{item['price']}` 🪙\n└ *{item['desc']}*\n\n"
    text += "👉 Для покупки напиши: `/buy <номер_предмета>`"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit():
        await message.reply("⚠️ Укажи ID предмета. Пример: `/buy 1`")
        return
        
    item_id = int(command.args)
    if item_id not in SHOP_ITEMS:
        await message.reply("❌ Предмета с таким ID нет в магазине!")
        return
        
    item = SHOP_ITEMS[item_id]
    user_data = get_profile(message.from_user)
    items_list = user_data.get("items") or []
    
    if item["name"] in items_list:
        await message.reply("❌ У тебя уже есть этот предмет!")
        return
        
    if user_data.get("coins", 0) < item["price"]:
        await message.reply(f"❌ Недостаточно монет! Нужен `{item['price']}` 🪙, а у тебя `{user_data.get('coins', 0)}` 🪙.")
        return
        
    user_data["coins"] -= item["price"]
    items_list.append(item["name"])
    
    update_profile(user_data["user_id"], {"coins": user_data["coins"], "items": items_list})
    await message.reply(f"🎉 Ты успешно купил **{item['name']}**! Посмотреть: `/inv`.")

@dp.message(Command("inv"))
async def cmd_inv(message: types.Message):
    user_data = get_profile(message.from_user)
    items_list = user_data.get("items") or []
    
    if not items_list:
        await message.reply("🎒 Твой инвентарь пуст. Купить предметы можно в `/shop`!")
        return
        
    items_str = "\n".join([f"• {it}" for it in items_list])
    await message.reply(f"🎒 **Инвентарь {message.from_user.first_name}:**\n\n{items_str}")

@dp.message(Command("pay"), F.reply_to_message)
async def cmd_pay(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit():
        await message.reply("⚠️ Укажи сумму. Пример: `/pay 100` (ответом на сообщение)")
        return
        
    amount = int(command.args)
    sender = get_profile(message.from_user)
    target_user = message.reply_to_message.from_user
    
    if target_user.id == message.from_user.id or target_user.is_bot:
        await message.reply("❌ Нельзя переводить монеты самому себе или боту!")
        return
        
    if sender.get("coins", 0) < amount:
        await message.reply("❌ У тебя нет столько монет!")
        return
        
    target_data = get_profile(target_user)
    sender["coins"] -= amount
    target_data["coins"] = target_data.get("coins", 0) + amount
    
    update_profile(sender["user_id"], {"coins": sender["coins"]})
    update_profile(target_data["user_id"], {"coins": target_data["coins"]})
    await message.answer(f"💸 **{message.from_user.first_name}** перевёл `{amount}` 🪙 монет пользователю **{target_user.first_name}**!")

# --- ПРОФИЛЬ И СТАТИСТИКА ---

@dp.message(Command("me"))
async def cmd_me(message: types.Message):
    user_data = get_profile(message.from_user)
    available_levels = [lvl for lvl in LEVEL_TITLES.keys() if lvl <= user_data['level']]
    title = LEVEL_TITLES[max(available_levels)] if available_levels else "💡 Новичок"
    
    items = user_data.get("items") or []
    aura = "✨ [Премиум Аура] ✨\n" if "🎨 Премиум Рамка" in items else ""
    crown = "👑 " if "👑 Корона Чата" in items else ""
    
    admin_status = "🛡 **Администратор бота**\n" if is_admin(message.from_user) else ""
    partner_text = f"\n💍 Половинка: **{user_data.get('partner_name', 'Нет')}**" if user_data.get('partner_id') else ""
    
    text = (
        f"{aura}{admin_status}"
        f"👤 **Профиль: {crown}{user_data['name']}**\n\n"
        f"🪙 Баланс: `{user_data.get('coins', 0)}` монет\n"
        f"🏅 Уровень: **{user_data['level']}**\n"
        f"🎖 Титул: *{title}*\n"
        f"✨ Опыт: `{user_data['xp']}` XP\n"
        f"🎒 Предметов в инвентаре: `{len(items)}` (/inv)\n"
        f"⚔ Побед в дуэлях: `{user_data['wins']}`"
        f"{partner_text}"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    response = supabase.table("users").select("name, level, coins").order("coins", desc=True).limit(10).execute()
    
    if not response.data:
        await message.answer("📊 Топ пока пуст.")
        return
        
    text = "🏆 **ТОП 10 САМЫХ БОГАТЫХ ИГРОКОВ:**\n\n"
    for idx, u in enumerate(response.data, 1):
        coins = u.get('coins', 0)
        text += f"{idx}. **{u['name']}** — `{coins}` 🪙 (Уровень {u['level']})\n"
        
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("loot"))
async def cmd_loot(message: types.Message):
    user_data = get_profile(message.from_user)
    now = time.time()
    
    if now - user_data['last_loot'] < 86400:
        cooldown = timedelta(seconds=int(86400 - (now - user_data['last_loot'])))
        await message.reply(f"⏱ Ты уже забирал лут. Возвращайся через: `{cooldown}`")
        return

    loot_xp = random.randint(10, 50)
    loot_coins = random.randint(50, 200)
    
    add_xp_and_coins(user_data, xp_amount=loot_xp, coins_amount=loot_coins)
    update_profile(user_data['user_id'], {"last_loot": now})
    await message.reply(f"🎁 **Ежедневный Бокс!** Ты получил **+{loot_xp} XP** и **+{loot_coins} 🪙** монет!")

# --- СЕМЬИ И СВАДЬБЫ ---

@dp.message(Command("marry"), F.reply_to_message)
async def cmd_marry(message: types.Message):
    sender, target = message.from_user, message.reply_to_message.from_user
    if sender.id == target.id or target.is_bot:
        await message.reply("❌ Нельзя жениться на себе или боте!")
        return
        
    s_data, t_data = get_profile(sender), get_profile(target)
    if s_data.get('partner_id') or t_data.get('partner_id'):
        await message.reply("❌ Кто-то из вас уже состоит в браке!")
        return
        
    marry_requests[target.id] = sender.id
    await message.answer(f"💍 **{sender.first_name}** делает предложение **{target.first_name}**!\nОтветь `согласен` на это сообщение.")

@dp.message(F.reply_to_message, F.text.lower().in_({"согласен", "согласна", "да"}))
async def handle_marry_accept(message: types.Message):
    target = message.from_user
    if target.id not in marry_requests: return
        
    sender_id = marry_requests[target.id]
    sender_res = supabase.table("users").select("*").eq("user_id", sender_id).execute()
    if not sender_res.data: return
        
    sender_data = sender_res.data[0]
    update_profile(sender_id, {"partner_id": target.id, "partner_name": target.first_name})
    update_profile(target.id, {"partner_id": sender_id, "partner_name": sender_data['name']})
    await message.answer(f"🎉 **ПОЗДРАВЛЯЕМ!** **{sender_data['name']}** и **{target.first_name}** теперь в браке! 💍✨")
    del marry_requests[target.id]

@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message):
    user_data = get_profile(message.from_user)
    partner_id = user_data.get('partner_id')
    if not partner_id:
        await message.reply("❌ Ты не состоишь в браке!")
        return
        
    update_profile(user_data['user_id'], {"partner_id": 0, "partner_name": ""})
    update_profile(partner_id, {"partner_id": 0, "partner_name": ""})
    await message.reply("💔 Вы успешно развелись.")

@dp.message(Command("partner"))
async def cmd_partner(message: types.Message):
    user_data = get_profile(message.from_user)
    p_name = user_data.get('partner_name')
    if p_name:
        await message.reply(f"💍 Ваша половинка: **{p_name}**")
    else:
        await message.reply("💔 У тебя пока нет половинки. Сделай предложение командой `/marry`!")

# --- ДУЭЛИ И АЗАРТ ---

@dp.message(Command("duel"), F.reply_to_message)
async def cmd_duel(message: types.Message):
    challenger, target = message.from_user, message.reply_to_message.from_user
    if target.id == challenger.id or target.is_bot:
        await message.reply("❌ Нельзя дуэлиться с самим собой или ботом.")
        return
        
    active_duels[target.id] = {'challenger_id': challenger.id, 'time': time.time()}
    await message.answer(f"⚔ **{challenger.first_name}** вызывает **{target.first_name}** на смертельную дуэль!\nОтветь `да` в течение 60 секунд.")

@dp.message(F.reply_to_message, F.text.lower() == "да")
async def handle_duel_accept(message: types.Message):
    target = message.from_user
    if target.id not in active_duels: return
    
    duel_data = active_duels[target.id]
    challenger_id = duel_data['challenger_id']
    
    c_res = supabase.table("users").select("*").eq("user_id", challenger_id).execute()
    c_data = c_res.data[0] if c_res.data else get_profile(types.User(id=challenger_id, first_name="Инициатор", is_bot=False))
    t_data = get_profile(target)
    
    c_items, t_items = c_data.get("items") or [], t_data.get("items") or []
    c_bonus = (15 if "🛡 Щит Афины" in c_items else 0) + (20 if "🗡 Меч Хаоса" in c_items else 0) + (5 if "👑 Корона Чата" in c_items else 0)
    t_bonus = (15 if "🛡 Щит Афины" in t_items else 0) + (20 if "🗡 Меч Хаоса" in t_items else 0) + (5 if "👑 Корона Чата" in t_items else 0)
    
    challenger_win_chance = max(10, min(90, 50 + c_bonus - t_bonus))
    await message.answer(f"⚡️ Дуэль! Шансы: {c_data['name']} ({challenger_win_chance}%) vs {t_data['name']} ({100 - challenger_win_chance}%)...")
    await asyncio.sleep(2)
    
    if random.randint(1, 100) <= challenger_win_chance:
        winner_data, loser_id = c_data, t_data['user_id']
    else:
        winner_data, loser_id = t_data, c_data['user_id']

    winner_data['wins'] = winner_data.get('wins', 0) + 1
    add_xp_and_coins(winner_data, xp_amount=35, coins_amount=100)
    update_profile(winner_data['user_id'], {"wins": winner_data['wins']})
    
    try:
        until_date = datetime.now() + timedelta(minutes=DUEL_MUTE_TIME)
        await bot.restrict_chat_member(message.chat.id, loser_id, permissions=types.ChatPermissions(can_send_messages=False), until_date=until_date)
        await message.answer(f"🏆 **{winner_data['name']}** победил, забирает **+35 XP** и **+100 🪙**!\n💀 Проигравший замучен на {DUEL_MUTE_TIME} минут.")
    except TelegramBadRequest:
        await message.answer(f"🏆 **{winner_data['name']}** побеждает в дуэли и забирает **+35 XP** и **+100 🪙**!")

    del active_duels[target.id]

@dp.message(Command("casino"))
async def cmd_casino(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit():
        await message.reply("⚠️ Пример: `/casino 50`")
        return
    bet = int(command.args)
    user_data = get_profile(message.from_user)
    if bet <= 0 or bet > user_data.get('coins', 0):
        await message.reply("❌ Недостаточно монет!")
        return

    if random.randint(1, 100) <= 45:
        add_xp_and_coins(user_data, coins_amount=bet)
        await message.reply(f"🎰 **ПОБЕДА!** Ты выиграл **+{bet} 🪙** монет!")
    else:
        add_xp_and_coins(user_data, coins_amount=-bet)
        await message.reply(f"🎰 **ПРОИГРЫШ!** Ты потерял **-{bet} 🪙** монет.")

@dp.message(Command("roulette"))
async def cmd_roulette(message: types.Message):
    user_data = get_profile(message.from_user)
    await message.answer("🎰 Крутим барабан...")
    await asyncio.sleep(2)
    if random.randint(1, 6) == 1:
        try:
            until_date = datetime.now() + timedelta(minutes=3)
            await bot.restrict_chat_member(message.chat.id, message.from_user.id, permissions=types.ChatPermissions(can_send_messages=False), until_date=until_date)
            await message.answer(f"💥 **ВЫСТРЕЛ!** **{message.from_user.first_name}** отправлен в мут на 3 минуты!")
        except TelegramBadRequest:
            await message.answer("💥 **ВЫСТРЕЛ!** Но у меня нет прав замутить тебя.")
    else:
        add_xp_and_coins(user_data, xp_amount=50, coins_amount=150)
        await message.answer(f"📊 **КЛИК!** Пустой барабан! Выживший получает **+50 XP** и **+150 🪙**!")

@dp.message(Command("ball"))
async def cmd_ball(message: types.Message, command: CommandObject):
    if not command.args: return
    await message.reply(f"🔮 {random.choice(BALL_ANSWERS)}")

# --- ВСЕМОГУЩИЕ АДМИНСКИЕ КОМАНДЫ ---

@dp.message(Command("add_xp"), F.reply_to_message)
async def admin_add_xp(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    target_data = get_profile(message.reply_to_message.from_user)
    add_xp_and_coins(target_data, xp_amount=int(command.args))
    await message.answer(f"🛡 Админ выдал **+{command.args} XP** пользователю **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("remove_xp"), F.reply_to_message)
async def admin_remove_xp(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    target_data = get_profile(message.reply_to_message.from_user)
    add_xp_and_coins(target_data, xp_amount=-int(command.args))
    await message.answer(f"🛡 Админ забрал **-{command.args} XP** у пользователя **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("set_xp"), F.reply_to_message)
async def admin_set_xp(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    val = int(command.args)
    target_data = get_profile(message.reply_to_message.from_user)
    target_data['xp'] = val
    update_profile(target_data['user_id'], {"xp": val})
    await message.answer(f"🛡 Админ установил XP = **{val}** для **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("add_coins"), F.reply_to_message)
async def admin_add_coins(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    target_data = get_profile(message.reply_to_message.from_user)
    add_xp_and_coins(target_data, coins_amount=int(command.args))
    await message.answer(f"🛡 Админ выдал **+{command.args} 🪙** пользователю **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("remove_coins"), F.reply_to_message)
async def admin_remove_coins(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    target_data = get_profile(message.reply_to_message.from_user)
    add_xp_and_coins(target_data, coins_amount=-int(command.args))
    await message.answer(f"🛡 Админ забрал **-{command.args} 🪙** у пользователя **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("set_coins"), F.reply_to_message)
async def admin_set_coins(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    val = int(command.args)
    target_data = get_profile(message.reply_to_message.from_user)
    target_data['coins'] = val
    update_profile(target_data['user_id'], {"coins": val})
    await message.answer(f"🛡 Админ установил монеты = **{val} 🪙** для **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("set_level"), F.reply_to_message)
async def admin_set_level(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    val = int(command.args)
    target_data = get_profile(message.reply_to_message.from_user)
    target_data['level'] = val
    update_profile(target_data['user_id'], {"level": val})
    await message.answer(f"🛡 Админ установил уровень = **{val}** для **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("clear_inv"), F.reply_to_message)
async def admin_clear_inv(message: types.Message):
    if not is_admin(message.from_user): return
    target_data = get_profile(message.reply_to_message.from_user)
    update_profile(target_data['user_id'], {"items": []})
    await message.answer(f"🛡 Админ полностью очистил инвентарь пользователя **{message.reply_to_message.from_user.first_name}**!")

@dp.message(Command("reset_user"), F.reply_to_message)
async def admin_reset_user(message: types.Message):
    if not is_admin(message.from_user): return
    target_user = message.reply_to_message.from_user
    
    reset_data = {
        "xp": 0, "level": 1, "coins": 100, "items": [],
        "wins": 0, "partner_id": 0, "partner_name": ""
    }
    update_profile(target_user.id, reset_data)
    await message.answer(f"💥 **ПОЛНЫЙ СБРОС!** Админ сбросил весь прогресс пользователя **{target_user.first_name}**!")

# --- ЗАПУСК ---
async def main():
    print("Супер-бот с полной панелью администратора запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
