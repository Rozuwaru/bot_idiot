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
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAEaeK78yhl1I3QrWzF3UMRBEPj0_-pEpgo"
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

APARTMENTS_CAT = {
    "studio": {"name": "🏢 Студия на окраине", "price": 1200},
    "1k": {"name": "🏢 1-комнатная квартира", "price": 2500},
    "3k": {"name": "🏢 3-комнатная в центре", "price": 5500},
    "penthouse": {"name": "🏢 Элитный пентхаус", "price": 15000},
}

HOUSES_CAT = {
    "dacha": {"name": "🏡 Дачный домик", "price": 4000},
    "cottage": {"name": "🏡 Загородный коттедж", "price": 10000},
    "villa": {"name": "🏡 Элитная вилла с бассейном", "price": 30000},
}

CARS_CAT = {
    "old": {"name": "🚗 Старая ВАЗ (Б/У)", "price": 900},
    "sedan": {"name": "🚗 Городской седан", "price": 3000},
    "suv": {"name": "🚗 Семейный кроссовер", "price": 8000},
    "sport": {"name": "🏎 Спортивный суперкар", "price": 22000},
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

def get_child_age(birth_time: int) -> str:
    if not birth_time or int(birth_time) == 0:
        return "0 лет"
    diff = time.time() - int(birth_time)
    years = diff / 259200
    if years < 1:
        months = int(years * 12)
        return f"{max(0, months)} мес."
    return f"{years:.1f} лет"

def is_admin(user: types.User) -> bool:
    if not user or not user.username:
        return False
    return user.username.lower() in {u.lower() for u in ADMIN_USERNAMES}

async def get_profile(user: types.User):
    uid = str(user.id)
    now = int(time.time())
    def _fetch():
        return supabase.table("users").select("*").eq("user_id", uid).execute()
    try:
        response = await asyncio.to_thread(_fetch)
        if response.data:
            user_data = response.data[0]
            if not user_data.get("created_at") or int(user_data.get("created_at", 0)) == 0:
                supabase.table("users").update({"created_at": now}).eq("user_id", uid).execute()
                user_data["created_at"] = now
            return user_data
    except Exception as e:
        logging.error(f"Supabase fetch error: {e}")

    new_user = {
        "user_id": uid,
        "username": user.username or user.first_name,
        "coins": 100, "xp": 0, "level": 1, "respect": 0,
        "partner_id": 0, "partner_name": "EMPTY",
        "inventory": "",
        "armory": "",
        "equipped_item": "",
        "personal_apartment": "❌ Нет",
        "personal_house": "❌ Нет",
        "personal_car": "❌ Нет",
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

async def get_or_create_family(uid1: str, uid2: str):
    uids = sorted([str(uid1), str(uid2)])
    fam_id = f"{uids[0]}_{uids[1]}"
    
    def _fetch():
        return supabase.table("families").select("*").eq("family_id", fam_id).execute()
    
    try:
        res = await asyncio.to_thread(_fetch)
        if res.data:
            return res.data[0]
    except Exception:
        pass
    
    new_fam = {
        "family_id": fam_id,
        "partner1_id": uids[0],
        "partner2_id": uids[1],
        "budget": 0,
        "food": 0,
        "house": "❌ Нет",
        "apartment": "❌ Нет",
        "car": "❌ Нет",
        "child_name": "❌ Нет",
        "child_hunger": 100,
        "child_birth_time": 0
    }
    def _insert():
        return supabase.table("families").upsert(new_fam).execute()
    try:
        ins_res = await asyncio.to_thread(_insert)
        if ins_res.data:
            return ins_res.data[0]
    except Exception:
        pass
    return new_fam

def get_main_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data=f"menu_profile_{user_id}"),
         InlineKeyboardButton(text="🎒 Инвентарь", callback_data=f"menu_inv_{user_id}")],
        [InlineKeyboardButton(text="⚔️ Оружейная", callback_data=f"menu_armory_{user_id}"),
         InlineKeyboardButton(text="🛒 Магазины", callback_data=f"menu_shops_{user_id}")],
        [InlineKeyboardButton(text="🍑 Секс-шоп", callback_data=f"menu_sexshop_{user_id}"),
         InlineKeyboardButton(text="🏠 Личное имущество", callback_data=f"menu_personal_{user_id}")],
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data=f"menu_top_{user_id}"),
         InlineKeyboardButton(text="💼 Биржа труда", callback_data=f"menu_work_{user_id}")],
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
        "Используйте кнопки ниже для управления персонажем, покупки имущества и развлечений."
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
    except Exception as e:
        logging.error(f"Error in back_home: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

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
            
            text = (
                f"👤 **Профиль: {p.get('username')}**\n"
                f"⏳ Возраст в боте: `{bot_age}`\n"
                f"⭐ Уровень: `{lvl}` / 67 (*{title}*)\n"
                f"✨ Опыт (XP): `{p.get('xp')}`\n"
                f"🪙 Монеты: `{p.get('coins')}`\n"
                f"❤️ Респект: `{p.get('respect')}`\n"
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
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "armory":
            armory_str = p.get("armory") or ""
            arm_items = [i.strip() for i in armory_str.split(",") if i.strip()]
            equipped = p.get("equipped_item", "")
            
            text = f"⚔️ **ОРУЖЕЙНАЯ ИГРОКА {p.get('username')}** (Баланс: `{p.get('coins', 0)}` 🪙)\n\n"
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
                
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

        elif action == "inv":
            inv_str = p.get("inventory") or ""
            items = [i.strip() for i in inv_str.split(",") if i.strip()]
            
            if not items:
                text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p.get('coins', 0)}` 🪙):\n\nВаш инвентарь пуст."
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]])
            else:
                text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p.get('coins', 0)}` 🪙):\nНажмите на предмет, чтобы использовать его:\n\n"
                buttons = []
                for idx, item_key in enumerate(items):
                    item_info = SHOP_CONSUMABLES.get(item_key) or SEX_SHOP.get(item_key) or {"name": item_key}
                    buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {item_info['name']}", callback_data=f"use_item_{idx}_{item_key}")])
                buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
                kb = InlineKeyboardMarkup(inline_keyboard=buttons)
                
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "shops":
            text = f"🛒 **ВЫБЕРИТЕ МАГАЗИН** (Баланс: `{p.get('coins', 0)}` 🪙):"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Снаряжение (в Оружейную)", callback_data=f"shop_eq_list_{uid}")],
                [InlineKeyboardButton(text="🍺 Продукты и ПК (в инвентарь)", callback_data=f"shop_cons_list_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

        elif action == "sexshop":
            text = f"🍑 **СЕКС-ШОП «БЕЗ ТОРМОЗОВ»** (Баланс: `{p.get('coins', 0)}` 🪙):\n\nПриобретайте игрушки, они попадают в инвентарь:"
            buttons = []
            for item_id, data in SEX_SHOP.items():
                buttons.append([InlineKeyboardButton(text=f"{data['name']} — {data['price']} 🪙", callback_data=f"buy_sex_{item_id}_{uid}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

        elif action == "personal":
            text = (
                f"🏠 **ЛИЧНОЕ ИМУЩЕСТВО** (Баланс: `{p.get('coins', 0)}` 🪙)\n\n"
                f"🏢 Квартира: `{p.get('personal_apartment', '❌ Нет')}`\n"
                f"🏡 Дом: `{p.get('personal_house', '❌ Нет')}`\n"
                f"🚗 Машина: `{p.get('personal_car', '❌ Нет')}`\n\n"
                f"👇 Выберите категорию для покупки:"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏢 Купить квартиру", callback_data=f"pers_shop_apt_{uid}"),
                 InlineKeyboardButton(text="🏡 Купить дом", callback_data=f"pers_shop_house_{uid}")],
                [InlineKeyboardButton(text="🚗 Купить машину", callback_data=f"pers_shop_car_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "top":
            def _fetch_top():
                return supabase.table("users").select("username, level, coins").order("level", desc=True).limit(10).execute()
            try:
                res = await asyncio.to_thread(_fetch_top)
            except Exception:
                res = None
            text = "🏆 **ТОП-10 ИГРОКОВ:**\n\n"
            if res and res.data:
                for i, u in enumerate(res.data, 1):
                    lvl = u.get('level', 1)
                    title = LEVELS.get(lvl, {}).get("title", "")
                    text += f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙 `{u.get('coins')}`\n"
            else:
                text += "Игроков пока нет."
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "work":
            text = f"💼 **БИРЖА ТРУДА** (Баланс: `{p.get('coins', 0)}` 🪙):\n\nВыберите смену:"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⛏ Шахтёр (40-90 🪙)", callback_data="do_work_1")],
                [InlineKeyboardButton(text="🛡 Стражник (60-130 🪙)", callback_data="do_work_2")],
                [InlineKeyboardButton(text="🧪 Алхимик (90-180 🪙)", callback_data="do_work_3")],
                [InlineKeyboardButton(text="🐉 Охотник (130-260 🪙)", callback_data="do_work_4")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "casino":
            text = (
                f"🎰 **КАЗИНО И ИГРЫ** (Баланс: `{p.get('coins', 0)}` 🪙):\n\n"
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
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
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
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in callback_main_menu: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

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
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@dp.callback_query(F.data.startswith("set_music_prompt_"))
async def set_music_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    await state.set_state(ProfileState.waiting_for_music)
    await callback.message.edit_text(
        "🎵 **УСТАНОВКА МУЗЫКИ В ПРОФИЛЬ**\n\nОтправьте в этот чат любой аудиофайл или музыку из Telegram следующим сообщением:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"profile_music_menu_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )
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
    def _fetch():
        return supabase.table("users").select("profile_music, username").eq("user_id", target_uid).execute()
    try:
        res = await asyncio.to_thread(_fetch)
        if res.data and res.data[0].get("profile_music"):
            file_id = res.data[0]["profile_music"]
            uname = res.data[0]["username"]
            await callback.message.answer_audio(audio=file_id, caption=f"🎵 Музыка из профиля игрока {uname}")
            await callback.answer("🎶 Воспроизведение...")
        else:
            await callback.answer("❌ У этого игрока не установлена музыка в профиле!", show_alert=True)
    except Exception as e:
        logging.error(f"Error playing music: {e}")
        await callback.answer("❌ Ошибка при воспроизведении!", show_alert=True)

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

# --- СЛОТЫ И ДРУГИЕ КОМПОНЕНТЫ ---

@dp.callback_query(F.data.startswith("slots_help_"))
async def slots_help_callback(callback: types.CallbackQuery):
    uid = callback.data.split("_")[2]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    text = (
        "🎰 **КОМБИНАЦИИ СЛОТОВ:**\n\n"
        "• 7️⃣7️⃣7️⃣ — x10\n"
        "• 7️⃣7️⃣... — x5\n"
        "• 3 одинаковых символа — x3\n"
        "• Одинаковые первые 2 символа — x2"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в казино", callback_data=f"menu_casino_{uid}")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_sex_"))
async def buy_sex_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    uid = parts[-1]
    item_key = "_".join(parts[2:-1])
    
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
        
    item = SEX_SHOP[item_key]
    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < item["price"]:
        await callback.answer(f"❌ Недостаточно монет! Нужно {item['price']} 🪙", show_alert=True)
        return
    new_coins = p["coins"] - item["price"]
    current_inv = p.get("inventory") or ""
    updated_inv = f"{current_inv},{item_key}" if current_inv else item_key
    
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "inventory": updated_inv}).eq("user_id", str(uid)).execute())
    except Exception as e:
        logging.error(f"Supabase update error: {e}")
        
    await callback.answer(f"🍑 Успешно куплено: {item['name']}! Предмет в инвентаре.", show_alert=True)
    
    p_refreshed = await get_profile(callback.from_user)
    try:
        text = f"🍑 **СЕКС-ШОП «БЕЗ ТОРМОЗОВ»** (Баланс: `{p_refreshed.get('coins', 0)}` 🪙):\n\nПриобретайте игрушки, они попадают в инвентарь:"
        buttons = []
        for i_id, data in SEX_SHOP.items():
            buttons.append([InlineKeyboardButton(text=f"{data['name']} — {data['price']} 🪙", callback_data=f"buy_sex_{i_id}_{uid}")])
        buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except Exception:
        pass

@dp.callback_query(F.data.startswith("pers_shop_apt_"))
async def pers_shop_apt(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    buttons = []
    for k, v in APARTMENTS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"pers_buy_apt_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    await callback.message.edit_text(f"🏢 **РЫНОК КВАРТИР** (Баланс: `{p.get('coins', 0)}` 🪙):\nВыберите вариант:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("pers_shop_house_"))
async def pers_shop_house(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    buttons = []
    for k, v in HOUSES_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"pers_buy_house_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    await callback.message.edit_text(f"🏡 **РЫНОК ДОМОВ** (Баланс: `{p.get('coins', 0)}` 🪙):\nВыберите вариант:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("pers_shop_car_"))
async def pers_shop_car(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    buttons = []
    for k, v in CARS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"pers_buy_car_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    await callback.message.edit_text(f"🚗 **АВТОСАЛОН** (Баланс: `{p.get('coins', 0)}` 🪙):\nВыберите автомобиль:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("pers_buy_"))
async def pers_buy_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    category = parts[2] 
    item_key = parts[3] 
    uid = parts[4]
    
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
        
    p = await get_profile(callback.from_user)
    item_data = {}
    col_name = ""
    if category == "apt":
        item_data = APARTMENTS_CAT[item_key]
        col_name = "personal_apartment"
    elif category == "house":
        item_data = HOUSES_CAT[item_key]
        col_name = "personal_house"
    elif category == "car":
        item_data = CARS_CAT[item_key]
        col_name = "personal_car"
        
    if p.get("coins", 0) < item_data["price"]:
        await callback.answer(f"❌ Недостаточно монет! Нужно {item_data['price']} 🪙", show_alert=True)
        return
        
    new_coins = p["coins"] - item_data["price"]
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({
            "coins": new_coins,
            col_name: item_data["name"]
        }).eq("user_id", str(uid)).execute())
    except Exception as e:
        logging.error(f"Supabase error: {e}")
    
    await callback.answer(f"🎉 Успешно куплено: {item_data['name']}!", show_alert=True)
    callback.data = f"menu_personal_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data == "family_main")
async def callback_family_main(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        p = await get_profile(callback.from_user)
        pid = p.get("partner_id")
        if not pid or str(pid) == "0":
            await callback.answer("❌ Доступно только для женатых пар!", show_alert=True)
            return
        
        fam = await get_or_create_family(callback.from_user.id, pid)
        uid = callback.from_user.id
        
        child_display = fam['child_name']
        if fam['child_name'] != "❌ Нет":
            c_age = get_child_age(fam.get('child_birth_time', 0))
            child_display = f"{fam['child_name']} (Возраст: {c_age})"

        text = (
            f"🏡 **СЕМЕЙНЫЙ ОЧАГ И ИМУЩЕСТВО** (Баланс: `{p.get('coins', 0)}` 🪙)\n\n"
            f"💵 Бюджет семьи: `{fam['budget']}` 🪙\n"
            f"🍔 Запасы еды: `{fam['food']}` ед.\n"
            f"🏠 Дом: `{fam['house']}`\n"
            f"🏢 Квартира: `{fam['apartment']}`\n"
            f"🚗 Машина: `{fam['car']}`\n"
            f"👶 Ребенок: `{child_display}` (Сытость: `{fam['child_hunger']}/100`)\n\n"
            f"👇 Выберите категорию покупок или действий:"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💵 Вложить в бюджет", callback_data="fam_deposit_prompt"),
             InlineKeyboardButton(text="🍔 Купить еду (50 🪙)", callback_data="fam_buy_food")],
            [InlineKeyboardButton(text="🏢 Выбрать квартиру", callback_data="fam_shop_apt"),
             InlineKeyboardButton(text="🏡 Выбрать дом", callback_data="fam_shop_house")],
            [InlineKeyboardButton(text="🚗 Выбрать машину", callback_data="fam_shop_car"),
             InlineKeyboardButton(text="👶 Завести ребенка (1000 🪙)", callback_data="fam_buy_child")],
            [InlineKeyboardButton(text="🍼 Покормить ребенка", callback_data="fam_feed_child"),
             InlineKeyboardButton(text="🧸 Поиграть с ребенком", callback_data="fam_play_child")],
            [InlineKeyboardButton(text="🗑 Отдать ребенка", callback_data="fam_delete_child")],
            [InlineKeyboardButton(text="🔙 Назад к отношениям", callback_data=f"menu_marry_{uid}")]
        ])
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in family_main: {e}")
        await callback.answer("❌ Ошибка при открытии меню семьи!", show_alert=True)

@dp.callback_query(F.data == "fam_shop_apt")
async def fam_shop_apt(callback: types.CallbackQuery):
    buttons = []
    for k, v in APARTMENTS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"fam_buy_item_apt_{k}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в семью", callback_data="family_main")])
    await callback.message.edit_text("🏢 **РЫНОК КВАРТИР:**\nВыберите вариант для покупки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == "fam_shop_house")
async def fam_shop_house(callback: types.CallbackQuery):
    buttons = []
    for k, v in HOUSES_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"fam_buy_item_house_{k}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в семью", callback_data="family_main")])
    await callback.message.edit_text("🏡 **РЫНОК ДОМОВ И ВИЛЛ:**\nВыберите загородную недвижимость:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == "fam_shop_car")
async def fam_shop_car(callback: types.CallbackQuery):
    buttons = []
    for k, v in CARS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"fam_buy_item_car_{k}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в семью", callback_data="family_main")])
    await callback.message.edit_text("🚗 **АВТОСАЛОН:**\nВыберите семейный автомобиль:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("fam_buy_item_"))
async def fam_buy_specific_item(callback: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.replace("fam_buy_item_", "").split("_", 1)
        category = parts[0]
        item_key = parts[1]
        
        p = await get_profile(callback.from_user)
        pid = p.get("partner_id")
        fam = await get_or_create_family(callback.from_user.id, pid)
        fam_id = fam["family_id"]
        
        item_data = {}
        if category == "apt": item_data = APARTMENTS_CAT[item_key]
        elif category == "house": item_data = HOUSES_CAT[item_key]
        elif category == "car": item_data = CARS_CAT[item_key]
        
        if fam["budget"] < item_data["price"]:
            await callback.answer(f"❌ В семейном бюджете не хватает средств! Нужно {item_data['price']} 🪙", show_alert=True)
            return
            
        column_map = {"apt": "apartment", "house": "house", "car": "car"}
        col_name = column_map[category]
        
        new_budget = fam["budget"] - item_data["price"]
        try:
            await asyncio.to_thread(lambda: supabase.table("families").update({
                "budget": new_budget,
                col_name: item_data["name"]
            }).eq("family_id", fam_id).execute())
        except Exception:
            pass
        
        await callback.answer(f"🎉 Успешно приобретено: {item_data['name']}!", show_alert=True)
        await callback_family_main(callback, state)
    except Exception as e:
        logging.error(f"Error buying item: {e}")
        await callback.answer("❌ Ошибка при покупке!", show_alert=True)

@dp.callback_query(F.data.startswith("fam_"))
async def callback_family_actions(callback: types.CallbackQuery, state: FSMContext):
    try:
        action = callback.data.split("_")[1]
        p = await get_profile(callback.from_user)
        pid = p.get("partner_id")
        if not pid or str(pid) == "0":
            await callback.answer("❌ Вы не в браке!", show_alert=True)
            return
            
        fam = await get_or_create_family(callback.from_user.id, pid)
        fam_id = fam["family_id"]
        
        if callback.data == "fam_deposit_prompt":
            await state.set_state(FamilyState.waiting_for_deposit_amount)
            await state.update_data(fam_id=fam_id, current_budget=fam["budget"])
            await callback.message.edit_text(
                "💵 **ПОПЛАНЕНИЕ СЕМЕЙНОГО БЮДЖЕТА**\n\nВведите сумму монет, которую хотите внести:",
                parse_mode=ParseMode.MARKDOWN
            )
            await callback.answer()
            return
            
        elif callback.data == "fam_delete_child":
            if fam["child_name"] == "❌ Нет":
                await callback.answer("❌ У вас нет ребенка!", show_alert=True)
                return
            try:
                await asyncio.to_thread(lambda: supabase.table("families").update({
                    "child_name": "❌ Нет",
                    "child_hunger": 100,
                    "child_birth_time": 0
                }).eq("family_id", fam_id).execute())
            except Exception:
                pass
            await callback.answer("🗑 Ребенок был отдан в приют.", show_alert=True)
            await callback_family_main(callback, state)
            return
            
        elif action == "buy" and callback.data.split("_")[2] == "food":
            if fam["budget"] < 50:
                await callback.answer("❌ В семейном бюджете недостаточно средств (нужно 50 🪙)!", show_alert=True)
                return
            try:
                await asyncio.to_thread(lambda: supabase.table("families").update({
                    "budget": fam["budget"] - 50,
                    "food": fam["food"] + 20
                }).eq("family_id", fam_id).execute())
            except Exception:
                pass
            await callback.answer("✅ Куплено 20 ед. продуктов в семью!", show_alert=True)
                
        elif action == "buy" and callback.data.split("_")[2] == "child":
            if fam["child_name"] != "❌ Нет":
                await callback.answer("⚠️ У вас уже есть ребенок!", show_alert=True)
                return
            if fam["budget"] < 1000:
                await callback.answer("❌ Нужно 1000 🪙 в семейном бюджете на расходы по рождению!", show_alert=True)
                return
            
            await state.set_state(FamilyState.waiting_for_child_name)
            await state.update_data(fam_id=fam_id, cost=1000, current_budget=fam["budget"])
            await callback.message.edit_text(
                "👶 **РОЖДЕНИЕ РЕБЕНКА**\n\nНапишите в чат желаемое **имя** для вашего ребенка следующим сообщением:",
                parse_mode=ParseMode.MARKDOWN
            )
            await callback.answer()
            return
                
        elif action == "feed":
            if fam["child_name"] == "❌ Нет":
                await callback.answer("❌ У вас пока нет детей!", show_alert=True)
                return
            if fam["food"] < 10:
                await callback.answer("❌ В семье закончилась еда! Купите продукты в меню семьи.", show_alert=True)
                return
            new_hunger = min(100, fam["child_hunger"] + 35)
            try:
                await asyncio.to_thread(lambda: supabase.table("families").update({
                    "food": fam["food"] - 10,
                    "child_hunger": new_hunger
                }).eq("family_id", fam_id).execute())
            except Exception:
                pass
            await callback.answer(f"🍼 Вы покормили ребенка. Сытость: {new_hunger}/100", show_alert=True)
            
        elif action == "play":
            if fam["child_name"] == "❌ Нет":
                await callback.answer("❌ У вас пока нет детей!", show_alert=True)
                return
            await callback.answer(f"🧸 Вы поиграли с ребенком {fam['child_name']}. Он очень доволен!", show_alert=True)
            
        await callback_family_main(callback, state)
    except Exception as e:
        logging.error(f"Error in family actions: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.message(FamilyState.waiting_for_deposit_amount)
async def process_deposit_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await message.answer("❌ Введите корректное положительное число монет:")
        return
        
    p = await get_profile(message.from_user)
    if p.get("coins", 0) < amount:
        await message.answer(f"❌ У вас недостаточно монет! На балансе: {p.get('coins', 0)} 🪙. Введите другую сумму:")
        return
        
    data = await state.get_data()
    fam_id = data.get("fam_id")
    current_budget = data.get("current_budget")
    
    new_user_coins = p["coins"] - amount
    new_budget = current_budget + amount
    
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_user_coins}).eq("user_id", p["user_id"]).execute())
        await asyncio.to_thread(lambda: supabase.table("families").update({"budget": new_budget}).eq("family_id", fam_id).execute())
    except Exception:
        pass
    
    await state.clear()
    await message.answer(f"✅ Вы успешно внесли `{amount}` монет в семейный бюджет! 💵 (Общий бюджет: `{new_budget}` 🪙)", parse_mode=ParseMode.MARKDOWN)

