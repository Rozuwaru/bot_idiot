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
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAH6TPW93SufV2pRi0Ng9AHuEmqOEmqfLnI"
SUPABASE_URL = "https://cbypocbgeevwqhjahchy.supabase.co"
SUPABASE_KEY = "sb_publishable_zcF4S765sEmvXLIQegRkFg_1el4gZn_".strip()

ADMIN_USERNAMES = {"p0tat0777"}

logging.basicConfig(level=logging.INFO)

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
INTIMATE_COOLDOWNS = {}

JOBS = {
    "1": {"name": "⛏ Шахтёр", "min_coins": 40, "max_coins": 90, "xp": 10},
    "2": {"name": "🛡 Стражник", "min_coins": 60, "max_coins": 130, "xp": 15},
    "3": {"name": "🧪 Алхимик", "min_coins": 90, "max_coins": 180, "xp": 22},
    "4": {"name": "🐉 Охотник на чудовищ", "min_coins": 130, "max_coins": 260, "xp": 30},
}

SHOP_EQUIPMENT = {
    "eq_1": {"name": "🪵 Деревянный меч", "price": 150, "effect_type": "xp", "value": 30, "desc": "Дает +30 XP."},
    "eq_2": {"name": "⚔️ Железный меч", "price": 350, "effect_type": "xp", "value": 90, "desc": "Дает +90 XP."},
    "eq_3": {"name": "🛡 Кожаная броня", "price": 250, "effect_type": "respect", "value": 2, "desc": "Дает +2 респекта."},
    "eq_4": {"name": "🧪 Зелье здоровья", "price": 120, "effect_type": "xp", "value": 45, "desc": "Дает +45 XP."},
    "eq_5": {"name": "💍 Руническое кольцо", "price": 600, "effect_type": "respect", "value": 6, "desc": "Дает +6 респекта."},
}

SHOP_CONSUMABLES = {
    "beer_okhota": {"name": "🍺 Охота Крепкое", "price": 120, "desc": "Легендарное пиво. Мут на 2 мин + рандом монет."},
    "energy": {"name": "⚡ Энергетик", "price": 90, "desc": "Дает +50 XP при открытии."},
    "pizza": {"name": "🍔 Пицца", "price": 80, "desc": "Вкусная еда (+30 XP и +20 монет)."},
    "vodka": {"name": "🥃 Паленая водка", "price": 200, "desc": "Жесткий напиток. Мут на 5 мин и риск потерять/удвоить монеты."},
    "pc": {"name": "💻 Игровой ПК", "price": 3500, "desc": "Топовая сборка. Дает +150 респекта при распаковке."},
    "cigars": {"name": "🚬 Сигареты", "price": 100, "desc": "Добавляет авторитета (+5 респекта)."},
}

# Справочники для семейных покупок
APARTMENTS_CAT = {
    "apt_studio": {"name": "🏢 Студия на окраине", "price": 1200},
    "apt_1k": {"name": "🏢 1-комнатная квартира", "price": 2500},
    "apt_3k": {"name": "🏢 3-комнатная в центре", "price": 5500},
    "apt_penthouse": {"name": "🏢 Элитный пентхаус", "price": 15000},
}

HOUSES_CAT = {
    "house_dacha": {"name": "🏡 Дачный домик", "price": 4000},
    "house_cottage": {"name": "🏡 Загородный коттедж", "price": 10000},
    "house_villa": {"name": "🏡 Элитная вилла с бассейном", "price": 30000},
}

CARS_CAT = {
    "car_old": {"name": "🚗 Старая ВАЗ (Б/У)", "price": 900},
    "car_sedan": {"name": "🚗 Городской седан", "price": 3000},
    "car_suv": {"name": "🚗 Семейный кроссовер", "price": 8000},
    "car_sport": {"name": "🏎 Спортивный суперкар", "price": 22000},
}

def is_admin(user: types.User) -> bool:
    if not user or not user.username:
        return False
    return user.username.lower() in {u.lower() for u in ADMIN_USERNAMES}

async def get_profile(user: types.User):
    uid = str(user.id)
    def _fetch():
        return supabase.table("users").select("*").eq("user_id", uid).execute()
    response = await asyncio.to_thread(_fetch)
    if response.data:
        return response.data[0]

    new_user = {
        "user_id": uid,
        "username": user.username or user.first_name,
        "coins": 100, "xp": 0, "level": 1, "respect": 0,
        "partner_id": 0, "partner_name": "EMPTY",
        "inventory": ""
    }
    def _insert():
        return supabase.table("users").insert(new_user).execute()
    res = await asyncio.to_thread(_insert)
    return res.data[0] if res.data else new_user

