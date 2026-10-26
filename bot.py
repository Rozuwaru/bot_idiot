import asyncio
import logging
import os
import random
import time
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAFO9wnwBz3capA6qcrZqyh5mlOOw9bc9bg"
SUPABASE_URL = "https://cbypocbgeevwqhjahchy.supabase.co"
SUPABASE_KEY = "sb_publishable_zcF4S765sEmvXLIQegRkFg_1el4gZn_".strip()

ADMIN_USERNAMES = {"p0tat0777"}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class FamilyState(StatesGroup):
    waiting_for_child_name = State()
    waiting_for_deposit_amount = State()

class ProfileState(StatesGroup):
    waiting_for_music = State()

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
INTIMATE_COOLDOWNS = {}
RACE_COOLDOWNS = {}

JOBS = {
    "1": {"name": "⛏ Шахтёр", "min_coins": 40, "max_coins": 90, "xp": 10},
    "2": {"name": "🛡 Стражник", "min_coins": 60, "max_coins": 130, "xp": 15},
    "3": {"name": "🧪 Алхимик", "min_coins": 90, "max_coins": 180, "xp": 22},
    "4": {"name": "🐉 Охотник на чудовищ", "min_coins": 130, "max_coins": 260, "xp": 30},
}

SHOP_EQUIPMENT = {
    "eq_1": {"name": "🪵 Деревянный меч", "price": 150, "duel_buff": 5, "desc": "Самодельное оружие. Дает +5% к победе в дуэли."},
    "eq_2": {"name": "⚔️ Железный меч", "price": 350, "duel_buff": 12, "desc": "Надежный клинок. Дает +12% к победе в дуэли."},
    "eq_3": {"name": "🛡 Кожаная броня", "price": 250, "duel_buff": 10, "desc": "Защита торса. Дает +10% к победе в дуэли."},
    "eq_4": {"name": "🛡 Мифриловый щит", "price": 1800, "duel_buff": 25, "desc": "Несокрушимая защита. Дает +25% к победе в дуэли."},
    "eq_5": {"name": "💍 Руническое кольцо", "price": 600, "duel_buff": 8, "desc": "Артефакт магов. Дает +8% к победе в дуэли."},
    "eq_6": {"name": "🔥 Пламенный клинок", "price": 1400, "duel_buff": 30, "desc": "Оружие дракоборцев. Дает +30% к победе в дуэли."},
    "eq_7": {"name": "👑 Корона победителя", "price": 5000, "duel_buff": 50, "desc": "Знак истинной власти. Дает +50% к победе в дуэли."},
}

SHOP_CONSUMABLES = {
    "beer_okhota": {"name": "🍺 Охота Крепкое", "price": 120, "desc": "Легендарное пиво. Мут на 2 мин + рандом монет."},
    "energy": {"name": "⚡ Энергетик", "price": 90, "desc": "Бодрящий напиток. Дает +50 XP."},
    "pizza": {"name": "🍔 Пицца", "price": 80, "desc": "Горячая сытная еда. Дает +30 XP и +20 монет."},
    "vodka": {"name": "🥃 Паленая водка", "price": 200, "desc": "Жесткий напиток. Мут на 5 мин и риск потерять/удвоить монеты."},
    "pc": {"name": "💻 Игровой ПК", "price": 3500, "desc": "Топовая сборка с RTX. Дает +150 респекта."},
    "cigars": {"name": "🚬 Сигареты", "price": 100, "desc": "Добавляет авторитета (+5 респекта) и никотиновую зависимость."},
    "hookah": {"name": "💨 Кальян", "price": 450, "desc": "Ароматный дым. Дает +80 XP."},
    "chips": {"name": "🍟 Чипсы с сыром", "price": 50, "desc": "Вкусный снек. Дает +15 XP."},
    "whiskey": {"name": "🥃 Элитный Виски", "price": 900, "desc": "Дорогой алкоголь. Дает +40 респекта."},
    "chair": {"name": "💺 Геймерское кресло", "price": 2200, "desc": "Эргономика. Дает +100 респекта."},
}

SEX_SHOP = {
    "sex_vibe": {"name": "🟣 Вибратор", "price": 800, "desc": "Мощная игрушка для ярких эмоций."},
    "sex_gag": {"name": "🔴 Кожаный кляп", "price": 500, "desc": "Чтобы стоны не мешали соседям."},
    "sex_cuff": {"name": "⛓️ Кожаные наручники", "price": 700, "desc": "Полный контроль над партнером."},
    "sex_maid": {"name": "👗 Костюм горничной", "price": 1000, "desc": "Соблазнительный наряд."},
    "sex_whip": {"name": "🖤 Кожаный хлыст", "price": 1200, "desc": "Добавляет перчинку в отношения."},
    "sex_oil": {"name": "🧴 Массажное масло", "price": 400, "desc": "Для безумно нежных касаний."},
    "sex_mask": {"name": "🎭 Кружевная маска", "price": 600, "desc": "Атмосфера тайного греха."},
}

CARS_CAT = {
    "granta": {"name": "🚗 Lada Granta", "price": 50000, "base_speed": 40},
    "vesta": {"name": "🚗 Lada Vesta", "price": 120000, "base_speed": 60},
    "rio": {"name": "🚗 Kia Rio", "price": 160000, "base_speed": 75},
    "solaris": {"name": "🚗 Hyundai Solaris", "price": 170000, "base_speed": 78},
    "octavia": {"name": "🚗 Skoda Octavia", "price": 250000, "base_speed": 95},
    "camry": {"name": "🚗 Toyota Camry", "price": 380000, "base_speed": 115},
    "m3": {"name": "🏎 BMW M3 E46", "price": 550000, "base_speed": 140},
    "w222": {"name": "🚘 Mercedes-Benz S-Class", "price": 900000, "base_speed": 160},
    "rs6": {"name": "🏎 Audi RS6 Avant", "price": 1250000, "base_speed": 190},
    "gtr": {"name": "🏎 Nissan GT-R R35", "price": 1600000, "base_speed": 220},
    "911": {"name": "🏎 Porsche 911 Turbo S", "price": 2200000, "base_speed": 250},
    "huracan": {"name": "🏎 Lamborghini Huracan", "price": 3000000, "base_speed": 285},
    "488": {"name": "🏎 Ferrari 488 Spider", "price": 3800000, "base_speed": 310},
    "chiron": {"name": "🏎 Bugatti Chiron", "price": 6000000, "base_speed": 360},
    "phantom": {"name": "👑 Rolls-Royce Phantom", "price": 8000000, "base_speed": 340},
    "m5f90": {"name": "🏎 BMW M5 F90", "price": 0, "base_speed": 340, "admin_only": True},
}

CAR_COLORS = [
    "🖤 Черный", "🤍 Белый", "🥈 Серебристый", "❤️ Красный", 
    "💙 Синий", "💛 Желтый", "💚 Зеленый", "💜 Фиолетовый"
]

APARTMENTS_CAT = {
    "studio": {"name": "🏢 Студия на окраине", "price": 50000},
    "1k": {"name": "🏢 1-комнатная квартира", "price": 120000},
    "3k": {"name": "🏢 3-комнатная в центре", "price": 350000},
    "penthouse": {"name": "🏢 Элитный пентхаус", "price": 1200000},
    "duplex": {"name": "🏢 Двухуровневые апартаменты", "price": 2500000},
}

HOUSES_CAT = {
    "dacha": {"name": "🏡 Дачный домик", "price": 200000},
    "cottage": {"name": "🏡 Загородный коттедж", "price": 800000},
    "villa": {"name": "🏡 Элитная вилла с бассейном", "price": 2000000},
    "estate": {"name": "🏰 Поместье с парком", "price": 5000000},
    "palace": {"name": "👑 Королевский особняк", "price": 10000000},
}