@dp.message(FamilyState.waiting_for_child_name)
async def process_child_name(message: types.Message, state: FSMContext):
    child_name = message.text.strip()
    if not child_name or len(child_name) > 20:
        await message.answer("❌ Имя слишком длинное или пустое. Введите корректное имя для ребенка:")
        return
        
    data = await state.get_data()
    fam_id = data.get("fam_id")
    cost = data.get("cost")
    current_budget = data.get("current_budget")
    
    new_budget = current_budget - cost
    try:
        await asyncio.to_thread(lambda: supabase.table("families").update({
            "budget": new_budget,
            "child_name": child_name,
            "child_hunger": 100,
            "child_birth_time": int(time.time())
        }).eq("family_id", fam_id).execute())
    except Exception:
        pass
    
    await state.clear()
    await message.answer(f"🎉 Поздравляем! У вас родился ребенок по имени **{child_name}**! 👶🍼 (Его возраст начнет расти по 1 году каждые 3 дня)", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("shop_eq_list_"))
async def callback_shop_eq(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    text = f"⚔️ **МАГАЗИН СНАРЯЖЕНИЯ** (Баланс: `{p.get('coins', 0)}` 🪙):\n\n"
    buttons = []
    for item_id, data in SHOP_EQUIPMENT.items():
        text += f"🔹 **{data['name']}** ({data['price']} 🪙)\n   └ *{data['desc']}*\n\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']}", callback_data=f"buy_eq_{item_id}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data=f"menu_shops_{uid}")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@dp.callback_query(F.data.startswith("shop_cons_list_"))
async def callback_shop_cons(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    text = f"🍺 **ПРОДУКТЫ И ТЕХНИКА** (Баланс: `{p.get('coins', 0)}` 🪙):\n\n"
    buttons = []
    for item_id, data in SHOP_CONSUMABLES.items():
        text += f"🔹 **{data['name']}** ({data['price']} 🪙)\n   └ *{data['desc']}*\n\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']}", callback_data=f"buy_cons_{item_id}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data=f"menu_shops_{uid}")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_eq_"))