async def get_or_create_family(uid1: str, uid2: str):
    uids = sorted([str(uid1), str(uid2)])
    fam_id = f"{uids[0]}_{uids[1]}"
    
    def _fetch():
        return supabase.table("families").select("*").eq("family_id", fam_id).execute()
    
    res = await asyncio.to_thread(_fetch)
    if res.data:
        return res.data[0]
    
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
        "child_hunger": 100
    }
    def _insert():
        return supabase.table("families").insert(new_fam).execute()
    
    ins_res = await asyncio.to_thread(_insert)
    return ins_res.data[0] if ins_res.data else new_fam

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile"),
         InlineKeyboardButton(text="🎒 Инвентарь", callback_data="menu_inv")],
        [InlineKeyboardButton(text="🛒 Магазины", callback_data="menu_shops"),
         InlineKeyboardButton(text="🏆 Топ игроков", callback_data="menu_top")],
        [InlineKeyboardButton(text="💼 Биржа труда", callback_data="menu_work"),
         InlineKeyboardButton(text="🎰 Казино и игры", callback_data="menu_casino")],
        [InlineKeyboardButton(text="💍 Отношения и Семья", callback_data="menu_marry")]
    ])

@dp.message(Command(commands=["start", "help", "menu"]))
async def cmd_start(message: types.Message):
    await get_profile(message.from_user)
    text = (
        "🎮 **ДОБРО ПОЖАЛОВАТЬ В RPG БОТ!**\n\n"
        "Используйте кнопки ниже для управления персонажем, покупки товаров и участия в развлечениях."
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("menu_"))
async def callback_main_menu(callback: types.CallbackQuery):
    try:
        action = callback.data.split("_")[1]
        p = await get_profile(callback.from_user)
        
        if action == "profile":
            lvl = p.get('level', 1)
            title = LEVELS.get(lvl, {}).get("title", "Воин")
            pid, pname = p.get("partner_id"), p.get("partner_name")
            marriage = f"💍 В браке с: **{pname}**" if pid and str(pid) != "0" and pname != "EMPTY" else "💍 Статус: Свободен"
            
            text = (
                f"👤 **Профиль: {p.get('username')}**\n"
                f"⭐ Уровень: `{lvl}` / 67 (*{title}*)\n"
                f"✨ Опыт (XP): `{p.get('xp')}`\n"
                f"🪙 Монеты: `{p.get('coins')}`\n"
                f"❤️ Респект: `{p.get('respect')}`\n"
                f"{marriage}"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Обновить", callback_data="menu_profile"),
                 InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]
            ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "inv":
            inv_str = p.get("inventory") or ""
            items = [i.strip() for i in inv_str.split(",") if i.strip()]
            
            if not items:
                text = f"🎒 **Инвентарь игрока {p.get('username')}:**\n\nВаш инвентарь пуст."
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]])
            else:
                text = f"🎒 **Инвентарь игрока {p.get('username')}:**\nНажмите на предмет, чтобы применить его эффект:\n\n"
                buttons = []
                for idx, item_key in enumerate(items):
                    item_info = SHOP_CONSUMABLES.get(item_key, {"name": item_key})
                    buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {item_info['name']}", callback_data=f"use_item_{idx}_{item_key}")])
                buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")])
                kb = InlineKeyboardMarkup(inline_keyboard=buttons)
                
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "shops":
            text = "🛒 **ВЫБЕРИТЕ МАГАЗИН:**"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Снаряжение (авто-эффект)", callback_data="shop_eq_list")],
                [InlineKeyboardButton(text="🍺 Продукты и ПК (в инвентарь)", callback_data="shop_cons_list")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]
            ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "top":
            def _fetch_top():
                return supabase.table("users").select("username, level, coins").order("level", desc=True).limit(10).execute()
            res = await asyncio.to_thread(_fetch_top)
            text = "🏆 **ТОП-10 ИГРОКОВ:**\n\n"
            if res.data:
                for i, u in enumerate(res.data, 1):
                    lvl = u.get('level', 1)
                    title = LEVELS.get(lvl, {}).get("title", "")
                    text += f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙 `{u.get('coins')}`\n"
            else:
                text += "Игроков пока нет."
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "work":
            text = "💼 **БИРЖА ТРУДА:**\n\nВыберите смену:"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⛏ Шахтёр (40-90 🪙)", callback_data="do_work_1")],
                [InlineKeyboardButton(text="🛡 Стражник (60-130 🪙)", callback_data="do_work_2")],
                [InlineKeyboardButton(text="🧪 Алхимик (90-180 🪙)", callback_data="do_work_3")],
                [InlineKeyboardButton(text="🐉 Охотник (130-260 🪙)", callback_data="do_work_4")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]
            ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "casino":
            text = (
                "🎰 **КАЗИНО И ИГРЫ:**\n\n"
                "Используйте команды в чате с нативной анимацией Telegram:\n"
                "• `/dice <ставка> <числа 1-6>` (Бросок кубика)\n"
                "• `/slots <ставка>` (Игровой автомат / слоты)"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        elif action == "marry":
            pid, pname = p.get("partner_id"), p.get("partner_name")
            if pid and str(pid) != "0" and pname != "EMPTY":
                text = f"💍 **СЕМЕЙНЫЙ ОЧАГ И ОТНОШЕНИЯ:**\n\n💍 В браке с: **{pname}**"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏡 Меню семьи", callback_data="family_main"),
                     InlineKeyboardButton(text="🔥 Уединиться (/sex)", callback_data="action_sex")],
                    [InlineKeyboardButton(text="💔 Развестись (/divorce)", callback_data="action_divorce"),
                     InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]
                ])
            else:
                text = f"💍 **ОТНОШЕНИЯ И СЕМЬЯ:**\n\n💍 Вы свободны. Сделайте предложение через реплай и `/marry`"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]
                ])
            await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in callback_main_menu: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