def format_age(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    res = []
    if days > 0:
        res.append(f"{days} дн.")
    if hours > 0 or days > 0:
        res.append(f"{hours} час.")
    res.append(f"{minutes} мин.")
    return " ".join(res) if res else "0 мин."

def is_admin(user: types.User) -> bool:
    if not user or not user.username:
        return False
    return user.username.lower() in {u.lower() for u in ADMIN_USERNAMES}

async def get_profile_by_id(uid: str):
    def _fetch():
        return supabase.table("users").select("*").eq("user_id", str(uid)).execute()
    try:
        res = await asyncio.to_thread(_fetch)
        if res.data:
            return res.data[0]
    except Exception as e:
        logging.error(f"Error fetching profile by id: {e}")
    return None

async def get_profile_by_username(username: str):
    uname = username.lstrip("@").lower()
    def _fetch():
        return supabase.table("users").select("*").ilike("username", uname).execute()
    try:
        res = await asyncio.to_thread(_fetch)
        if res.data:
            return res.data[0]
    except Exception as e:
        logging.error(f"Error fetching profile by username: {e}")
    return None

async def resolve_target_user(message: types.Message, args: list, identifier_index: int = 1):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        return str(target.id), target.first_name
    
    if len(args) > identifier_index:
        identifier = args[identifier_index].strip()
        if identifier.isdigit():
            p = await get_profile_by_id(identifier)
            if p:
                return str(p["user_id"]), p["username"]
            return identifier, f"ID:{identifier}"
        else:
            p = await get_profile_by_username(identifier)
            if p:
                return str(p["user_id"]), p["username"]
            return None, f"❌ Пользователь `{identifier}` не найден в базе данных!"
            
    return None, "❌ Укажите пользователя через ответ на сообщение, `@username` или `user_id`!"

async def get_profile(user: types.User):
    uid = str(user.id)
    now = int(time.time())
    def _fetch():
        return supabase.table("users").select("*").eq("user_id", uid).execute()
    try:
        response = await asyncio.to_thread(_fetch)
        if response.data:
            user_data = response.data[0]
            updates = {}
            if not user_data.get("created_at") or int(user_data.get("created_at", 0)) == 0:
                updates["created_at"] = now
                user_data["created_at"] = now
            if user_data.get("partner_id") and str(user_data.get("partner_id")) != "0":
                if not user_data.get("marriage_time") or int(user_data.get("marriage_time", 0)) == 0:
                    updates["marriage_time"] = now
                    user_data["marriage_time"] = now
            if updates:
                supabase.table("users").update(updates).eq("user_id", uid).execute()
            return user_data
    except Exception as e:
        logging.error(f"Supabase fetch error: {e}")

    new_user = {
        "user_id": uid,
        "username": user.username or user.first_name,
        "coins": 5000000, "xp": 0, "level": 1, "respect": 0,
        "partner_id": 0, "partner_name": "EMPTY",
        "inventory": "",
        "armory": "",
        "equipped_item": "",
        "personal_apartment": "❌ Нет",
        "personal_house": "❌ Нет",
        "smoking_level": 0,
        "last_smoke_time": 0,
        "created_at": now,
        "marriage_time": 0,
        "profile_music": ""
    }
    def _insert():
        return supabase.table("users").upsert(new_user).execute()
    try:
        res = await asyncio.to_thread(_insert)
        if res.data:
            return res.data[0]
    except Exception as e:
        logging.error(f"Supabase insert error: {e}")
    return new_user

def get_main_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data=f"menu_profile_{user_id}"),
         InlineKeyboardButton(text="🎒 Инвентарь", callback_data=f"menu_inv_{user_id}")],
        [InlineKeyboardButton(text="⚔️ Оружейная", callback_data=f"menu_armory_{user_id}"),
         InlineKeyboardButton(text="🏎 Гараж и Авто", callback_data=f"menu_garage_{user_id}")],
        [InlineKeyboardButton(text="🛒 Магазины", callback_data=f"menu_shops_{user_id}"),
         InlineKeyboardButton(text="🍑 Секс-шоп", callback_data=f"menu_sexshop_{user_id}")],
        [InlineKeyboardButton(text="🏠 Имущество", callback_data=f"menu_personal_{user_id}"),
         InlineKeyboardButton(text="🏆 Топ игроков", callback_data=f"menu_top_{user_id}")],
        [InlineKeyboardButton(text="💼 Биржа труда", callback_data=f"menu_work_{user_id}"),
         InlineKeyboardButton(text="🏁 Уличные гонки", callback_data=f"menu_race_{user_id}")],
        [InlineKeyboardButton(text="🎰 Казино и игры", callback_data=f"menu_casino_{user_id}"),
         InlineKeyboardButton(text="💍 Отношения и Семья", callback_data=f"menu_marry_{user_id}")]
    ])