async def callback_buy_eq(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    item_id = f"{parts[2]}_{parts[3]}"
    uid = parts[4]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    item = SHOP_EQUIPMENT[item_id]
    p = await get_profile(callback.from_user)
    
    if p.get("coins", 0) < item["price"]:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
        
    new_coins = p["coins"] - item["price"]
    armory_str = p.get("armory") or ""
    updated_armory = f"{armory_str},{item_id}" if armory_str else item_id
    
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "armory": updated_armory}).eq("user_id", str(uid)).execute())
    except Exception as e:
        logging.error(f"Supabase update error: {e}")
        
    await callback.answer(f"✅ {item['name']} добавлен в Оружейную!", show_alert=True)
    callback.data = f"menu_armory_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("equip_item_"))
async def callback_equip_item(callback: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split("_", 2)
        remainder = parts[2]
        idx_str, item_key = remainder.split("_", 1)
        uid = str(callback.from_user.id)
        
        p = await get_profile(callback.from_user)
        armory_str = p.get("armory") or ""
        arm_items = [i.strip() for i in armory_str.split(",") if i.strip()]
        
        item_idx = int(idx_str)
        if item_idx >= len(arm_items) or arm_items[item_idx] != item_key:
            await callback.answer("❌ Предмет не найден!", show_alert=True)
            return
            
        item_info = SHOP_EQUIPMENT.get(item_key, {"name": item_key})
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"equipped_item": item_key}).eq("user_id", uid).execute())
        except Exception:
            pass
            
        await callback.answer(f"🟢 Надето: {item_info['name']}!", show_alert=True)
        callback.data = f"menu_armory_{uid}"
        await callback_main_menu(callback, state)
    except Exception as e:
        logging.error(f"Error in equip_item: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.callback_query(F.data.startswith("unequip_item_"))
async def callback_unequip_item(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.data.split("_")[2]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
        
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"equipped_item": ""}).eq("user_id", uid).execute())
    except Exception:
        pass
        
    await callback.answer("🛑 Экипировка снята.", show_alert=True)
    callback.data = f"menu_armory_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("buy_cons_"))