# --- РАСШИРЕННОЕ МЕНЮ СЕМЬИ ---
@dp.callback_query(F.data == "family_main")
async def callback_family_main(callback: types.CallbackQuery):
    try:
        p = await get_profile(callback.from_user)
        pid = p.get("partner_id")
        if not pid or str(pid) == "0":
            await callback.answer("❌ Доступно только для женатых пар!", show_alert=True)
            return
        
        fam = await get_or_create_family(callback.from_user.id, pid)
        
        text = (
            f"🏡 **СЕМЕЙНЫЙ ОЧАГ И ИМУЩЕСТВО**\n\n"
            f"💵 Бюджет семьи: `{fam['budget']}` 🪙\n"
            f"🍔 Запасы еды: `{fam['food']}` ед.\n"
            f"🏠 Дом: `{fam['house']}`\n"
            f"🏢 Квартира: `{fam['apartment']}`\n"
            f"🚗 Машина: `{fam['car']}`\n"
            f"👶 Ребенок: `{fam['child_name']}` (Сытость: `{fam['child_hunger']}/100`)\n\n"
            f"👇 Выберите категорию покупок или действий:"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💵 Вложить 100 🪙", callback_data="fam_deposit"),
             InlineKeyboardButton(text="🍔 Купить еду (50 🪙)", callback_data="fam_buy_food")],
            [InlineKeyboardButton(text="🏢 Выбрать квартиру", callback_data="fam_shop_apt"),
             InlineKeyboardButton(text="🏡 Выбрать дом", callback_data="fam_shop_house")],
            [InlineKeyboardButton(text="🚗 Выбрать машину", callback_data="fam_shop_car"),
             InlineKeyboardButton(text="👶 Завести ребенка (1000 🪙)", callback_data="fam_buy_child")],
            [InlineKeyboardButton(text="🍼 Покормить ребенка", callback_data="fam_feed_child"),
             InlineKeyboardButton(text="🧸 Поиграть с ребенком", callback_data="fam_play_child")],
            [InlineKeyboardButton(text="🔙 Назад к отношениям", callback_data="menu_marry")]
        ])
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in family_main: {e}")
        await callback.answer("❌ Ошибка при открытии меню семьи!", show_alert=True)