@dp.message(Command(commands=["start", "help", "menu"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await get_profile(message.from_user)
    text = (
        f"👤 **Меню игрока: {message.from_user.first_name}**\n\n"
        "🎮 Добро пожаловать в RPG бот!\n"
        "Используйте кнопки ниже для управления персонажем, оружейной, казино, тюнинга и гонок."
    )
    await message.answer(text, reply_markup=get_main_keyboard(message.from_user.id), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("back_home_"))
async def callback_back_home(callback: types.CallbackQuery, state: FSMContext):
    uid_str = callback.data.split("_")[2]
    if str(callback.from_user.id) != uid_str:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    try:
        await state.clear()
        text = f"👤 **Меню игрока: {callback.from_user.first_name}**\n\n🎮 **ГЛАВНОЕ МЕНЮ:**"
        await callback.message.edit_text(text, reply_markup=get_main_keyboard(callback.from_user.id), parse_mode=ParseMode.MARKDOWN)
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("menu_"))
async def callback_main_menu(callback: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split("_")
        action = parts[1]
        owner_id = parts[2] if len(parts) > 2 else None
        
        if owner_id and str(callback.from_user.id) != owner_id:
            await callback.answer("❌ Это не ваше меню! Введите /start чтобы открыть свое.", show_alert=True)
            return

        await state.clear()
        p = await get_profile(callback.from_user)
        uid = callback.from_user.id
        
        if action == "profile":
            lvl = p.get('level', 1)
            title = LEVELS.get(lvl, {}).get("title", "Воин")
            pid, pname = p.get("partner_id"), p.get("partner_name")
            
            created_at = int(p.get("created_at") or time.time())
            bot_age = format_age(int(time.time()) - created_at)
            
            if pid and str(pid) != "0" and pname != "EMPTY":
                m_time = int(p.get("marriage_time") or time.time())
                marriage_duration = format_age(int(time.time()) - m_time)
                marriage = f"💍 В браке с: **{pname}** (уже {marriage_duration})"
            else:
                marriage = "💍 Статус: Свободен"

            smoke_lvl = p.get('smoking_level', 0)
            smoke_status = f"🚬 Никотиновая зависимость: Уровень `{smoke_lvl}`" if smoke_lvl > 0 else "🚭 Не курит"
            equipped = p.get("equipped_item", "")
            eq_name = SHOP_EQUIPMENT.get(equipped, {}).get("name", "❌ Ничего не надето")
            music_status = "🎵 Установлена" if p.get("profile_music") else "❌ Нет"
            
            def _get_car_and_prop():
                car_res = supabase.table("user_cars").select("*").eq("user_id", str(uid)).eq("is_active", True).execute()
                active_car = car_res.data[0] if car_res.data else None
                return active_car
            active_car = await asyncio.to_thread(_get_car_and_prop)
            car_info = f"🚗 Машина: **{active_car['car_name']}** ({active_car['color']})" if active_car else "🚗 Машина: ❌ Нет"
            apt_info = f"🏢 Квартира: `{p.get('personal_apartment', '❌ Нет')}`"
            house_info = f"🏡 Дом: `{p.get('personal_house', '❌ Нет')}`"
            
            text = (
                f"👤 **Профиль: {p.get('username')}**\n"
                f"⏳ Возраст в боте: `{bot_age}`\n"
                f"⭐ Уровень: `{lvl}` / 67 (*{title}*)\n"
                f"✨ Опыт (XP): `{p.get('xp')}`\n"
                f"🪙 Монеты: `{p.get('coins'):,}`\n"
                f"❤️ Респект: `{p.get('respect')}`\n"
                f"{car_info}\n"
                f"{apt_info}\n"
                f"{house_info}\n"
                f"⚔️ Экипировка: `{eq_name}`\n"
                f"🎶 Музыка в профиле: `{music_status}`\n"
                f"{smoke_status}\n"
                f"{marriage}"
            )
            
            kb_buttons = [
                [InlineKeyboardButton(text="🎵 Музыка профиля", callback_data=f"profile_music_menu_{uid}")]
            ]
            if p.get("profile_music"):
                kb_buttons.append([InlineKeyboardButton(text="🎧 Прослушать музыку", callback_data=f"play_music_{uid}")])
            
            kb_buttons.extend([
                [InlineKeyboardButton(text="🔄 Обновить", callback_data=f"menu_profile_{uid}"),
                 InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer("🔄 Профиль уже актуален!")
                return

        elif action == "armory":
            armory_str = p.get("armory") or ""
            arm_items = [i.strip() for i in armory_str.split(",") if i.strip()]
            equipped = p.get("equipped_item", "")
            
            text = f"⚔️ **ОРУЖЕЙНАЯ ИГРОКА {p.get('username')}** (Баланс: `{p.get('coins', 0):,}` 🪙)\n\n"
            eq_info = SHOP_EQUIPMENT.get(equipped)
            if eq_info:
                text += f"🟢 **Надето:** {eq_info['name']} (*+{eq_info['duel_buff']}% к дуэли*)\n\n"
            else:
                text += "🟢 **Надето:** Ничего\n\n"
                
            if not arm_items:
                text += "В вашей оружейной пока пусто. Купите оружие или броню в магазине снаряжения!"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⚔️ Купить снаряжение", callback_data=f"shop_eq_list_{uid}")],
                    [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            else:
                text += "Выберите предмет, чтобы надеть его:"
                buttons = []
                for idx, eq_key in enumerate(arm_items):
                    eq_data = SHOP_EQUIPMENT.get(eq_key, {"name": eq_key})
                    is_eq = " [НАДЕТО]" if equipped == eq_key else ""
                    buttons.append([InlineKeyboardButton(text=f"⚔️ Надеть: {eq_data['name']}{is_eq}", callback_data=f"equip_item_{idx}_{eq_key}")])
                if equipped:
                    buttons.append([InlineKeyboardButton(text="🛑 Снять экипировку", callback_data=f"unequip_item_{uid}")])
                buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
                kb = InlineKeyboardMarkup(inline_keyboard=buttons)
                
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "inv":
            inv_str = p.get("inventory") or ""
            items = [i.strip() for i in inv_str.split(",") if i.strip()]
            
            if not items:
                text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\nВаш инвентарь пуст."
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]])
            else:
                text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p.get('coins', 0):,}` 🪙):\nНажмите на предмет, чтобы использовать его:\n\n"
                buttons = []
                for idx, item_key in enumerate(items):
                    item_info = SHOP_CONSUMABLES.get(item_key) or SEX_SHOP.get(item_key) or {"name": item_key}
                    buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {item_info['name']}", callback_data=f"use_item_{idx}_{item_key}")])
                buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
                kb = InlineKeyboardMarkup(inline_keyboard=buttons)
                
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "garage":
            def _get_cars():
                return supabase.table("user_cars").select("*").eq("user_id", str(uid)).execute()
            cars_res = await asyncio.to_thread(_get_cars)
            user_cars = cars_res.data if cars_res and cars_res.data else []

            text = f"🏎 **ВАШ ГАРАЖ И АВТОМОБИЛИ** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\n"
            buttons = []

            if not user_cars:
                text += "У вас пока нет машин. Купите их в автосалоне!"
            else:
                for car in user_cars:
                    active_mark = "🟢 [АКТИВНА]" if car['is_active'] else ""
                    text += f"🚗 **{car['car_name']}** | {car['color']} {active_mark}\n"
                    text += f"   └ Двиг: Ур.{car['engine_lvl']} | Турбо: Ур.{car['turbo_lvl']} | Управл: Ур.{car['handling_lvl']}\n\n"
                    if not car['is_active']:
                        buttons.append([InlineKeyboardButton(text=f"🔑 Сесть за руль: {car['car_name']}", callback_data=f"car_activate_{car['id']}")])
                    buttons.append([InlineKeyboardButton(text=f"⚙️ Тюнинг / Покраска: {car['car_name']}", callback_data=f"car_tune_{car['id']}")])

            buttons.append([InlineKeyboardButton(text="🛍 Автосалон (Купить авто)", callback_data=f"shop_cars_list_{uid}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "race":
            def _get_active():
                return supabase.table("user_cars").select("*").eq("user_id", str(uid)).eq("is_active", True).execute()
            active_res = await asyncio.to_thread(_get_active)
            active_car = active_res.data[0] if active_res and active_res.data else None

            text = "🏁 **УЛИЧНЫЕ ГОНКИ (PvP между игроками)**\n\n"
            if not active_car:
                text += "❌ У вас нет активной машины! Выберите машину в гараже."
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏎 Перейти в гараж", callback_data=f"menu_garage_{uid}")],
                    [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            else:
                text += (
                    f"🏎 Ваша машина: **{active_car['car_name']}** ({active_car['color']})\n"
                    f"⚡ Тюнинг (Двиг {active_car['engine_lvl']} | Турбо {active_car['turbo_lvl']} | Руль {active_car['handling_lvl']})\n\n"
                    f"🏆 Гонки проходят против машин других реальных игроков! Ставка: 1,000 🪙."
                )
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔥 Начать заезд с игроком (1,000 🪙)", callback_data="start_street_race")],
                    [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "shops":
            text = f"🛒 **ВЫБЕРИТЕ МАГАЗИН** (Баланс: `{p.get('coins', 0):,}` 🪙):"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏎 Автосалон (Все модели)", callback_data=f"shop_cars_list_{uid}")],
                [InlineKeyboardButton(text="⚔️ Снаряжение (в Оружейную)", callback_data=f"shop_eq_list_{uid}")],
                [InlineKeyboardButton(text="🍺 Продукты и ПК (в инвентарь)", callback_data=f"shop_cons_list_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "sexshop":
            text = f"🍑 **СЕКС-ШОП «БЕЗ ТОРМОЗОВ»** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\nПриобретайте игрушки, они попадают в инвентарь:"
            buttons = []
            for item_id, data in SEX_SHOP.items():
                buttons.append([InlineKeyboardButton(text=f"{data['name']} — {data['price']:,} 🪙", callback_data=f"buy_sex_{item_id}_{uid}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            try:
                await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "personal":
            text = (
                f"🏠 **ЛИЧНОЕ ИМУЩЕСТВО** (Баланс: `{p.get('coins', 0):,}` 🪙)\n\n"
                f"🏢 Квартира: `{p.get('personal_apartment', '❌ Нет')}`\n"
                f"🏡 Дом: `{p.get('personal_house', '❌ Нет')}`\n\n"
                f"👇 Выберите категорию для покупки:"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏢 Купить квартиру", callback_data=f"pers_shop_apt_{uid}"),
                 InlineKeyboardButton(text="🏡 Купить дом", callback_data=f"pers_shop_house_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        elif action == "top":
            def _fetch_top():
                return supabase.table("users").select("user_id, username, level, coins").order("level", desc=True).limit(10).execute()
            try:
                res = await asyncio.to_thread(_fetch_top)
            except Exception:
                res = None
            text = "🏆 **ТОП-10 ИГРОКОВ:**\nНажмите на игрока, чтобы посмотреть его профиль:\n\n"
            buttons = []
            if res and res.data:
                for i, u in enumerate(res.data, 1):
                    lvl = u.get('level', 1)
                    title = LEVELS.get(lvl, {}).get("title", "")
                    text += f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙 `{u.get('coins'):,}`\n"
                    buttons.append([InlineKeyboardButton(text=f"👤 Профиль: {u.get('username')}", callback_data=f"view_profile_{u.get('user_id')}")])
            else:
                text += "Игроков пока нет."
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        elif action == "work":
            text = f"💼 **БИРЖА ТРУДА** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\nВыберите смену:"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⛏ Шахтёр (40-90 🪙)", callback_data="do_work_1")],
                [InlineKeyboardButton(text="🛡 Стражник (60-130 🪙)", callback_data="do_work_2")],
                [InlineKeyboardButton(text="🧪 Алхимик (90-180 🪙)", callback_data="do_work_3")],
                [InlineKeyboardButton(text="🐉 Охотник (130-260 🪙)", callback_data="do_work_4")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        elif action == "casino":
            text = (
                f"🎰 **КАЗИНО И ИГРЫ** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\n"
                "Доступные игры в чате:\n"
                "• `/dice <ставка> <числа 1-6>`\n"
                "• `/coin <ставка> <орел/решка>`\n"
                "• `/slots <ставка>`\n"
                "• `/duel` (Дуэль с экипировкой)\n\n"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 Комбинации слотов", callback_data=f"slots_help_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        elif action == "marry":
            pid, pname = p.get("partner_id"), p.get("partner_name")
            if pid and str(pid) != "0" and pname != "EMPTY":
                m_time = int(p.get("marriage_time") or time.time())
                md = format_age(int(time.time()) - m_time)
                text = f"💍 **СЕМЕЙНЫЙ ОЧАГ:**\n\n💍 В браке с: **{pname}**\n⏳ Длительность брака: `{md}`"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏡 Меню семьи", callback_data="family_main"),
                     InlineKeyboardButton(text="🍑 Уединиться (/sex)", callback_data="action_sex_menu")],
                    [InlineKeyboardButton(text="💔 Развестись (/divorce)", callback_data="action_divorce"),
                     InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            else:
                text = f"💍 **ОТНОШЕНИЯ И СЕМЬЯ:**\n\n💍 Вы свободны. Сделайте предложение через реплай и `/marry`"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in callback_main_menu: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

# --- ПРОСМОТР ЧУЖОГО ПРОФИЛЯ ---
@dp.callback_query(F.data.startswith("view_profile_"))
async def view_other_profile(callback: types.CallbackQuery):
    target_uid = callback.data.split("_")[2]
    p = await get_profile_by_id(target_uid)
    if not p:
        await callback.answer("❌ Профиль не найден!", show_alert=True)
        return

    lvl = p.get('level', 1)
    title = LEVELS.get(lvl, {}).get("title", "Воин")
    pid, pname = p.get("partner_id"), p.get("partner_name")
    
    created_at = int(p.get("created_at") or time.time())
    bot_age = format_age(int(time.time()) - created_at)
    
    if pid and str(pid) != "0" and pname != "EMPTY":
        m_time = int(p.get("marriage_time") or time.time())
        marriage_duration = format_age(int(time.time()) - m_time)
        marriage = f"💍 В браке с: **{pname}** (уже {marriage_duration})"
    else:
        marriage = "💍 Статус: Свободен"

    smoke_lvl = p.get('smoking_level', 0)
    smoke_status = f"🚬 Никотиновая зависимость: Уровень `{smoke_lvl}`" if smoke_lvl > 0 else "🚭 Не курит"
    equipped = p.get("equipped_item", "")
    eq_name = SHOP_EQUIPMENT.get(equipped, {}).get("name", "❌ Ничего не надето")
    music_status = "🎵 Установлена" if p.get("profile_music") else "❌ Нет"

    def _get_car_and_prop():
        car_res = supabase.table("user_cars").select("*").eq("user_id", str(target_uid)).eq("is_active", True).execute()
        active_car = car_res.data[0] if car_res.data else None
        return active_car
    active_car = await asyncio.to_thread(_get_car_and_prop)
    car_info = f"🚗 Машина: **{active_car['car_name']}** ({active_car['color']})" if active_car else "🚗 Машина: ❌ Нет"
    apt_info = f"🏢 Квартира: `{p.get('personal_apartment', '❌ Нет')}`"
    house_info = f"🏡 Дом: `{p.get('personal_house', '❌ Нет')}`"

    text = (
        f"👤 **Профиль игрока: {p.get('username')}** (Просмотр)\n"
        f"⏳ Возраст в боте: `{bot_age}`\n"
        f"⭐ Уровень: `{lvl}` / 67 (*{title}*)\n"
        f"✨ Опыт (XP): `{p.get('xp')}`\n"
        f"🪙 Монеты: `{p.get('coins'):,}`\n"
        f"❤️ Респект: `{p.get('respect')}`\n"
        f"{car_info}\n"
        f"{apt_info}\n"
        f"{house_info}\n"
        f"⚔️ Экипировка: `{eq_name}`\n"
        f"🎶 Музыка в профиле: `{music_status}`\n"
        f"{smoke_status}\n"
        f"{marriage}"
    )

    buttons = []
    if p.get("profile_music"):
        buttons.append([InlineKeyboardButton(text="🎧 Прослушать музыку", callback_data=f"play_music_{target_uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в меню", callback_data=f"back_home_{callback.from_user.id}")])

    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

# --- МУЗЫКА В ПРОФИЛЕ ---
@dp.callback_query(F.data.startswith("profile_music_menu_"))
async def profile_music_menu(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    has_music = bool(p.get("profile_music"))
    
    text = (
        f"🎵 **МУЗЫКА В ПРОФИЛЕ**\n\n"
        f"Здесь вы можете установить аудиозапись или песню, которая будет привязана к вашему профилю.\n"
        f"Статус: `{'Установлена' if has_music else 'Отсутствует'}`"
    )
    buttons = [
        [InlineKeyboardButton(text="📥 Установить / Изменить музыку", callback_data=f"set_music_prompt_{uid}")]
    ]
    if has_music:
        buttons.append([InlineKeyboardButton(text="🎧 Прослушать текущую", callback_data=f"play_music_{uid}")])
        buttons.append([InlineKeyboardButton(text="❌ Удалить музыку", callback_data=f"del_music_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в профиль", callback_data=f"menu_profile_{uid}")])
    
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

@dp.callback_query(F.data.startswith("set_music_prompt_"))
async def set_music_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    await state.set_state(ProfileState.waiting_for_music)
    try:
        await callback.message.edit_text(
            "🎵 **УСТАНОВКА МУЗЫКИ В ПРОФИЛЬ**\n\nОтправьте в этот чат любой аудиофайл или музыку из Telegram следующим сообщением:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"profile_music_menu_{uid}")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

@dp.message(ProfileState.waiting_for_music, F.audio)
async def save_profile_music(message: types.Message, state: FSMContext):
    file_id = message.audio.file_id
    uid = str(message.from_user.id)
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"profile_music": file_id}).eq("user_id", uid).execute())
    except Exception as e:
        logging.error(f"Error saving profile music: {e}")
    await state.clear()
    await message.answer(
        "✅ Музыка успешно установлена в ваш профиль!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 В профиль", callback_data=f"menu_profile_{uid}")]
        ])
    )

@dp.message(ProfileState.waiting_for_music)
async def not_audio_music(message: types.Message):
    await message.answer("❌ Пожалуйста, отправьте именно **аудиофайл** или музыку из Telegram:")

@dp.callback_query(F.data.startswith("play_music_"))
async def play_profile_music(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    target_uid = parts[2]
    p = await get_profile_by_id(target_uid)
    if p and p.get("profile_music"):
        file_id = p["profile_music"]
        uname = p["username"]
        await callback.message.answer_audio(audio=file_id, caption=f"🎵 Музыка из профиля игрока {uname}")
        await callback.answer("🎶 Воспроизведение...")
    else:
        await callback.answer("❌ У этого игрока не установлена музыка в профиле!", show_alert=True)

@dp.callback_query(F.data.startswith("del_music_"))
async def delete_profile_music(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.data.split("_")[2]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"profile_music": ""}).eq("user_id", uid).execute())
    except Exception:
        pass
    await callback.answer("🗑 Музыка удалена из профиля.", show_alert=True)
    callback.data = f"menu_profile_{uid}"
    await callback_main_menu(callback, state)

# --- АВТОСАЛОН И ТЮНИНГ ---
@dp.callback_query(F.data.startswith("shop_cars_list_"))
async def shop_cars_list(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    text = f"🏎 **АВТОСАЛОН** (Баланс: `{p.get('coins', 0):,}` 🪙):\nВыберите машину для покупки:\n\n"
    buttons = []
    for k, car in CARS_CAT.items():
        if car.get("admin_only"):
            text += f"• **{car['name']}** — 🔒 *Эксклюзив (Только от админа)* (Скорость: {car['base_speed']})\n"
        else:
            text += f"• **{car['name']}** — `{car['price']:,}` 🪙 (Скорость: {car['base_speed']})\n"
            buttons.append([InlineKeyboardButton(text=f"Купить: {car['name']} ({car['price']:,} 🪙)", callback_data=f"buy_car_{k}_{uid}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 В гараж", callback_data=f"menu_garage_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_car_"))
async def buy_car_action(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_key = parts[2]
    uid = parts[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    car_info = CARS_CAT.get(car_key)
    if not car_info or car_info.get("admin_only"):
        await callback.answer("❌ Эту машину нельзя купить в автосалоне!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < car_info["price"]:
        await callback.answer(f"❌ Недостаточно монет! Нужно {car_info['price']:,} 🪙", show_alert=True)
        return

    new_coins = p["coins"] - car_info["price"]

    def _check_cars():
        return supabase.table("user_cars").select("*").eq("user_id", str(uid)).execute()
    existing = await asyncio.to_thread(_check_cars)
    is_first = not existing.data

    def _insert_car():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", str(uid)).execute()
        supabase.table("user_cars").insert({
            "user_id": str(uid),
            "car_key": car_key,
            "car_name": car_info["name"],
            "color": "🖤 Черный",
            "engine_lvl": 1,
            "turbo_lvl": 1,
            "handling_lvl": 1,
            "is_active": is_first
        }).execute()
    await asyncio.to_thread(_insert_car)

    await callback.answer(f"🎉 Вы успешно купили {car_info['name']}!", show_alert=True)
    callback.data = f"menu_garage_{uid}"
    await callback_main_menu(callback, None)

@dp.callback_query(F.data.startswith("car_activate_"))
async def car_activate(callback: types.CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    uid = str(callback.from_user.id)

    def _set_active():
        supabase.table("user_cars").update({"is_active": False}).eq("user_id", uid).execute()
        supabase.table("user_cars").update({"is_active": True}).eq("id", car_id).execute()
    await asyncio.to_thread(_set_active)

    await callback.answer("🔑 Машина выбрана в качестве основной!", show_alert=True)
    callback.data = f"menu_garage_{uid}"
    await callback_main_menu(callback, None)

@dp.callback_query(F.data.startswith("car_tune_"))
async def car_tune_menu(callback: types.CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    def _get_car():
        return supabase.table("user_cars").select("*").eq("id", car_id).execute()
    res = await asyncio.to_thread(_get_car)
    if not res.data:
        await callback.answer("❌ Машина не найдена!", show_alert=True)
        return
    car = res.data[0]
    p = await get_profile(callback.from_user)

    engine_cost = car["engine_lvl"] * 20000
    turbo_cost = car["turbo_lvl"] * 35000
    handling_cost = car["handling_lvl"] * 15000

    text = (
        f"⚙️ **ТЮНИНГ И ПОКРАСКА: {car['car_name']}**\n"
        f"🎨 Текущий цвет: {car['color']}\n"
        f"🪙 Ваш баланс: `{p.get('coins', 0):,}` 🪙\n\n"
        f"🔹 Двигатель (Ур. {car['engine_lvl']}) — ` апгрейд: {engine_cost:,} 🪙`\n"
        f"🔸 Турбина (Ур. {car['turbo_lvl']}) — `⚡ апгрейд: {turbo_cost:,} 🪙`\n"
        f"🟢 Подвеска (Ур. {car['handling_lvl']}) — `🛡 апгрейд: {handling_cost:,} 🪙`\n"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⬆️ Улучшить Двигатель ({engine_cost:,} 🪙)", callback_data=f"up_car_{car_id}_engine")],
        [InlineKeyboardButton(text=f"⬆️ Улучшить Турбину ({turbo_cost:,} 🪙)", callback_data=f"up_car_{car_id}_turbo")],
        [InlineKeyboardButton(text=f"⬆️ Улучшить Руль ({handling_cost:,} 🪙)", callback_data=f"up_car_{car_id}_handling")],
        [InlineKeyboardButton(text="🎨 Выбрать цвет покраски (8 цветов)", callback_data=f"paint_car_menu_{car_id}")],
        [InlineKeyboardButton(text="🔙 В гараж", callback_data=f"menu_garage_{callback.from_user.id}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("up_car_"))
async def upgrade_car_part(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    part = parts[3]

    def _get_car():
        return supabase.table("user_cars").select("*").eq("id", car_id).execute()
    res = await asyncio.to_thread(_get_car)
    if not res.data:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    car = res.data[0]
    p = await get_profile(callback.from_user)

    costs = {
        "engine": car["engine_lvl"] * 20000,
        "turbo": car["turbo_lvl"] * 35000,
        "handling": car["handling_lvl"] * 15000
    }
    cost = costs[part]

    if p.get("coins", 0) < cost:
        await callback.answer(f"❌ Недостаточно монет! Нужно {cost:,} 🪙", show_alert=True)
        return

    new_coins = p["coins"] - cost
    col_map = {"engine": "engine_lvl", "turbo": "turbo_lvl", "handling": "handling_lvl"}
    new_lvl = car[col_map[part]] + 1

    def _update():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", str(p["user_id"])).execute()
        supabase.table("user_cars").update({col_map[part]: new_lvl}).eq("id", car_id).execute()
    await asyncio.to_thread(_update)

    await callback.answer("✅ Улучшение успешно установлено!", show_alert=True)
    callback.data = f"car_tune_{car_id}"
    await car_tune_menu(callback)

@dp.callback_query(F.data.startswith("paint_car_menu_"))
async def paint_car_menu(callback: types.CallbackQuery):
    car_id = int(callback.data.split("_")[3] if len(callback.data.split("_")) > 3 else callback.data.split("_")[2])
    buttons = []
    for color in CAR_COLORS:
        buttons.append([InlineKeyboardButton(text=f"🎨 {color}", callback_data=f"set_color_{car_id}_{color}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к тюнингу", callback_data=f"car_tune_{car_id}")])

    try:
        await callback.message.edit_text("🎨 **ВЫБЕРИТЕ ЦВЕТ ДЛЯ ПОКРАСКИ МАШИНЫ:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("set_color_"))
async def set_car_color(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    color = "_".join(parts[3:])

    def _update_color():
        supabase.table("user_cars").update({"color": color}).eq("id", car_id).execute()
    await asyncio.to_thread(_update_color)

    await callback.answer(f"🎨 Машина перекрашена в {color}!", show_alert=True)
    callback.data = f"car_tune_{car_id}"
    await car_tune_menu(callback)

# --- УЛИЧНЫЕ ГОНКИ МЕЖДУ РЕАЛЬНЫМИ ИГРОКАМИ ---
@dp.callback_query(F.data == "start_street_race")
async def start_street_race(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    now = time.time()
    if now - RACE_COOLDOWNS.get(uid, 0) < 30:
        rem = int(30 - (now - RACE_COOLDOWNS.get(uid, 0)))
        await callback.answer(f"⏳ Ваша машина остывает после гонки. Подождите {rem} сек.", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < 1000:
        await callback.answer("❌ Для участия в заезде нужно минимум 1,000 🪙!", show_alert=True)
        return

    def _get_active():
        return supabase.table("user_cars").select("*").eq("user_id", uid).eq("is_active", True).execute()
    res = await asyncio.to_thread(_get_active)
    if not res.data:
        await callback.answer("❌ У вас нет активной машины! Выберите машину в гараже.", show_alert=True)
        return
    my_car = res.data[0]

    def _get_opponents():
        return supabase.table("user_cars").select("*").eq("is_active", True).neq("user_id", uid).execute()
    opp_res = await asyncio.to_thread(_get_opponents)

    if not opp_res.data:
        await callback.answer("❌ Сейчас нет других игроков с активными машинами в сети! Пригласите друзей в бота.", show_alert=True)
        return

    opponent_car = random.choice(opp_res.data)

    def _get_opp_user():
        return supabase.table("users").select("username").eq("user_id", opponent_car["user_id"]).execute()
    opp_user_res = await asyncio.to_thread(_get_opp_user)
    opp_username = opp_user_res.data[0]["username"] if opp_user_res.data else "Игрок"

    RACE_COOLDOWNS[uid] = now

    my_base = CARS_CAT.get(my_car["car_key"], {}).get("base_speed", 50)
    my_power = my_base + (my_car["engine_lvl"] * 15) + (my_car["turbo_lvl"] * 25) + (my_car["handling_lvl"] * 10)

    opp_base = CARS_CAT.get(opponent_car["car_key"], {}).get("base_speed", 50)
    opp_power = opp_base + (opponent_car["engine_lvl"] * 15) + (opponent_car["turbo_lvl"] * 25) + (opponent_car["handling_lvl"] * 10)

    win = my_power >= opp_power

    if win:
        reward = random.randint(2000, 6000)
        xp_gain = 40
        new_coins = p["coins"] - 1000 + reward
        new_xp = p.get("xp", 0) + xp_gain
        result_text = (
            f"🏁 **ПОБЕДА В ГОНКЕ ПРОТИВ ИГРОКА!** 🎉\n\n"
            f"🏎 Ваша машина: **{my_car['car_name']}** ({my_car['color']})\n"
            f"🚗 Соперник (**{opp_username}**): **{opponent_car['car_name']}** ({opponent_car['color']})\n\n"
            f"💰 Выигрыш: `+{reward:,}` 🪙\n"
            f"✨ Опыт: `+{xp_gain} XP`"
        )
    else:
        new_coins = p["coins"] - 1000
        new_xp = p.get("xp", 0) + 10
        result_text = (
            f"🏁 **ПОРАЖЕНИЕ В ГОНКЕ...** 💨\n\n"
            f"🏎 Ваша машина: **{my_car['car_name']}** ({my_car['color']})\n"
            f"🚗 Соперник (**{opp_username}**): **{opponent_car['car_name']}** ({opponent_car['color']})\n\n"
            f"💸 Ставка сгорела: `-1,000 🪙`\n"
            f"✨ Опыт утешения: `+10 XP`"
        )

    new_level = p.get("level", 1)
    for lvl, d in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= d["xp"]: new_level = lvl

    def _save():
        supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute()
    await asyncio.to_thread(_save)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏁 Еще гонка с игроком", callback_data="start_street_race")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
    ])
    try:
        await callback.message.edit_text(result_text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

# --- МАГАЗИНЫ И ИМУЩЕСТВО ---
@dp.callback_query(F.data.startswith("shop_eq_list_"))
async def callback_shop_eq(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    p = await get_profile(callback.from_user)
    text = f"⚔️ **МАГАЗИН СНАРЯЖЕНИЯ** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\n"
    buttons = []
    for item_id, data in SHOP_EQUIPMENT.items():
        text += f"🔹 **{data['name']}** ({data['price']:,} 🪙)\n   └ *{data['desc']}*\n\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']}", callback_data=f"buy_eq_{item_id}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data=f"menu_shops_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

@dp.callback_query(F.data.startswith("shop_cons_list_"))
async def callback_shop_cons(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    p = await get_profile(callback.from_user)
    text = f"🍺 **ПРОДУКТЫ И ТЕХНИКА** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\n"
    buttons = []
    for item_id, data in SHOP_CONSUMABLES.items():
        text += f"🔹 **{data['name']}** ({data['price']:,} 🪙)\n   └ *{data['desc']}*\n\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']}", callback_data=f"buy_cons_{item_id}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data=f"menu_shops_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_eq_"))
async def callback_buy_eq(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    item_id = f"{parts[2]}_{parts[3]}"
    uid = parts[4]
    item = SHOP_EQUIPMENT[item_id]
    p = await get_profile(callback.from_user)
    
    if p.get("coins", 0) < item["price"]:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
        
    new_coins = p["coins"] - item["price"]
    armory_str = p.get("armory") or ""
    updated_armory = f"{armory_str},{item_id}" if armory_str else item_id
    
    def _upd():
        supabase.table("users").update({"coins": new_coins, "armory": updated_armory}).eq("user_id", str(uid)).execute()
    await asyncio.to_thread(_upd)
        
    await callback.answer(f"✅ {item['name']} добавлен в Оружейную!", show_alert=True)
    callback.data = f"menu_armory_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("buy_cons_"))
async def callback_buy_cons(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    uid = parts[-1]
    item_key = "_".join(parts[2:-1])
    item = SHOP_CONSUMABLES[item_key]
    p = await get_profile(callback.from_user)
    
    if p.get("coins", 0) < item["price"]:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
        
    new_coins = p["coins"] - item["price"]
    current_inv = p.get("inventory") or ""
    updated_inv = f"{current_inv},{item_key}" if current_inv else item_key
    
    def _upd():
        supabase.table("users").update({"coins": new_coins, "inventory": updated_inv}).eq("user_id", str(uid)).execute()
    await asyncio.to_thread(_upd)
        
    await callback.answer(f"✅ {item['name']} добавлен в инвентарь!", show_alert=True)
    callback.data = f"menu_shops_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("buy_sex_"))
async def buy_sex_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    uid = parts[-1]
    item_key = "_".join(parts[2:-1])
    item = SEX_SHOP[item_key]
    p = await get_profile(callback.from_user)
    
    if p.get("coins", 0) < item["price"]:
        await callback.answer(f"❌ Недостаточно монет! Нужно {item['price']:,} 🪙", show_alert=True)
        return
        
    new_coins = p["coins"] - item["price"]
    current_inv = p.get("inventory") or ""
    updated_inv = f"{current_inv},{item_key}" if current_inv else item_key
    
    def _upd():
        supabase.table("users").update({"coins": new_coins, "inventory": updated_inv}).eq("user_id", str(uid)).execute()
    await asyncio.to_thread(_upd)
        
    await callback.answer(f"🍑 Успешно куплено: {item['name']}!", show_alert=True)
    callback.data = f"menu_sexshop_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("pers_shop_apt_"))
async def pers_shop_apt(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    p = await get_profile(callback.from_user)
    buttons = []
    for k, v in APARTMENTS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']:,} 🪙", callback_data=f"pers_buy_apt_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    try:
        await callback.message.edit_text(f"🏢 **РЫНОК КВАРТИР** (Баланс: `{p.get('coins', 0):,}` 🪙):\nВыберите вариант:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("pers_shop_house_"))
async def pers_shop_house(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    p = await get_profile(callback.from_user)
    buttons = []
    for k, v in HOUSES_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']:,} 🪙", callback_data=f"pers_buy_house_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    try:
        await callback.message.edit_text(f"🏡 **РЫНОК ДОМОВ** (Баланс: `{p.get('coins', 0):,}` 🪙):\nВыберите вариант:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("pers_buy_"))
async def pers_buy_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    category = parts[2] 
    item_key = parts[3] 
    uid = parts[4]
    
    p = await get_profile(callback.from_user)
    item_data = {}
    col_name = ""
    if category == "apt":
        item_data = APARTMENTS_CAT[item_key]
        col_name = "personal_apartment"
    elif category == "house":
        item_data = HOUSES_CAT[item_key]
        col_name = "personal_house"
        
    if p.get("coins", 0) < item_data["price"]:
        await callback.answer(f"❌ Недостаточно монет! Нужно {item_data['price']:,} 🪙", show_alert=True)
        return
        
    new_coins = p["coins"] - item_data["price"]
    def _buy():
        supabase.table("users").update({"coins": new_coins, col_name: item_data["name"]}).eq("user_id", str(uid)).execute()
    await asyncio.to_thread(_buy)
    
    await callback.answer(f"🎉 Успешно куплено: {item_data['name']}!", show_alert=True)
    callback.data = f"menu_personal_{uid}"
    await callback_main_menu(callback, state)

# --- БИРЖА ТРУДА И КАЗИНО ---
@dp.message(Command("work"))
async def cmd_work(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    now = time.time()
    if now - WORK_COOLDOWNS.get(uid, 0) < 60:
        await message.answer(f"⏳ Отдохните еще `{int(60 - (now - WORK_COOLDOWNS.get(uid, 0)))}` сек.", parse_mode=ParseMode.MARKDOWN)
        return
    if len(args) < 2 or args[1] not in JOBS:
        text = f"💼 **БИРЖА ТРУДА** (Баланс: `{p.get('coins', 0):,}` 🪙):\n"
        for j_id, j_data in JOBS.items():
            text += f"🔹 [{j_id}] {j_data['name']} (🪙 {j_data['min_coins']}–{j_data['max_coins']})\n"
        text += "👉 Используйте `/work <номер>`"
        await message.answer(text, parse_mode=ParseMode.MARKDOWN)
        return
    job = JOBS[args[1]]
    earned_coins, earned_xp = random.randint(job["min_coins"], job["max_coins"]), job["xp"]
    WORK_COOLDOWNS[uid] = now
    new_coins, new_xp = p.get("coins", 0) + earned_coins, p.get("xp", 0) + earned_xp
    new_level = p.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]: new_level = lvl
    def _upd():
        supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute()
    await asyncio.to_thread(_upd)
    await message.answer(f"✅ Вы отработали как **{job['name']}**!\n🪙 `+{earned_coins}` монет\n✨ `+{earned_xp} XP`", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("slots_help_"))
async def slots_help_callback(callback: types.CallbackQuery):
    uid = callback.data.split("_")[2]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    text = (
        "🎰 **Комбинации и коэффициенты слотов:**\n\n"
        "• 7️⃣ 7️⃣ 7️⃣ (Три семерки) — x10 от ставки!\n"
        "• 🍋 🍋 (Два одинаковых подряд) — x2 от ставки!\n"
        "• 🍇 🍇 🍇 (Три одинаковых фрукта) — x3 от ставки!\n"
        "• 🎰 🎰 (Два бара) — x5 от ставки!\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в казино", callback_data=f"menu_casino_{uid}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()
    await callback.answer()

@dp.callback_query(F.data.startswith("do_work_"))
async def do_work_callback(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    job_id = parts[2]
    uid = str(callback.from_user.id)
    
    p = await get_profile(callback.from_user)
    now = time.time()
    if now - WORK_COOLDOWNS.get(uid, 0) < 60:
        rem = int(60 - (now - WORK_COOLDOWNS.get(uid, 0)))
        await callback.answer(f"⏳ Отдохните еще {rem} сек.", show_alert=True)
        return
        
    job = JOBS.get(job_id)
    if not job:
        await callback.answer("❌ Профессия не найдена!", show_alert=True)
        return
        
    earned_coins, earned_xp = random.randint(job["min_coins"], job["max_coins"]), job["xp"]
    WORK_COOLDOWNS[uid] = now
    new_coins = p.get("coins", 0) + earned_coins
    new_xp = p.get("xp", 0) + earned_xp
    new_level = p.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]:
            new_level = lvl
            
    def _upd():
        supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute()
    await asyncio.to_thread(_upd)
    
    await callback.answer(f"✅ Вы отработали как {job['name']} (+{earned_coins} 🪙, +{earned_xp} XP)", show_alert=True)
    
    text = f"💼 **БИРЖА ТРУДА** (Баланс: `{new_coins:,}` 🪙):\n\n✅ Последняя смена ({job['name']}): `+{earned_coins} 🪙`, `+{earned_xp} XP`\n\nВыберите смену:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⛏ Шахтёр (40-90 🪙)", callback_data="do_work_1")],
        [InlineKeyboardButton(text="🛡 Стражник (60-130 🪙)", callback_data="do_work_2")],
        [InlineKeyboardButton(text="🧪 Алхимик (90-180 🪙)", callback_data="do_work_3")],
        [InlineKeyboardButton(text="🐉 Охотник (130-260 🪙)", callback_data="do_work_4")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        pass

@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Использование: `/dice <ставка> <числа от 1 до 6>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        bet = int(args[1])
        chosen = [int(x) for x in args[2:] if 1 <= int(x) <= 6]
        if bet <= 0 or not (1 <= len(chosen) <= 3):
            raise ValueError()
    except ValueError:
        await message.answer("❌ Ошибка ставки!", parse_mode=ParseMode.MARKDOWN)
        return
        
    p = await get_profile(message.from_user)
    if p.get("coins", 0) < bet:
        await message.answer("❌ У вас недостаточно монет!")
        return
        
    dice_msg = await message.answer_dice(emoji="🎲")
    roll = dice_msg.dice.value
    await asyncio.sleep(3)
    
    coins = p["coins"] - bet
    mult = {1: 6.0, 2: 3.0, 3: 2.0}[len(chosen)]
    
    if roll in chosen:
        win = int(bet * mult)
        coins += win
        profit = win - bet
        def _upd():
            supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute()
        await asyncio.to_thread(_upd)
        await message.answer(f"🎲 Выпало **{roll}**! Вы выиграли `+{profit:,}` монет! 🎉 (Баланс: `{coins:,}`)", parse_mode=ParseMode.MARKDOWN)
    else:
        def _upd():
            supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute()
        await asyncio.to_thread(_upd)
        await message.answer(f"🎲 Выпало **{roll}**. Проигрыш `{bet:,}` монет. 💸 (Баланс: `{coins:,}`)", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("coin"))
async def cmd_coin(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Использование: `/coin <ставка> <орел/решка>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        bet = int(args[1])
        user_choice = "орел" if args[2].lower() in ["орел", "о", "head"] else "решка"
        if bet <= 0: raise ValueError()
    except ValueError:
        await message.answer("❌ Неверная ставка!", parse_mode=ParseMode.MARKDOWN)
        return

    p = await get_profile(message.from_user)
    if p.get("coins", 0) < bet:
        await message.answer("❌ Недостаточно монет!")
        return

    result = random.choice(["орел", "решка"])
    coins = p["coins"] - bet
    
    if user_choice == result:
        win = bet * 2
        coins += win
        profit = win - bet
        def _upd():
            supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute()
        await asyncio.to_thread(_upd)
        await message.answer(f"🪙 Выпал **{result}**! Вы выиграли `+{profit:,}` монет! 🎉 (Баланс: `{coins:,}`)", parse_mode=ParseMode.MARKDOWN)
    else:
        def _upd():
            supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute()
        await asyncio.to_thread(_upd)
        await message.answer(f"🪙 Выпал **{result}**. Проигрыш `{bet:,}` монет. 💸 (Баланс: `{coins:,}`)", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("slots"))
async def cmd_slots(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: `/slots <ставка>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        bet = int(args[1])
        if bet <= 0: raise ValueError()
    except ValueError:
        await message.answer("❌ Неверная ставка!", parse_mode=ParseMode.MARKDOWN)
        return
        
    p = await get_profile(message.from_user)
    if p.get("coins", 0) < bet:
        await message.answer("❌ У вас недостаточно монет!")
        return
        
    slot_msg = await message.answer_dice(emoji="🎰")
    val = slot_msg.dice.value
    await asyncio.sleep(3)
    
    coins = p["coins"] - bet
    v = val - 1
    r1, r2, r3 = v % 4, (v // 4) % 4, (v // 16) % 4
    
    multiplier = 0
    if r1 == 3 and r2 == 3 and r3 == 3: multiplier = 10
    elif r1 == 3 and r2 == 3: multiplier = 5
    elif r1 == r2 == r3: multiplier = 3
    elif r1 == r2: multiplier = 2

    if multiplier > 0:
        win = bet * multiplier
        coins += win
        res_text = f"🎰 Выигрыш x{multiplier}! (`+{win:,}` 🪙)"
    else:
        res_text = f"🎰 Проигрыш (`-{bet:,}` 🪙)"
        
    def _upd():
        supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute()
    await asyncio.to_thread(_upd)
    
    await message.answer(f"{res_text}\n💰 Баланс: `{coins:,}` 🪙", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("duel"))
async def cmd_duel(message: types.Message, state: FSMContext):
    await state.clear()
    if not message.reply_to_message:
        await message.answer("⚔️ Ответьте на сообщение противника командой `/duel`", parse_mode=ParseMode.MARKDOWN)
        return
        
    user1, user2 = message.from_user, message.reply_to_message.from_user
    if user1.id == user2.id:
        await message.answer("❌ Нельзя вызывать на дуэль себя!")
        return
        
    p1, p2 = await get_profile(user1), await get_profile(user2)
    score1 = 50 + SHOP_EQUIPMENT.get(p1.get("equipped_item", ""), {}).get("duel_buff", 0)
    score2 = 50 + SHOP_EQUIPMENT.get(p2.get("equipped_item", ""), {}).get("duel_buff", 0)
    
    winner = random.choices([user1, user2], weights=[score1, score2], k=1)[0]
    await message.answer(f"⚔️ **ДУЭЛЬ!**\n\n🏆 Победитель: **{winner.first_name}**! 🎉", parse_mode=ParseMode.MARKDOWN)

# --- АДМИН-МЕНЮ И УНИВЕРСАЛЬНЫЕ АДМИН-КОМАНДЫ ---
@dp.message(Command("admin"))
async def cmd_admin_menu(message: types.Message):
    if not is_admin(message.from_user):
        await message.answer("❌ У вас нет прав администратора для просмотра этого меню!")
        return
    
    text = (
        "🛠 **ПАНЕЛЬ УПРАВЛЕНИЯ АДМИНИСТРАТОРА**\n\n"
        "Все админ-команды поддерживают два способа вызова:\n"
        "• **Реплаем** (ответом на сообщение игрока)\n"
        "• **Через аргументы** (`@username` или `user_id`)\n\n"
        "📋 **Список команд:**\n"
        "1. `/give <сумма>` (или `/give @user <сумма>`) — выдать монеты.\n"
        "2. `/setcoins <сумма>` (или `/setcoins @user <сумма>`) — точный баланс.\n"
        "3. `/givecar <ключ>` (или `/givecar @user <ключ>`) — выдать авто (например, `m5f90`).\n"
        "4. `/admin` — открыть это меню.\n\n"
        "⚠️ Соблюдайте осторожность."
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("give"))
async def admin_give(message: types.Message):
    if not is_admin(message.from_user):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if message.reply_to_message:
        if len(args) < 2:
            await message.answer("❌ Укажите сумму: `/give <сумма>`", parse_mode=ParseMode.MARKDOWN)
            return
        target_id, target_name = str(message.reply_to_message.from_user.id), message.reply_to_message.from_user.first_name
        try:
            amount = int(args[1])
        except ValueError:
            await message.answer("❌ Неверная сумма!")
            return
    else:
        if len(args) < 3:
            await message.answer("❌ Использование: `/give <сумма>` (реплаем) или `/give <@user/id> <сумма>`", parse_mode=ParseMode.MARKDOWN)
            return
        target_id, target_name = await resolve_target_user(message, args, identifier_index=1)
        if not target_id:
            await message.answer(target_name, parse_mode=ParseMode.MARKDOWN)
            return
        try:
            amount = int(args[2])
        except ValueError:
            await message.answer("❌ Неверная сумма!")
            return

    p = await get_profile_by_id(target_id)
    if not p:
        p = await get_profile(types.User(id=int(target_id), is_bot=False, first_name=target_name))
        
    new_coins = p.get("coins", 0) + amount
    def _upd():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", str(target_id)).execute()
    await asyncio.to_thread(_upd)
    await message.answer(f"✅ Игроку **{target_name}** начислено `+{amount:,}` 🪙 (Баланс: `{new_coins:,}` 🪙)", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("setcoins"))
async def admin_setcoins(message: types.Message):
    if not is_admin(message.from_user):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if message.reply_to_message:
        if len(args) < 2:
            await message.answer("❌ Укажите сумму: `/setcoins <сумма>`", parse_mode=ParseMode.MARKDOWN)
            return
        target_id, target_name = str(message.reply_to_message.from_user.id), message.reply_to_message.from_user.first_name
        try:
            amount = int(args[1])
        except ValueError:
            await message.answer("❌ Неверная сумма!")
            return
    else:
        if len(args) < 3:
            await message.answer("❌ Использование: `/setcoins <сумма>` (реплаем) или `/setcoins <@user/id> <сумма>`", parse_mode=ParseMode.MARKDOWN)
            return
        target_id, target_name = await resolve_target_user(message, args, identifier_index=1)
        if not target_id:
            await message.answer(target_name, parse_mode=ParseMode.MARKDOWN)
            return
        try:
            amount = int(args[2])
        except ValueError:
            await message.answer("❌ Неверная сумма!")
            return

    def _upd():
        supabase.table("users").update({"coins": amount}).eq("user_id", str(target_id)).execute()
    await asyncio.to_thread(_upd)
    await message.answer(f"✅ Баланс игрока **{target_name}** установлен на `{amount:,}` 🪙", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("givecar"))
async def admin_give_car(message: types.Message):
    if not is_admin(message.from_user):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    available_keys = ", ".join(CARS_CAT.keys())

    if message.reply_to_message:
        if len(args) < 2:
            await message.answer(f"❌ Укажите ключ машины:\nДоступно: `{available_keys}`", parse_mode=ParseMode.MARKDOWN)
            return
        target_id, target_name = str(message.reply_to_message.from_user.id), message.reply_to_message.from_user.first_name
        car_key = args[1].lower()
    else:
        if len(args) < 3:
            await message.answer(
                "❌ Использование: `/givecar <ключ>` (реплаем) или `/givecar <@user/id> <ключ>`\n"
                f"Доступные ключи: `{available_keys}`", 
                parse_mode=ParseMode.MARKDOWN
            )
            return
        target_id, target_name = await resolve_target_user(message, args, identifier_index=1)
        if not target_id:
            await message.answer(target_name, parse_mode=ParseMode.MARKDOWN)
            return
        car_key = args[2].lower()

    car_info = CARS_CAT.get(car_key)
    if not car_info:
        await message.answer(f"❌ Машина с ключом `{car_key}` не найдена!\nДоступные ключи: `{available_keys}`", parse_mode=ParseMode.MARKDOWN)
        return

    def _check_user_cars():
        return supabase.table("user_cars").select("*").eq("user_id", str(target_id)).execute()
    existing = await asyncio.to_thread(_check_user_cars)
    is_first = not existing.data

    def _insert_car():
        supabase.table("user_cars").insert({
            "user_id": str(target_id),
            "car_key": car_key,
            "car_name": car_info["name"],
            "color": "🖤 Черный",
            "engine_lvl": 1,
            "turbo_lvl": 1,
            "handling_lvl": 1,
            "is_active": is_first
        }).execute()
    
    try:
        await asyncio.to_thread(_insert_car)
        await message.answer(f"✅ Игроку **{target_name}** успешно выдана машина: **{car_info['name']}**!", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error giving car: {e}")
        await message.answer("❌ Ошибка при выдаче машины в базу данных.")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER И ЗАПУСК БОТА ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем мини-сервер для Render, чтобы он зафиксировал открытый порт и завершил деплой
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logging.info("Бот и веб-сервер успешно запущены...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
