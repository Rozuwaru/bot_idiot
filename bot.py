import asyncio
import random
import logging
import time
import os
from aiohttp import web
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAH-5pSNsC4gV7vVSMoa6oyC6GHAGQgoH_w"
SUPABASE_URL = "https://cbypocbgeevwqhjahchy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNieXBvY2JnZWV2d3FoamFoY2h5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI1MDEzMTEsImV4cCI6MjEwODA3NzMxMX0.B2kKt2EeYidQ0a78EcZF83oJgoVE4gi1qIVnDUr4u34"

ADMIN_USERNAMES = {"p0tat0777"}
DUEL_MUTE_TIME = 3

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

active_duels = {}
marry_requests = {}

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

@dp.message(Command("start"), Command("help"), Command("commands"), Command("all_commands"))
async def cmd_all_commands(message: types.Message):
    admin_block = ""
    if is_admin(message.from_user):
        admin_block = (
            "\n\n🛡 **АДМИНСКИЕ КОМАНДЫ:**\n"
            "• `/add_xp`, `/remove_xp`, `/set_xp`\n"
            "• `/add_coins`, `/remove_coins`, `/set_coins`\n"
            "• `/set_level`, `/clear_inv`, `/reset_user`"
        )

    text = (
        "📋 **КОМАНДЫ БОТА:**\n\n"
        "👤 `/me`, `/shop`, `/buy <id>`, `/inv`, `/pay <сумма>`, `/top`, `/loot`, `+` (респект)\n"
        "⚔️ `/duel`, `/casino <ставка>`, `/roulette`, `/ball <вопрос>`\n"
        "💍 `/marry`, `/divorce`, `/partner`"
        f"{admin_block}"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

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
    if target_user.id == from_user.id or target_user.is_bot: return
    target_data = get_profile(target_user)
    add_xp_and_coins(target_data, xp_amount=15, coins_amount=25)
    await message.answer(f"🤝 **{from_user.first_name}** респектнул **{target_user.first_name}**! (+15 XP, +25 🪙)")

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    text = "🛒 **МАГАЗИН:**\n\n"
    for item_id, item in SHOP_ITEMS.items():
        text += f"`[{item_id}]` **{item['name']}** — `{item['price']}` 🪙\n└ *{item['desc']}*\n\n"
    text += "👉 Купить: `/buy <номер>`"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit(): return
    item_id = int(command.args)
    if item_id not in SHOP_ITEMS: return
    item = SHOP_ITEMS[item_id]
    user_data = get_profile(message.from_user)
    items_list = user_data.get("items") or []
    if item["name"] in items_list or user_data.get("coins", 0) < item["price"]: return
    user_data["coins"] -= item["price"]
    items_list.append(item["name"])
    update_profile(user_data["user_id"], {"coins": user_data["coins"], "items": items_list})
    await message.reply(f"🎉 Куплено: **{item['name']}**!")

@dp.message(Command("inv"))
async def cmd_inv(message: types.Message):
    user_data = get_profile(message.from_user)
    items_list = user_data.get("items") or []
    if not items_list: await message.reply("🎒 Инвентарь пуст."); return
    await message.reply(f"🎒 **Инвентарь:**\n" + "\n".join([f"• {it}" for it in items_list]))

@dp.message(Command("pay"), F.reply_to_message)
async def cmd_pay(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit(): return
    amount = int(command.args)
    sender = get_profile(message.from_user)
    target_user = message.reply_to_message.from_user
    if target_user.id == message.from_user.id or target_user.is_bot or sender.get("coins", 0) < amount: return
    target_data = get_profile(target_user)
    sender["coins"] -= amount
    target_data["coins"] = target_data.get("coins", 0) + amount
    update_profile(sender["user_id"], {"coins": sender["coins"]})
    update_profile(target_data["user_id"], {"coins": target_data["coins"]})
    await message.answer(f"💸 Переведено `{amount}` 🪙 монет пользователю **{target_user.first_name}**!")

@dp.message(Command("me"))
async def cmd_me(message: types.Message):
    user_data = get_profile(message.from_user)
    available_levels = [lvl for lvl in LEVEL_TITLES.keys() if lvl <= user_data['level']]
    title = LEVEL_TITLES[max(available_levels)] if available_levels else "💡 Новичок"
    items = user_data.get("items") or []
    aura = "✨ [Премиум Аура] ✨\n" if "🎨 Премиум Рамка" in items else ""
    crown = "👑 " if "👑 Корона Чата" in items else ""
    admin_status = "🛡 **Администратор**\n" if is_admin(message.from_user) else ""
    partner_text = f"\n💍 Половинка: **{user_data.get('partner_name')}**" if user_data.get('partner_id') else ""
    
    text = (
        f"{aura}{admin_status}"
        f"👤 **Профиль: {crown}{user_data['name']}**\n\n"
        f"🪙 Баланс: `{user_data.get('coins', 0)}` монет\n"
        f"🏅 Уровень: **{user_data['level']}**\n"
        f"🎖 Титул: *{title}*\n"
        f"✨ Опыт: `{user_data['xp']}` XP\n"
        f"⚔ Побед: `{user_data['wins']}`{partner_text}"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    response = supabase.table("users").select("name, level, coins").order("coins", desc=True).limit(10).execute()
    if not response.data: return
    text = "🏆 **ТОП 10 БОГАТЕЕВ:**\n\n"
    for idx, u in enumerate(response.data, 1):
        text += f"{idx}. **{u['name']}** — `{u.get('coins', 0)}` 🪙 (Лвл {u['level']})\n"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("loot"))
async def cmd_loot(message: types.Message):
    user_data = get_profile(message.from_user)
    if time.time() - user_data['last_loot'] < 86400:
        await message.reply("⏱ Лут уже собран. Жди 24 часа.")
        return
    loot_xp, loot_coins = random.randint(10, 50), random.randint(50, 200)
    add_xp_and_coins(user_data, xp_amount=loot_xp, coins_amount=loot_coins)
    update_profile(user_data['user_id'], {"last_loot": time.time()})
    await message.reply(f"🎁 **Бокс открыт!** +{loot_xp} XP и +{loot_coins} 🪙 монет!")

@dp.message(Command("marry"), F.reply_to_message)
async def cmd_marry(message: types.Message):
    sender, target = message.from_user, message.reply_to_message.from_user
    if sender.id == target.id or target.is_bot: return
    marry_requests[target.id] = sender.id
    await message.answer(f"💍 **{sender.first_name}** делает предложение **{target.first_name}**! Ответь `согласен`.")

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
    await message.answer(f"🎉 **ПОЗДРАВЛЯЕМ!** **{sender_data['name']}** и **{target.first_name}** поженились! 💍")
    del marry_requests[target.id]

@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message):
    user_data = get_profile(message.from_user)
    p_id = user_data.get('partner_id')
    if not p_id: return
    update_profile(user_data['user_id'], {"partner_id": 0, "partner_name": ""})
    update_profile(p_id, {"partner_id": 0, "partner_name": ""})
    await message.reply("💔 Развод оформлен.")

@dp.message(Command("partner"))
async def cmd_partner(message: types.Message):
    p_name = get_profile(message.from_user).get('partner_name')
    await message.reply(f"💍 Половинка: **{p_name}**" if p_name else "💔 Нет пары.")

@dp.message(Command("duel"), F.reply_to_message)
async def cmd_duel(message: types.Message):
    challenger, target = message.from_user, message.reply_to_message.from_user
    if target.id == challenger.id or target.is_bot: return
    active_duels[target.id] = {'challenger_id': challenger.id, 'time': time.time()}
    await message.answer(f"⚔ **{challenger.first_name}** вызывает **{target.first_name}** на дуэль! Ответь `да` (60 сек).")

@dp.message(F.reply_to_message, F.text.lower() == "да")
async def handle_duel_accept(message: types.Message):
    target = message.from_user
    if target.id not in active_duels: return
    duel_data = active_duels[target.id]
    c_res = supabase.table("users").select("*").eq("user_id", duel_data['challenger_id']).execute()
    c_data = c_res.data[0] if c_res.data else get_profile(types.User(id=duel_data['challenger_id'], first_name="Игрок", is_bot=False))
    t_data = get_profile(target)
    
    c_bonus = (15 if "🛡 Щит Афины" in (c_data.get("items") or []) else 0) + (20 if "🗡 Меч Хаоса" in (c_data.get("items") or []) else 0)
    t_bonus = (15 if "🛡 Щит Афины" in (t_data.get("items") or []) else 0) + (20 if "🗡 Меч Хаоса" in (t_data.get("items") or []) else 0)
    c_chance = max(10, min(90, 50 + c_bonus - t_bonus))
    
    await asyncio.sleep(2)
    winner, loser_id = (c_data, t_data['user_id']) if random.randint(1, 100) <= c_chance else (t_data, c_data['user_id'])
    winner['wins'] = winner.get('wins', 0) + 1
    add_xp_and_coins(winner, xp_amount=35, coins_amount=100)
    update_profile(winner['user_id'], {"wins": winner['wins']})
    
    try:
        await bot.restrict_chat_member(message.chat.id, loser_id, permissions=types.ChatPermissions(can_send_messages=False), until_date=datetime.now() + timedelta(minutes=DUEL_MUTE_TIME))
        await message.answer(f"🏆 **{winner['name']}** побеждает (+35 XP, +100 🪙)! Проигравший в муте.")
    except TelegramBadRequest:
        await message.answer(f"🏆 **{winner['name']}** побеждает (+35 XP, +100 🪙)!")
    del active_duels[target.id]

@dp.message(Command("casino"))
async def cmd_casino(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit(): return
    bet = int(command.args)
    user_data = get_profile(message.from_user)
    if bet <= 0 or bet > user_data.get('coins', 0): return
    if random.randint(1, 100) <= 45:
        add_xp_and_coins(user_data, coins_amount=bet)
        await message.reply(f"🎰 Победа! +{bet} 🪙")
    else:
        add_xp_and_coins(user_data, coins_amount=-bet)
        await message.reply(f"🎰 Проигрыш! -{bet} 🪙")

@dp.message(Command("roulette"))
async def cmd_roulette(message: types.Message):
    user_data = get_profile(message.from_user)
    if random.randint(1, 6) == 1:
        try:
            await bot.restrict_chat_member(message.chat.id, message.from_user.id, permissions=types.ChatPermissions(can_send_messages=False), until_date=datetime.now() + timedelta(minutes=3))
            await message.reply("💥 Выстрел! Мут на 3 минуты.")
        except TelegramBadRequest:
            await message.reply("💥 Выстрел!")
    else:
        add_xp_and_coins(user_data, xp_amount=50, coins_amount=150)
        await message.reply("📊 Клик! +50 XP и +150 🪙!")

@dp.message(Command("ball"))
async def cmd_ball(message: types.Message, command: CommandObject):
    if not command.args: return
    await message.reply(f"🔮 {random.choice(BALL_ANSWERS)}")

# --- АДМИНСКИЕ КОМАНДЫ ---
@dp.message(Command("add_xp"), F.reply_to_message)
async def a_add_xp(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    add_xp_and_coins(get_profile(message.reply_to_message.from_user), xp_amount=int(command.args))
    await message.reply("🛡 Выдано XP.")

@dp.message(Command("remove_xp"), F.reply_to_message)
async def a_rem_xp(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    add_xp_and_coins(get_profile(message.reply_to_message.from_user), xp_amount=-int(command.args))
    await message.reply("🛡 Снято XP.")

@dp.message(Command("set_xp"), F.reply_to_message)
async def a_set_xp(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    u = get_profile(message.reply_to_message.from_user)
    u['xp'] = int(command.args)
    update_profile(u['user_id'], {"xp": u['xp']})
    await message.reply("🛡 XP установлены.")

@dp.message(Command("add_coins"), F.reply_to_message)
async def a_add_c(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    add_xp_and_coins(get_profile(message.reply_to_message.from_user), coins_amount=int(command.args))
    await message.reply("🛡 Выданы монеты.")

@dp.message(Command("remove_coins"), F.reply_to_message)
async def a_rem_c(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    add_xp_and_coins(get_profile(message.reply_to_message.from_user), coins_amount=-int(command.args))
    await message.reply("🛡 Сняты монеты.")

@dp.message(Command("set_coins"), F.reply_to_message)
async def a_set_c(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    u = get_profile(message.reply_to_message.from_user)
    u['coins'] = int(command.args)
    update_profile(u['user_id'], {"coins": u['coins']})
    await message.reply("🛡 Баланс установлен.")

@dp.message(Command("set_level"), F.reply_to_message)
async def a_set_l(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user) or not command.args or not command.args.isdigit(): return
    u = get_profile(message.reply_to_message.from_user)
    u['level'] = int(command.args)
    update_profile(u['user_id'], {"level": u['level']})
    await message.reply("🛡 Уровень установлен.")

@dp.message(Command("clear_inv"), F.reply_to_message)
async def a_clear_inv(message: types.Message):
    if not is_admin(message.from_user): return
    u = get_profile(message.reply_to_message.from_user)
    update_profile(u['user_id'], {"items": []})
    await message.reply("🛡 Инвентарь очищен.")

@dp.message(Command("reset_user"), F.reply_to_message)
async def a_reset(message: types.Message):
    if not is_admin(message.from_user): return
    update_profile(message.reply_to_message.from_user.id, {"xp": 0, "level": 1, "coins": 100, "items": [], "wins": 0, "partner_id": 0, "partner_name": ""})
    await message.reply("💥 Прогресс пользователя сброшен.")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_web(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    print("Бот и веб-сервер запущены...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