async def callback_buy_cons(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    uid = parts[-1]
    item_key = "_".join(parts[2:-1])
    
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
        
    item = SHOP_CONSUMABLES[item_key]
    p = await get_profile(callback.from_user)
    
    if p.get("coins", 0) < item["price"]:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
        
    new_coins = p["coins"] - item["price"]
    current_inv = p.get("inventory") or ""
    updated_inv = f"{current_inv},{item_key}" if current_inv else item_key
    
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "inventory": updated_inv}).eq("user_id", str(uid)).execute())
    except Exception as e:
        logging.error(f"Supabase update error: {e}")
        
    await callback.answer(f"✅ {item['name']} добавлен в инвентарь!", show_alert=True)
    
    p_refreshed = await get_profile(callback.from_user)
    try:
        text = f"🍺 **ПРОДУКТЫ И ТЕХНИКА** (Баланс: `{p_refreshed.get('coins', 0)}` 🪙):\n\n"
        buttons = []
        for i_id, data in SHOP_CONSUMABLES.items():
            text += f"🔹 **{data['name']}** ({data['price']} 🪙)\n   └ *{data['desc']}*\n\n"
            buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']}", callback_data=f"buy_cons_{i_id}_{uid}")])
        buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data=f"menu_shops_{uid}")])
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except Exception:
        pass