# Магазин квартир
@dp.callback_query(F.data == "fam_shop_apt")
async def fam_shop_apt(callback: types.CallbackQuery):
    buttons = []
    for k, v in APARTMENTS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"fam_buy_item_apt_{k}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в семью", callback_data="family_main")])
    await callback.message.edit_text("🏢 **РЫНОК КВАРТИР:**\nВыберите вариант для покупки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

# Магазин домов
@dp.callback_query(F.data == "fam_shop_house")
async def fam_shop_house(callback: types.CallbackQuery):
    buttons = []
    for k, v in HOUSES_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"fam_buy_item_house_{k}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в семью", callback_data="family_main")])
    await callback.message.edit_text("🏡 **РЫНОК ДОМОВ И ВИЛЛ:**\nВыберите загородную недвижимость:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

# Магазин машин
@dp.callback_query(F.data == "fam_shop_car")
async def fam_shop_car(callback: types.CallbackQuery):
    buttons = []
    for k, v in CARS_CAT.items():
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']} 🪙", callback_data=f"fam_buy_item_car_{k}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в семью", callback_data="family_main")])
    await callback.message.edit_text("🚗 **АВТОСАЛОН:**\nВыберите семейный автомобиль:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("fam_buy_item_"))
async def fam_buy_specific_item(callback: types.CallbackQuery):
    try:
        parts = callback.data.replace("fam_buy_item_", "").split("_", 1)
        category = parts[0] # apt, house, car
        item_key = f"{parts[0]}_{parts[1]}"
        
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
        await asyncio.to_thread(lambda: supabase.table("families").update({
            "budget": new_budget,
            col_name: item_data["name"]
        }).eq("family_id", fam_id).execute())
        
        await callback.answer(f"🎉 Успешно приобретено: {item_data['name']}!", show_alert=True)
        await callback_family_main(callback)
    except Exception as e:
        logging.error(f"Error buying item: {e}")
        await callback.answer("❌ Ошибка при покупке!", show_alert=True)

@dp.callback_query(F.data.startswith("fam_"))
async def callback_family_actions(callback: types.CallbackQuery):
    try:
        action = callback.data.split("_")[1]
        p = await get_profile(callback.from_user)
        pid = p.get("partner_id")
        if not pid or str(pid) == "0":
            await callback.answer("❌ Вы не в браке!", show_alert=True)
            return
            
        fam = await get_or_create_family(callback.from_user.id, pid)
        fam_id = fam["family_id"]
        coins = p.get("coins", 0)
        
        if action == "deposit":
            if coins < 100:
                await callback.answer("❌ У вас недостаточно монет (нужно 100 🪙)!", show_alert=True)
                return
            new_coins = coins - 100
            new_budget = fam["budget"] + 100
            await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins}).eq("user_id", p["user_id"]).execute())
            await asyncio.to_thread(lambda: supabase.table("families").update({"budget": new_budget}).eq("family_id", fam_id).execute())
            await callback.answer("✅ Вы успешно внесли 100 монет в семейный бюджет!", show_alert=True)
            
        elif action == "buy" and callback.data.split("_")[2] == "food":
            if fam["budget"] < 50:
                await callback.answer("❌ В семейном бюджете недостаточно средств (нужно 50 🪙)!", show_alert=True)
                return
            await asyncio.to_thread(lambda: supabase.table("families").update({
                "budget": fam["budget"] - 50,
                "food": fam["food"] + 20
            }).eq("family_id", fam_id).execute())
            await callback.answer("✅ Куплено 20 ед. продуктов в семью!", show_alert=True)
                
        elif action == "buy" and callback.data.split("_")[2] == "child":
            if fam["child_name"] != "❌ Нет":
                await callback.answer("⚠️ У вас уже есть ребенок!", show_alert=True)
                return
            if fam["budget"] < 1000:
                await callback.answer("❌ Нужно 1000 🪙 в семейном бюджете на расходы по рождению!", show_alert=True)
                return
            child_names = ["Тони", "Алиса", "Максим", "София", "Артем", "Милана"]
            c_name = random.choice(child_names)
            await asyncio.to_thread(lambda: supabase.table("families").update({
                "budget": fam["budget"] - 1000,
                "child_name": c_name,
                "child_hunger": 100
            }).eq("family_id", fam_id).execute())
            await callback.answer(f"👶 У вас родился замечательный ребенок: {c_name}!", show_alert=True)
                
        elif action == "feed":
            if fam["child_name"] == "❌ Нет":
                await callback.answer("❌ У вас пока нет детей!", show_alert=True)
                return
            if fam["food"] < 10:
                await callback.answer("❌ В семье закончилась еда! Купите продукты в меню семьи.", show_alert=True)
                return
            new_hunger = min(100, fam["child_hunger"] + 35)
            await asyncio.to_thread(lambda: supabase.table("families").update({
                "food": fam["food"] - 10,
                "child_hunger": new_hunger
            }).eq("family_id", fam_id).execute())
            await callback.answer(f"🍼 Вы покормили ребенка. Сытость: {new_hunger}/100", show_alert=True)
            
        elif action == "play":
            if fam["child_name"] == "❌ Нет":
                await callback.answer("❌ У вас пока нет детей!", show_alert=True)
                return
            await callback.answer(f"🧸 Вы поиграли с ребенком {fam['child_name']}. Он очень доволен!", show_alert=True)
            
        await callback_family_main(callback)
    except Exception as e:
        logging.error(f"Error in family actions: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.callback_query(F.data == "shop_eq_list")
async def callback_shop_eq(callback: types.CallbackQuery):
    try:
        text = "⚔️ **СНАРЯЖЕНИЕ (эффект сразу):**\n\n"
        buttons = []
        for item_id, data in SHOP_EQUIPMENT.items():
            buttons.append([InlineKeyboardButton(text=f"{data['name']} — {data['price']} 🪙", callback_data=f"buy_eq_{item_id}")])
        buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data="menu_shops")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in shop_eq_list: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.callback_query(F.data == "shop_cons_list")
async def callback_shop_cons(callback: types.CallbackQuery):
    try:
        text = "🍺 **ПРОДУКТЫ И ТЕХНИКА (в инвентарь):**\n\n"
        buttons = []
        for item_id, data in SHOP_CONSUMABLES.items():
            buttons.append([InlineKeyboardButton(text=f"{data['name']} — {data['price']} 🪙", callback_data=f"buy_cons_{item_id}")])
        buttons.append([InlineKeyboardButton(text="🔙 К магазинам", callback_data="menu_shops")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in shop_cons_list: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.callback_query(F.data.startswith("buy_eq_"))
async def callback_buy_eq(callback: types.CallbackQuery):
    try:
        item_id = callback.data.replace("buy_eq_", "", 1)
        item = SHOP_EQUIPMENT[item_id]
        p = await get_profile(callback.from_user)
        
        if p.get("coins", 0) < item["price"]:
            await callback.answer("❌ Недостаточно монет!", show_alert=True)
            return
            
        new_coins = p["coins"] - item["price"]
        new_xp, new_respect = p.get("xp", 0), p.get("respect", 0)
        if item["effect_type"] == "xp": new_xp += item["value"]
        elif item["effect_type"] == "respect": new_respect += item["value"]
        
        new_level = p.get("level", 1)
        for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
            if new_xp >= data["xp"]: new_level = lvl
            
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "respect": new_respect, "level": new_level}).eq("user_id", p["user_id"]).execute())
        await callback.answer(f"✅ Куплено: {item['name']}!", show_alert=True)
    except Exception as e:
        logging.error(f"Error in buy_eq: {e}")
        await callback.answer("❌ Ошибка при покупке!", show_alert=True)