@dp.callback_query(F.data.startswith("use_item_"))
async def callback_use_item(callback: types.CallbackQuery):
    try:
        parts = callback.data.split("_", 2)
        remainder = parts[2]
        idx_str, item_key = remainder.split("_", 1)
        item_idx = int(idx_str)
        
        p = await get_profile(callback.from_user)
        inv_str = p.get("inventory") or ""
        items = [i.strip() for i in inv_str.split(",") if i.strip()]
        
        if item_idx >= len(items) or items[item_idx] != item_key:
            await callback.answer("❌ Предмет уже использован или не найден!", show_alert=True)
            return
            
        if not item_key.startswith("sex_"):
            items.pop(item_idx)
        new_inv_str = ",".join(items)
        
        uid = p["user_id"]
        coins = p.get("coins", 0)
        xp = p.get("xp", 0)
        respect = p.get("respect", 0)
        smoking_level = p.get("smoking_level", 0)
        
        effect_message = ""
        
        if item_key == "cigars":
            smoking_level += 1
            respect += 5
            effect_message = f"🚬 Вы закурили сигарету. Никотиновая зависимость (+1), авторитет +5 респекта!"
        elif item_key == "hookah":
            xp += 80
            respect += 3
            effect_message = "💨 Вы расслабились за кальяном: +80 XP и +3 респекта."
        elif item_key == "chips":
            xp += 15
            coins += 5
            effect_message = "🍟 Съели чипсы: +15 XP и +5 монет."
        elif item_key == "whiskey":
            respect += 40
            coins -= 20
            effect_message = "🥃 Выпили элитный виски: статус +40 респекта."
        elif item_key == "chair":
            respect += 100
            effect_message = "💺 Кресло установлено: +100 респекта."
        elif item_key.startswith("sex_"):
            item_name = SEX_SHOP[item_key]["name"]
            effect_message = f"🍑 Игрушка {item_name} готова к использованию в команде /sex."
        elif item_key == "beer_okhota":
            effect_message = "🍺 Вы выпили «Охота Крепкое»!"
            try:
                if callback.message.chat.type in ["group", "supergroup"]:
                    await bot.restrict_chat_member(
                        chat_id=callback.message.chat.id,
                        user_id=callback.from_user.id,
                        permissions=types.ChatPermissions(can_send_messages=False),
                        until_date=int(time.time()) + 120
                    )
                    effect_message += " 🔇 (Мут на 2 мин!)"
            except Exception:
                pass
            coins += random.randint(20, 80)
        elif item_key == "energy":
            effect_message = "⚡ Энергетик выпит: +50 XP."
            xp += 50
        elif item_key == "pizza":
            effect_message = "🍔 Пицца съедена: +30 XP и +20 монет."
            xp += 30
            coins += 20
        elif item_key == "vodka":
            effect_message = "🥃 Паленая водка ударила в голову!"
            try:
                if callback.message.chat.type in ["group", "supergroup"]:
                    await bot.restrict_chat_member(
                        chat_id=callback.message.chat.id,
                        user_id=callback.from_user.id,
                        permissions=types.ChatPermissions(can_send_messages=False),
                        until_date=int(time.time()) + 300
                    )
            except Exception:
                pass
            if random.random() > 0.5:
                coins += 100
                effect_message += " Удача, +100 🪙."
            else:
                loss = min(coins, 100)
                coins -= loss
                effect_message += f" Потеряли {loss} 🪙."
        elif item_key == "pc":
            effect_message = "💻 ПК собран: +150 респекта."
            respect += 150
            
        new_level = p.get("level", 1)
        for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
            if xp >= data["xp"]: new_level = lvl

        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({
                "coins": coins, "xp": xp, "respect": respect, "level": new_level, "inventory": new_inv_str, "smoking_level": smoking_level
            }).eq("user_id", uid).execute())
        except Exception as e:
            logging.error(f"Supabase update error: {e}")
        
        await callback.answer(effect_message, show_alert=True)
        
        p_updated = await get_profile(callback.from_user)
        items_up = [i.strip() for i in (p_updated.get("inventory") or "").split(",") if i.strip()]
        if not items_up:
            text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p_updated.get('coins', 0)}` 🪙):\n\nИнвентарь пуст."
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]])
        else:
            text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p_updated.get('coins', 0)}` 🪙):\n\n"
            buttons = []
            for idx, i_key in enumerate(items_up):
                i_info = SHOP_CONSUMABLES.get(i_key) or SEX_SHOP.get(i_key) or {"name": i_key}
                buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {i_info['name']}", callback_data=f"use_item_{idx}_{i_key}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")] )
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error in use_item: {e}")
        await callback.answer("❌ Ошибка при использовании предмета!", show_alert=True)

@dp.callback_query(F.data.startswith("do_work_"))
async def callback_do_work(callback: types.CallbackQuery):
    try:
        job_id = callback.data.split("_")[2]
        job = JOBS[job_id]
        uid = str(callback.from_user.id)
        p = await get_profile(callback.from_user)
        
        now = time.time()
        if now - WORK_COOLDOWNS.get(uid, 0) < 60:
            rem = int(60 - (now - WORK_COOLDOWNS.get(uid, 0)))
            await callback.answer(f"⏳ Отдохните еще {rem} сек.", show_alert=True)
            return
            
        WORK_COOLDOWNS[uid] = now
        earned_coins = random.randint(job["min_coins"], job["max_coins"])
        earned_xp = job["xp"]
        
        new_coins = p.get("coins", 0) + earned_coins
        new_xp = p.get("xp", 0) + earned_xp
        new_level = p.get("level", 1)
        for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
            if new_xp >= data["xp"]: new_level = lvl
            
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
        except Exception:
            pass
        await callback.answer(f"✅ Смена окончена! +{earned_coins} 🪙, +{earned_xp} XP", show_alert=True)
    except Exception as e:
        logging.error(f"Error in do_work: {e}")
        await callback.answer("❌ Ошибка при работе!", show_alert=True)

@dp.callback_query(F.data == "action_sex_menu")
async def callback_action_sex_menu(callback: types.CallbackQuery):
    await show_sex_selection(callback.message, callback.from_user)
    await callback.answer()

@dp.message(Command("sex"))
async def cmd_sex_text(message: types.Message, state: FSMContext):
    await state.clear()
    await show_sex_selection(message, message.from_user)

async def show_sex_selection(message_obj, user_obj):
    p = await get_profile(user_obj)
    pid, pname = p.get("partner_id"), p.get("partner_name")
    
    if not pid or str(pid) == "0" or not pname or pname == "EMPTY":
        if isinstance(message_obj, types.CallbackQuery):
            await message_obj.answer("🛏️ Эта команда доступна только тем, кто состоит в браке!", show_alert=True)
        else:
            await message_obj.answer("🛏️ Эта команда доступна только тем, кто состоит в браке!")
        return

    uid = str(user_obj.id)
    now = time.time()
    if now - INTIMATE_COOLDOWNS.get(uid, 0) < 600:
        rem = int(600 - (now - INTIMATE_COOLDOWNS.get(uid, 0)))
        text_cd = f"⏳ Вы слишком устали. Отдохните еще {rem // 60} мин."
        if isinstance(message_obj, types.CallbackQuery):
            await message_obj.answer(text_cd, show_alert=True)
        else:
            await message_obj.answer(text_cd)
        return

    inv_str = p.get("inventory") or ""
    items = [i.strip() for i in inv_str.split(",") if i.strip() and i.strip().startswith("sex_")]
    
    buttons = []
    for i_key in items:
        i_name = SEX_SHOP.get(i_key, {}).get("name", i_key)
        buttons.append([InlineKeyboardButton(text=f"Использовать: {i_name}", callback_data=f"sex_use_{i_key}")])
    
    buttons.append([InlineKeyboardButton(text="Без игрушек", callback_data="sex_use_none")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    text = f"🍑 Выберите предмет для уединения с партнером {pname}:"
    if isinstance(message_obj, types.CallbackQuery):
        await message_obj.edit_text(text, reply_markup=kb)
    else:
        await message_obj.answer(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("sex_use_"))
async def callback_sex_use_item(callback: types.CallbackQuery):
    try:
        item_key = callback.data.replace("sex_use_", "")
        user_obj = callback.from_user
        uid = str(user_obj.id)
        
        p = await get_profile(user_obj)
        pid, pname = p.get("partner_id"), p.get("partner_name")
        
        if not pid or str(pid) == "0":
            await callback.answer("❌ Вы не в браке!", show_alert=True)
            return
            
        INTIMATE_COOLDOWNS[uid] = time.time()
        coins, xp = random.randint(80, 200), 40
        new_coins, new_xp = p.get("coins", 0) + coins, p.get("xp", 0) + xp
        new_level = p.get("level", 1)
        for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
            if new_xp >= data["xp"]: new_level = lvl
            
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", p["user_id"]).execute())
        except Exception:
            pass

        descriptions = {
            "none": f"Воздух в комнате мгновенно раскаляется от жажды близости когда {user_obj.first_name} прижимает к себе {pname} и страстно впивается в губы срывая остатки одежды. Тела сливаются в единое целое в диком и безудержном ритме под громкие стоны наполняющие каждый угол спальни. Каждое движение пропитано безумной страстью доводя обоих до исступления и дикой сладкой разрядки.",
            "sex_vibe": f"В тишине спальни {user_obj.first_name} берет мощный вибратор и начинает медленно сводить с ума {pname} исследуя каждый сантиметр чувствительного тела. Глубокие вибрации заставляют {pname} выгибаться в дугу и исступленно кричать от накатывающих волн оргазмического экстаза. Страсть перерастает в жесткий и дикий процесс где каждый толчок приносит сокрушительное удовольствие.",
            "sex_gag": f"Кожаный кляп надежно запирает губы {pname} оставляя лишь глухие сладкие стоны в то время как {user_obj.first_name} берет полный контроль над ситуацией. Жесткие и глубокие движения заставляют тело партнера биться в судорогах полного подчинения и восторга. Воздух наполнен запахом пота и раскаленной страсти доведенной до абсолютного предела.",
            "sex_cuff": f"Туго затянутые кожаные наручники фиксируют запястья {pname} к спинке кровати лишая любой возможности сопротивления. {user_obj.first_name} неспешно и властно наслаждается каждым дюймом полностью беспомощного и разгоряченного тела партнера. Глубокие и резкие толчки заставляют комнату дрожать от диких стонов и дикого животного влечения.",
            "sex_maid": f"Соблазнительный костюм горничной на {pname} сводит {user_obj.first_name} с ума с первой же секунды провоцируя на самые смелые фантазии. Отрезвляющая страсть выплескивается наружу в жестком и стремительном ритме когда преграды между партнерами окончательно стираются. Интенсивность движений нарастает с каждой секундой приводя к мощному взрыву удовольствия.",
            "sex_whip": f"Легкие и звонкие удары хлыстом заставляют нежную кожу {pname} покрываться мурашками а кровь бурлить от дикого адреналина. {user_obj.first_name} властно управляет процессом требуя полной отдачи и громких стонов в ответ на каждое движение. Безумная страсть захватывает обоих погружая в пучину греховного и безудержного наслаждения.",
            "sex_oil": f"Тёплое массажное масло щедро растекается по обнаженным телам делая каждое прикосновение {user_obj.first_name} и {pname} невероятно скользким и жгучим. Руки скользят по изгибам вызывая дрожь во всем теле и заставляя дыхание срываться на крик. Процесс превращается в плавное но невероятно жаркое и страстное соитие.",
            "sex_mask": f"Кружевная маска скрывающая лицо {pname} добавляет происходящему атмосферу запретного и тайного греха. {user_obj.first_name} действует жестко и уверенно растворяясь в темноте спальни под звуки тяжелого дыхания и шлепки тел. Страсть достигает своего пика оставляя после себя сладкую истому."
        }

        desc = descriptions.get(item_key, descriptions["none"])
        final_text = f"{desc}\n\nНаграда за уединение: +{coins} монет и +{xp} опыта."
        
        await callback.message.edit_text(final_text)
        await callback.answer("Близость удалась!", show_alert=True)
    except Exception as e:
        logging.error(f"Error in sex action: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@dp.message(Command("me"))
async def cmd_me(message: types.Message, state: FSMContext):
    await state.clear()
    p = await get_profile(message.from_user)
    lvl = p.get('level', 1)
    title = LEVELS.get(lvl, {}).get("title", "Воин")
    pid, pname = p.get("partner_id"), p.get("partner_name")
    
    created_at = int(p.get("created_at") or time.time())
    bot_age = format_age(int(time.time()) - created_at)
    
    if pid and str(pid) != "0" and pname != "EMPTY":
        m_time = int(p.get("marriage_time") or time.time())
        md = format_age(int(time.time()) - m_time)
        marriage = f"💍 В браке с: **{pname}** (уже {md})"
    else:
        marriage = "💍 Статус: Свободен"

    smoke_lvl = p.get('smoking_level', 0)
    smoke_status = f"🚬 Никотиновая зависимость: Уровень `{smoke_lvl}`" if smoke_lvl > 0 else "🚭 Не курит"
    equipped = p.get("equipped_item", "")
    eq_name = SHOP_EQUIPMENT.get(equipped, {}).get("name", "❌ Ничего не надето")
    
    text = (
        f"👤 **Профиль: {p.get('username')}**\n"
        f"⏳ Возраст в боте: `{bot_age}`\n"
        f"⭐ Уровень: `{lvl}` / 67 (*{title}*)\n"
        f"✨ Опыт (XP): `{p.get('xp')}`\n"
        f"🪙 Монеты: `{p.get('coins')}`\n"
        f"❤️ Респект: `{p.get('respect')}`\n"
        f"⚔️ Экипировка: `{eq_name}`\n"
        f"{smoke_status}\n"
        f"{marriage}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Магазины", callback_data=f"menu_shops_{message.from_user.id}"),
         InlineKeyboardButton(text="🎒 Инвентарь", callback_data=f"menu_inv_{message.from_user.id}")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message, state: FSMContext):
    await state.clear()
    p = await get_profile(message.from_user)
    text = f"🛒 **МАГАЗИНЫ БОТА** (Баланс: `{p.get('coins', 0)}` 🪙):"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Снаряжение", callback_data=f"shop_eq_list_{message.from_user.id}"),
         InlineKeyboardButton(text="🍺 Продукты и ПК", callback_data=f"shop_cons_list_{message.from_user.id}")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("inv"))
async def cmd_inv(message: types.Message, state: FSMContext):
    await state.clear()
    p = await get_profile(message.from_user)
    inv_str = p.get("inventory") or ""
    items = [i.strip() for i in inv_str.split(",") if i.strip()]
    if not items:
        await message.answer(f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p.get('coins', 0)}` 🪙):\n\nПусто.", parse_mode=ParseMode.MARKDOWN)
    else:
        text = f"🎒 **Инвентарь игрока {p.get('username')}** (Баланс: `{p.get('coins', 0)}` 🪙):\n\n"
        buttons = []
        for idx, item_key in enumerate(items):
            item_info = SHOP_CONSUMABLES.get(item_key) or SEX_SHOP.get(item_key) or {"name": item_key}
            buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {item_info['name']}", callback_data=f"use_item_{idx}_{item_key}")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("top"))
async def cmd_top(message: types.Message, state: FSMContext):
    await state.clear()
    def _fetch_top():
        return supabase.table("users").select("username, level, coins").order("level", desc=True).limit(10).execute()
    try:
        res = await asyncio.to_thread(_fetch_top)
    except Exception:
        res = None
    text = "🏆 **ТОП-10 ИГРОКОВ:**\n\n"
    if res and res.data:
        for i, u in enumerate(res.data, 1):
            lvl = u.get('level', 1)
            title = LEVELS.get(lvl, {}).get("title", "")
            text += f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙 `{u.get('coins')}`\n"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

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
        text = f"💼 **БИРЖА ТРУДА** (Баланс: `{p.get('coins', 0)}` 🪙):\n"
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
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
    except Exception:
        pass
    await message.answer(f"✅ Вы отработали как **{job['name']}**!\n🪙 `+{earned_coins}` монет\n✨ `+{earned_xp} XP`", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("pay"))
async def cmd_pay(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    if len(args) < 2 or not message.reply_to_message:
        await message.answer("Ответьте на сообщение командой `/pay <сумма>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(args[1])
        if amount <= 0: raise ValueError()
    except ValueError:
        return
    sender = await get_profile(message.from_user)
    if sender.get("coins", 0) < amount:
        await message.answer("Недостаточно монет!")
        return
    receiver_user = message.reply_to_message.from_user
    if receiver_user.id == message.from_user.id: return
    receiver = await get_profile(receiver_user)
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": sender["coins"] - amount}).eq("user_id", sender["user_id"]).execute())
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": receiver["coins"] + amount}).eq("user_id", receiver["user_id"]).execute())
    except Exception:
        pass
    await message.answer(f"💸 Переведено `{amount}` монет **{receiver['username']}**!", parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "+")
async def give_respect(message: types.Message):
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id: return
    p = await get_profile(target)
    new_respect = p.get("respect", 0) + 1
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"respect": new_respect}).eq("user_id", str(target.id)).execute())
    except Exception:
        pass
    await message.answer(f"👍 Респект **{target.first_name}** повышен! (`{new_respect}`)", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "❌ Использование: `/dice <ставка> <числа от 1 до 6>`\n"
            "Пример: `/dice 100 2 5 6`", 
            parse_mode=ParseMode.MARKDOWN
        )
        return
    try:
        bet = int(args[1])
        chosen = []
        for x in args[2:]:
            num = int(x)
            if 1 <= num <= 6 and num not in chosen:
                chosen.append(num)
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
    count = len(chosen)
    mult = {1: 6.0, 2: 3.0, 3: 2.0}[count]
    
    if roll in chosen:
        win = int(bet * mult)
        coins += win
        profit = win - bet
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
        except Exception:
            pass
        await message.answer(f"🎲 Выпало **{roll}**! Вы выиграли `+{profit}` монет (x{mult})! 💰 (Баланс: `{coins}`)", parse_mode=ParseMode.MARKDOWN)
    else:
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
        except Exception:
            pass
        await message.answer(f"🎲 Выпало **{roll}**. Проигрыш `{bet}` монет. 💸 (Баланс: `{coins}`)", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("coin"))