@dp.callback_query(F.data.startswith("buy_cons_"))
async def callback_buy_cons(callback: types.CallbackQuery):
    try:
        item_id = callback.data.replace("buy_cons_", "", 1)
        item = SHOP_CONSUMABLES[item_id]
        p = await get_profile(callback.from_user)
        
        if p.get("coins", 0) < item["price"]:
            await callback.answer("❌ Недостаточно монет!", show_alert=True)
            return
            
        new_coins = p["coins"] - item["price"]
        current_inv = p.get("inventory") or ""
        updated_inv = f"{current_inv},{item_id}" if current_inv else item_id
        
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "inventory": updated_inv}).eq("user_id", p["user_id"]).execute())
        await callback.answer(f"✅ {item['name']} добавлен в инвентарь!", show_alert=True)
    except Exception as e:
        logging.error(f"Error in buy_cons: {e}")
        await callback.answer("❌ Ошибка! Убедитесь, что в Supabase создана колонка inventory.", show_alert=True)

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
            
        items.pop(item_idx)
        new_inv_str = ",".join(items)
        
        uid = p["user_id"]
        coins = p.get("coins", 0)
        xp = p.get("xp", 0)
        respect = p.get("respect", 0)
        
        effect_message = ""
        
        if item_key == "beer_okhota":
            effect_message = "🍺 Вы выпили «Охота Крепкое»! Расслабон."
            try:
                if callback.message.chat.type in ["group", "supergroup"]:
                    await bot.restrict_chat_member(
                        chat_id=callback.message.chat.id,
                        user_id=callback.from_user.id,
                        permissions=types.ChatPermissions(can_send_messages=False),
                        until_date=int(time.time()) + 120
                    )
                    effect_message += " 🔇 (Мут в чате на 2 минуты!)"
            except Exception:
                pass
            coins += random.randint(20, 80)
            
        elif item_key == "energy":
            effect_message = "⚡ Вы выпили энергетик! Прилив сил: +50 XP."
            xp += 50
            
        elif item_key == "pizza":
            effect_message = "🍔 Вы съели пиццу! +30 XP и +20 монет."
            xp += 30
            coins += 20
            
        elif item_key == "vodka":
            effect_message = "🥃 Вы хлопнули паленой водки!"
            try:
                if callback.message.chat.type in ["group", "supergroup"]:
                    await bot.restrict_chat_member(
                        chat_id=callback.message.chat.id,
                        user_id=callback.from_user.id,
                        permissions=types.ChatPermissions(can_send_messages=False),
                        until_date=int(time.time()) + 300
                    )
                    effect_message += " 🔇 (Лютющий мут на 5 минут!)"
            except Exception:
                pass
            if random.random() > 0.5:
                change = random.randint(50, 150)
                coins += change
                effect_message += f" Удача! Нашли еще +{change} 🪙."
            else:
                loss = min(coins, 100)
                coins -= loss
                effect_message += f" Жесть... Потеряли {loss} 🪙 на похмелье."
                
        elif item_key == "pc":
            effect_message = "💻 Игровой ПК установлен! +150 респекта."
            respect += 150
            
        elif item_key == "cigars":
            effect_message = "🚬 Сигарета выкурена. Авторитет вырос: +5 респекта."
            respect += 5
            
        new_level = p.get("level", 1)
        for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
            if xp >= data["xp"]: new_level = lvl

        await asyncio.to_thread(lambda: supabase.table("users").update({
            "coins": coins, "xp": xp, "respect": respect, "level": new_level, "inventory": new_inv_str
        }).eq("user_id", uid).execute())
        
        await callback.answer(effect_message, show_alert=True)
        
        p_updated = await get_profile(callback.from_user)
        items_up = [i.strip() for i in (p_updated.get("inventory") or "").split(",") if i.strip()]
        if not items_up:
            text = f"🎒 **Инвентарь игрока {p.get('username')}:**\n\nИнвентарь пуст."
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]])
        else:
            text = f"🎒 **Инвентарь игрока {p.get('username')}:**\n\n"
            buttons = []
            for idx, i_key in enumerate(items_up):
                i_info = SHOP_CONSUMABLES.get(i_key, {"name": i_key})
                buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {i_info['name']}", callback_data=f"use_item_{idx}_{i_key}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")])
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
            
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
        await callback.answer(f"✅ Смена окончена! +{earned_coins} 🪙, +{earned_xp} XP", show_alert=True)
    except Exception as e:
        logging.error(f"Error in do_work: {e}")
        await callback.answer("❌ Ошибка при работе!", show_alert=True)