async def cmd_coin(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Использование: `/coin <ставка> <орел/решка>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        bet = int(args[1])
        choice_input = args[2].lower()
        if bet <= 0: raise ValueError()
        user_choice = "орел" if choice_input in ["орел", "о", "head", "heads"] else "решка"
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
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
        except Exception:
            pass
        await message.answer(f"🪙 Выпал **{result}**! Вы выиграли `+{profit}` монет! 🎉 (Баланс: `{coins}`)", parse_mode=ParseMode.MARKDOWN)
    else:
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
        except Exception:
            pass
        await message.answer(f"🪙 Выпал **{result}**. Проигрыш `{bet}` монет. 💸 (Баланс: `{coins}`)", parse_mode=ParseMode.MARKDOWN)

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
    if r1 == 3 and r2 == 3 and r3 == 3:
        multiplier = 10
    elif r1 == 3 and r2 == 3:
        multiplier = 5
    elif r1 == r2 == r3:
        multiplier = 3
    elif r1 == r2:
        multiplier = 2
    else:
        multiplier = 0

    if multiplier > 0:
        win = bet * multiplier
        coins += win
        res_text = f"Выигрыш x{multiplier}! (+{win} 🪙)"
    else:
        res_text = f"Проигрыш (-{bet} 🪙)"
        
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
    except Exception:
        pass
    
    await message.answer(f"{res_text}\n💰 Баланс: `{coins}` 🪙", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("ball"))
async def cmd_ball(message: types.Message, state: FSMContext):
    await state.clear()
    answers = ["Да", "Нет", "Скорее всего да", "Точно нет", "Спроси позже", "Определенно да"]
    await message.answer(f"🎱 Шар говорит: *{random.choice(answers)}*", parse_mode=ParseMode.MARKDOWN)

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

@dp.message(Command("kiss"))
async def cmd_kiss(message: types.Message, state: FSMContext):
    await state.clear()
    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение пользователя командой `/kiss`", parse_mode=ParseMode.MARKDOWN)
        return
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id: return
    await message.answer(f"💋 **{message.from_user.first_name}** целует **{target.first_name}**! 💕", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("marry"))
async def cmd_marry(message: types.Message, state: FSMContext):
    await state.clear()
    if not message.reply_to_message:
        await message.answer("💍 Ответьте на сообщение пользователя командой `/marry`.", parse_mode=ParseMode.MARKDOWN)
        return
    target_user = message.reply_to_message.from_user
    if target_user.id == message.from_user.id: return
    sender = await get_profile(message.from_user)
    if sender.get("partner_id") and str(sender.get("partner_id")) != "0":
        await message.answer("💍 Вы уже в браке!")
        return
    target = await get_profile(target_user)
    if target.get("partner_id") and str(target.get("partner_id")) != "0":
        await message.answer("💍 Пользователь уже занят!")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Принять", callback_data=f"marry_accept_{message.from_user.id}"),
         InlineKeyboardButton(text="💔 Отказаться", callback_data=f"marry_reject_{message.from_user.id}")]
    ])
    await message.answer(f"💍 **{message.from_user.first_name}** делает предложение **{target_user.first_name}**!", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("marry_"))
async def callback_marry(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        data_parts = callback.data.split("_")
        action, proposer_id = data_parts[1], int(data_parts[2])
        accepter = callback.from_user
        if accepter.id == proposer_id:
            await callback.answer("Нельзя ответить на свое предложение!", show_alert=True)
            return
        
        def _fetch_prop():
            return supabase.table("users").select("*").eq("user_id", str(proposer_id)).execute()
        try:
            proposer_res = await asyncio.to_thread(_fetch_prop)
        except Exception:
            proposer_res = None
            
        if not proposer_res or not proposer_res.data:
            await callback.message.edit_text("💔 Инициатор не найден.")
            return
        proposer_data = proposer_res.data[0]

        if action == "reject":
            await callback.message.edit_text(f"💔 **{accepter.first_name}** отклонил(а) предложение.")
            return

        now = int(time.time())
        try:
            await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": str(accepter.id), "partner_name": accepter.first_name, "marriage_time": now}).eq("user_id", str(proposer_id)).execute())
            await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": str(proposer_id), "partner_name": proposer_data["username"], "marriage_time": now}).eq("user_id", str(accepter.id)).execute())
        except Exception:
            pass
        await callback.message.edit_text(f"🎉 Горько! **{proposer_data['username']}** и **{accepter.first_name}** поженились! 💍❤️")
    except Exception as e:
        logging.error(f"Error in marry callback: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.message(Command("partner"))
async def cmd_partner(message: types.Message, state: FSMContext):
    await state.clear()
    p = await get_profile(message.from_user)
    pid, pname = p.get("partner_id"), p.get("partner_name")
    if not pid or str(pid) == "0" or not pname or pname == "EMPTY":
        await message.answer("💍 У вас нет партнера.", parse_mode=ParseMode.MARKDOWN)
    else:
        m_time = int(p.get("marriage_time") or time.time())
        md = format_age(int(time.time()) - m_time)
        await message.answer(f"💍 Вторая половинка: **{pname}** ❤️\n⏳ В браке уже: `{md}`", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message, state: FSMContext):
    await state.clear()
    p = await get_profile(message.from_user)
    pid = p.get("partner_id")
    if not pid or str(pid) == "0":
        await message.answer("💔 Вы не в браке.", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY", "marriage_time": 0}).eq("user_id", str(pid)).execute())
        await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY", "marriage_time": 0}).eq("user_id", p["user_id"]).execute())
    except Exception:
        pass
    await message.answer("💔 Развод оформлен.", parse_mode=ParseMode.MARKDOWN)

async def verify_admin(message: types.Message) -> bool:
    if not is_admin(message.from_user):
        await message.answer("❌ Нет прав.")
        return False
    if not message.reply_to_message:
        await message.answer("⚠️ Сделайте реплай на сообщение игрока!")
        return False
    return True

@dp.message(Command("add_coins"))
async def admin_add_coins(message: types.Message, state: FSMContext):
    await state.clear()
    if not await verify_admin(message): return
    amount = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": target["coins"] + amount}).eq("user_id", target["user_id"]).execute())
    except Exception:
        pass
    await message.answer(f"🛡 Добавлено `{amount}` монет.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("set_coins"))
async def admin_set_coins(message: types.Message, state: FSMContext):
    await state.clear()
    if not await verify_admin(message): return
    amount = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": amount}).eq("user_id", target["user_id"]).execute())
    except Exception:
        pass
    await message.answer(f"🛡 Баланс установлен на `{amount}`.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("add_xp"))
async def admin_add_xp(message: types.Message, state: FSMContext):
    await state.clear()
    if not await verify_admin(message): return
    amount = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    new_xp = target.get("xp", 0) + amount
    new_lvl = target.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]: new_lvl = lvl
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"xp": new_xp, "level": new_lvl}).eq("user_id", target["user_id"]).execute())
    except Exception:
        pass
    await message.answer(f"🛡 Добавлено `+{amount} XP`.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("set_level"))
async def admin_set_level(message: types.Message, state: FSMContext):
    await state.clear()
    if not await verify_admin(message): return
    lvl = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    req_xp = LEVELS[lvl]["xp"]
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"level": lvl, "xp": req_xp}).eq("user_id", target["user_id"]).execute())
    except Exception:
        pass
    await message.answer(f"🛡 Уровень изменен на `{lvl}`.", parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text)
async def process_message_xp(message: types.Message, state: FSMContext):
    if message.text.startswith("/"): return
    current_state = await state.get_state()
    if current_state in [FamilyState.waiting_for_child_name.state, FamilyState.waiting_for_deposit_amount.state, ProfileState.waiting_for_music.state]:
        return
        
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    new_xp = p.get("xp", 0) + 5
    new_level = p.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]: new_level = lvl
    if new_level > p.get("level", 1):
        await message.answer(f"🎉 Уровень **{message.from_user.first_name}** повышен до `{new_level}`!", parse_mode=ParseMode.MARKDOWN)
    try:
        await asyncio.to_thread(lambda: supabase.table("users").update({"xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
    except Exception:
        pass

async def handle_ping(request):
    return web.Response(text="Бот работает!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()

async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню с кнопками"),
        BotCommand(command="me", description="Профиль игрока"),
        BotCommand(command="shop", description="Магазины"),
        BotCommand(command="inv", description="Инвентарь"),
        BotCommand(command="top", description="Топ игроков"),
        BotCommand(command="work", description="Биржа труда"),
        BotCommand(command="marry", description="Предложение брака"),
        BotCommand(command="partner", description="Моя пара"),
        BotCommand(command="help", description="Справка"),
    ])
    asyncio.create_task(web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