@dp.callback_query(F.data == "action_sex")
async def callback_action_sex(callback: types.CallbackQuery):
    try:
        uid = str(callback.from_user.id)
        p = await get_profile(callback.from_user)
        pid, pname = p.get("partner_id"), p.get("partner_name")
        
        if not pid or str(pid) == "0" or not pname or pname == "EMPTY":
            await callback.answer("🛏️ Доступно только в браке!", show_alert=True)
            return
            
        now = time.time()
        if now - INTIMATE_COOLDOWNS.get(uid, 0) < 600:
            rem = int(600 - (now - INTIMATE_COOLDOWNS.get(uid, 0)))
            await callback.answer(f"⏳ Отдохните еще {rem // 60} мин.", show_alert=True)
            return
            
        INTIMATE_COOLDOWNS[uid] = now
        coins, xp = random.randint(50, 150), 25
        new_coins, new_xp = p.get("coins", 0) + coins, p.get("xp", 0) + xp
        new_level = p.get("level", 1)
        for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
            if new_xp >= data["xp"]: new_level = lvl
            
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
        
        announcement = (
            f"🔥 **ВНИМАНИЕ ВСЕМ!** 🔥\n"
            f"В этом чате только что произошел страстный половой акт между **{callback.from_user.first_name}** и **{pname}**! 🛲💦\n"
            f"🪙 Оба участника получили порцию страсти (+{coins} монет, +{xp} XP)!"
        )
        await callback.message.answer(announcement, parse_mode=ParseMode.MARKDOWN)
        await callback.answer("✅ Успешно!", show_alert=False)
    except Exception as e:
        logging.error(f"Error in action_sex: {e}")
        await callback.answer("❌ Ошибка!", show_alert=True)

@dp.callback_query(F.data == "action_divorce")
async def callback_action_divorce(callback: types.CallbackQuery):
    try:
        p = await get_profile(callback.from_user)
        pid = p.get("partner_id")
        if not pid or str(pid) == "0":
            await callback.answer("💔 Вы не в браке.", show_alert=True)
            return
        await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY"}).eq("user_id", str(pid)).execute())
        await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY"}).eq("user_id", p["user_id"]).execute())
        await callback.message.edit_text("💔 Развод успешно оформлен.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="back_home")]]))
    except Exception as e:
        logging.error(f"Error in divorce: {e}")
        await callback.answer("❌ Ошибка при разводе!", show_alert=True)

# --- ТЕКСТОВЫЕ КОМАНДЫ ---
@dp.message(Command("me"))
async def cmd_me(message: types.Message):
    p = await get_profile(message.from_user)
    lvl = p.get('level', 1)
    title = LEVELS.get(lvl, {}).get("title", "Воин")
    pid, pname = p.get("partner_id"), p.get("partner_name")
    marriage = f"💍 В браке с: **{pname}**" if pid and str(pid) != "0" and pname != "EMPTY" else "💍 Статус: Свободен"
    
    text = (
        f"👤 **Профиль: {p.get('username')}**\n"
        f"⭐ Уровень: `{lvl}` / 67 (*{title}*)\n"
        f"✨ Опыт (XP): `{p.get('xp')}`\n"
        f"🪙 Монеты: `{p.get('coins')}`\n"
        f"❤️ Респект: `{p.get('respect')}`\n"
        f"{marriage}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Магазины", callback_data="menu_shops"),
         InlineKeyboardButton(text="🎒 Инвентарь", callback_data="menu_inv")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    text = "🛒 **МАГАЗИНЫ БОТА:**"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Снаряжение", callback_data="shop_eq_list"),
         InlineKeyboardButton(text="🍺 Продукты и ПК", callback_data="shop_cons_list")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("inv"))
async def cmd_inv(message: types.Message):
    p = await get_profile(message.from_user)
    inv_str = p.get("inventory") or ""
    items = [i.strip() for i in inv_str.split(",") if i.strip()]
    if not items:
        await message.answer(f"🎒 **Инвентарь игрока {p.get('username')}:**\n\nПусто.", parse_mode=ParseMode.MARKDOWN)
    else:
        text = f"🎒 **Инвентарь игрока {p.get('username')}:**\n\n"
        buttons = []
        for idx, item_key in enumerate(items):
            item_info = SHOP_CONSUMABLES.get(item_key, {"name": item_key})
            buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {item_info['name']}", callback_data=f"use_item_{idx}_{item_key}")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    def _fetch_top():
        return supabase.table("users").select("username, level, coins").order("level", desc=True).limit(10).execute()
    res = await asyncio.to_thread(_fetch_top)
    text = "🏆 **ТОП-10 ИГРОКОВ:**\n\n"
    if res.data:
        for i, u in enumerate(res.data, 1):
            lvl = u.get('level', 1)
            title = LEVELS.get(lvl, {}).get("title", "")
            text += f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙 `{u.get('coins')}`\n"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("work"))
async def cmd_work(message: types.Message):
    args = message.text.split()
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    now = time.time()
    if now - WORK_COOLDOWNS.get(uid, 0) < 60:
        await message.answer(f"⏳ Отдохните еще `{int(60 - (now - WORK_COOLDOWNS.get(uid, 0)))}` сек.", parse_mode=ParseMode.MARKDOWN)
        return
    if len(args) < 2 or args[1] not in JOBS:
        text = "💼 **БИРЖА ТРУДА:**\n"
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
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
    await message.answer(f"✅ Вы отработали как **{job['name']}**!\n🪙 `+{earned_coins}` монет\n✨ `+{earned_xp} XP`", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
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
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": sender["coins"] - amount}).eq("user_id", sender["user_id"]).execute())
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": receiver["coins"] + amount}).eq("user_id", receiver["user_id"]).execute())
    await message.answer(f"💸 Переведено `{amount}` монет **{receiver['username']}**!", parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "+")
async def give_respect(message: types.Message):
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id: return
    p = await get_profile(target)
    new_respect = p.get("respect", 0) + 1
    await asyncio.to_thread(lambda: supabase.table("users").update({"respect": new_respect}).eq("user_id", str(target.id)).execute())
    await message.answer(f"👍 Респект **{target.first_name}** повышен! (`{new_respect}`)", parse_mode=ParseMode.MARKDOWN)

# --- НАТИВНЫЕ АНИМАЦИИ ДАЙСА И СЛОТОВ ---
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Использование: `/dice <ставка> <числа 1-6>`\nПример: `/dice 100 3 4 5`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        bet = int(args[1])
        chosen = list(set([int(x) for x in args[2:]]))
        if bet <= 0 or any(n < 1 or n > 6 for n in chosen): raise ValueError()
    except ValueError:
        await message.answer("❌ Неверная ставка или числа! Числа должны быть от 1 до 6.", parse_mode=ParseMode.MARKDOWN)
        return
        
    p = await get_profile(message.from_user)
    if p.get("coins", 0) < bet:
        await message.answer("❌ У вас недостаточно монет!")
        return
        
    dice_msg = await message.answer_dice(emoji="🎲")
    roll = dice_msg.dice.value
    
    await asyncio.sleep(3)
    
    coins = p["coins"] - bet
    multipliers = {1: 6.0, 2: 3.0, 3: 2.0, 4: 1.5, 5: 1.2}
    
    if roll in chosen:
        win = int(bet * multipliers[len(chosen)])
        coins += win
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
        await message.answer(f"🎲 Выпало **{roll}**! Победа! Вы выиграли `+{win - bet}` монет! 💰 (Баланс: `{coins}`)", parse_mode=ParseMode.MARKDOWN)
    else:
        await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
        await message.answer(f"🎲 Выпало **{roll}**. Проигрыш `{bet}` монет. 💸 (Баланс: `{coins}`)", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("slots"))
async def cmd_slots(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: `/slots <ставка>`", parse_mode=ParseMode.MARKDOWN)
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
    is_jackpot = val in [1, 22, 43, 64]
    is_win = val in [16, 23, 34, 41, 52, 59] or is_jackpot
    
    if is_jackpot:
        win = bet * 5
        coins += win
        res_text = f"🎉 ДЖЕКПОТ (x5)! Вы выиграли `+{win}` монет!"
    elif is_win:
        win = int(bet * 2)
        coins += win
        res_text = f"✨ Удача (x2)! Вы выиграли `+{win}` монет!"
    else:
        res_text = f"❌ Проигрыш `{bet}` монет."
        
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": coins}).eq("user_id", p["user_id"]).execute())
    await message.answer(f"{res_text}\n💰 Баланс: `{coins}`", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("ball"))
async def cmd_ball(message: types.Message):
    answers = ["Да", "Нет", "Скорее всего да", "Точно нет", "Спроси позже", "Определенно да"]
    await message.answer(f"🎱 Шар говорит: *{random.choice(answers)}*", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("duel"))
async def cmd_duel(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение противника командой `/duel`", parse_mode=ParseMode.MARKDOWN)
        return
    winner = random.choice([message.from_user, message.reply_to_message.from_user])
    await message.answer(f"⚔️ Победитель дуэли: **{winner.first_name}**!", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("kiss"))
async def cmd_kiss(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение пользователя командой `/kiss`", parse_mode=ParseMode.MARKDOWN)
        return
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id: return
    await message.answer(f"💋 **{message.from_user.first_name}** целует **{target.first_name}**! 💕", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("marry"))
async def cmd_marry(message: types.Message):
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
async def callback_marry(callback: types.CallbackQuery):
    try:
        data_parts = callback.data.split("_")
        action, proposer_id = data_parts[1], int(data_parts[2])
        accepter = callback.from_user
        if accepter.id == proposer_id:
            await callback.answer("Нельзя ответить на свое предложение!", show_alert=True)
            return
        proposer_res = supabase.table("users").select("*").eq("user_id", str(proposer_id)).execute()
        if not proposer_res.data:
            await callback.message.edit_text("💔 Инициатор не найден.")
            return
        proposer_data = proposer_res.data[0]
        accepter_data = await get_profile(accepter)

        if action == "reject":
            await callback.message.edit_text(f"💔 **{accepter.first_name}** отклонил(а) предложение.")
            return

        await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": str(accepter.id), "partner_name": accepter.first_name}).eq("user_id", str(proposer_id)).execute())
        await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": str(proposer_id), "partner_name": proposer_data["username"]}).eq("user_id", str(accepter.id)).execute())
        await callback.message.edit_text(f"🎉 Горько! **{proposer_data['username']}** и **{accepter.first_name}** поженились! 💍❤️ Теперь вам доступно меню семьи в профиле отношений.")
    except Exception as e:
        logging.error(f"Error in marry callback: {e}")
        await callback.answer("❌ Ошибка при заключении брака!", show_alert=True)

@dp.message(Command("partner"))
async def cmd_partner(message: types.Message):
    p = await get_profile(message.from_user)
    pid, pname = p.get("partner_id"), p.get("partner_name")
    if not pid or str(pid) == "0" or not pname or pname == "EMPTY":
        await message.answer("💍 У вас нет партнера.", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer(f"💍 Вторая половинка: **{pname}** ❤️", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message):
    p = await get_profile(message.from_user)
    pid = p.get("partner_id")
    if not pid or str(pid) == "0":
        await message.answer("💔 Вы не в браке.", parse_mode=ParseMode.MARKDOWN)
        return
    await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY"}).eq("user_id", str(pid)).execute())
    await asyncio.to_thread(lambda: supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY"}).eq("user_id", p["user_id"]).execute())
    await message.answer("💔 Развод оформлен.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("sex"))
async def cmd_sex(message: types.Message):
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    pid, pname = p.get("partner_id"), p.get("partner_name")
    if not pid or str(pid) == "0" or not pname or pname == "EMPTY":
        await message.answer("🛏️ Доступно только в браке!", parse_mode=ParseMode.MARKDOWN)
        return
    now = time.time()
    if now - INTIMATE_COOLDOWNS.get(uid, 0) < 600:
        rem = int(600 - (now - INTIMATE_COOLDOWNS.get(uid, 0)))
        await message.answer(f"⏳ Отдохните еще `{rem // 60} мин.`", parse_mode=ParseMode.MARKDOWN)
        return
    INTIMATE_COOLDOWNS[uid] = now
    coins, xp = random.randint(50, 150), 25
    new_coins, new_xp = p.get("coins", 0) + coins, p.get("xp", 0) + xp
    new_level = p.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]: new_level = lvl
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": new_coins, "xp": new_xp, "level": new_level}).eq("user_id", uid).execute())
    
    announcement = (
        f"🔥 **ВНИМАНИЕ ВСЕМ!** 🔥\n"
        f"В этом чате только что произошел страстный половой акт между **{message.from_user.first_name}** и **{pname}**! 🛏️💦\n"
        f"🪙 Оба участника получили порцию страсти (+{coins} монет, +{xp} XP)!"
    )
    await message.answer(announcement, parse_mode=ParseMode.MARKDOWN)

# --- АДМИНСКИЕ КОМАНДЫ ---
async def verify_admin(message: types.Message) -> bool:
    if not is_admin(message.from_user):
        await message.answer("❌ Нет прав.")
        return False
    if not message.reply_to_message:
        await message.answer("⚠️ Сделайте реплай на сообщение игрока!")
        return False
    return True

@dp.message(Command("add_coins"))
async def admin_add_coins(message: types.Message):
    if not await verify_admin(message): return
    amount = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": target["coins"] + amount}).eq("user_id", target["user_id"]).execute())
    await message.answer(f"🛡 Добавлено `{amount}` монет.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("set_coins"))
async def admin_set_coins(message: types.Message):
    if not await verify_admin(message): return
    amount = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    await asyncio.to_thread(lambda: supabase.table("users").update({"coins": amount}).eq("user_id", target["user_id"]).execute())
    await message.answer(f"🛡 Баланс установлен на `{amount}`.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("add_xp"))
async def admin_add_xp(message: types.Message):
    if not await verify_admin(message): return
    amount = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    new_xp = target.get("xp", 0) + amount
    new_lvl = target.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]: new_lvl = lvl
    await asyncio.to_thread(lambda: supabase.table("users").update({"xp": new_xp, "level": new_lvl}).eq("user_id", target["user_id"]).execute())
    await message.answer(f"🛡 Добавлено `+{amount} XP`.", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("set_level"))
async def admin_set_level(message: types.Message):
    if not await verify_admin(message): return
    lvl = int(message.text.split()[1])
    target = await get_profile(message.reply_to_message.from_user)
    req_xp = LEVELS[lvl]["xp"]
    await asyncio.to_thread(lambda: supabase.table("users").update({"level": lvl, "xp": req_xp}).eq("user_id", target["user_id"]).execute())
    await message.answer(f"🛡 Уровень изменен на `{lvl}`.", parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text)
async def process_message_xp(message: types.Message):
    if message.text.startswith("/"): return
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    new_xp = p.get("xp", 0) + 5
    new_level = p.get("level", 1)
    for lvl, data in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= data["xp"]: new_level = lvl
    if new_level > p.get("level", 1):
        await message.answer(f"🎉 Уровень **{message.from_user.first_name}** повышен до `{new_level}`!", parse_mode=ParseMode.MARKDOWN)
    await asyncio.to_thread(lambda: supabase.table("users").update({"xp": new_xp, "level": new_level}).eq("user_id", uid).execute())

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
