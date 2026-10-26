import asyncio
import logging
import os
import random
import time
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand, BotCommandScopeDefault
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from supabase import create_client, Client

# --- НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ) ---
BOT_TOKEN = "8844907899:AAHMzg4WwV6hbu9D3yFgRWipr0iKm75kYyw"
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
    waiting_for_withdraw_amount = State()

class ProfileState(StatesGroup):
    waiting_for_music = State()

class SupportState(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()

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

BUSINESSES_CAT = {
    "lemonade": {
        "name": "🍋 Лимонадный киоск",
        "price": 50000,
        "base_profit": 1500,
        "raw_cost_per_unit": 20,
        "up1": {"name": "🧊 Промышленный льдогенератор", "price": 20000, "profit_add": 300, "raw_add": 2},
        "up2": {"name": "🥤 Автомат по разливу", "price": 45000, "profit_add": 700, "raw_add": 4},
        "up3": {"name": "🌟 Брендовая неоновая вывеска", "price": 90000, "profit_add": 1500, "raw_add": 7}
    },
    "cafe": {
        "name": "☕ Уютная кофейня",
        "price": 200000,
        "base_profit": 5500,
        "raw_cost_per_unit": 60,
        "up1": {"name": "🫘 Итальянская кофемашина", "price": 80000, "profit_add": 1200, "raw_add": 3},
        "up2": {"name": "🥐 Витрина со свежей выпечкой", "price": 160000, "profit_add": 2500, "raw_add": 6},
        "up3": {"name": "🛋 Зона отдыха для гостей", "price": 320000, "profit_add": 5200, "raw_add": 10}
    },
    "farm": {
        "name": "🌾 Агроферма",
        "price": 400000,
        "base_profit": 11000,
        "raw_cost_per_unit": 100,
        "up1": {"name": "💧 Система капельного полива", "price": 150000, "profit_add": 2400, "raw_add": 4},
        "up2": {"name": "🚜 Новый трактор МТЗ", "price": 300000, "profit_add": 5000, "raw_add": 8},
        "up3": {"name": "🧪 Удобрения нового поколения", "price": 600000, "profit_add": 10500, "raw_add": 14}
    },
    "shop": {
        "name": "🏪 Супермаркет",
        "price": 800000,
        "base_profit": 22000,
        "raw_cost_per_unit": 200,
        "up1": {"name": "❄️ Морозильные камеры", "price": 300000, "profit_add": 5000, "raw_add": 5},
        "up2": {"name": "💳 Кассы самообслуживания", "price": 600000, "profit_add": 11000, "raw_add": 10},
        "up3": {"name": "🕒 Круглосуточный режим 24/7", "price": 1200000, "profit_add": 23000, "raw_add": 18}
    },
    "plant": {
        "name": "🏭 Завод",
        "price": 1500000,
        "base_profit": 42000,
        "raw_cost_per_unit": 350,
        "up1": {"name": "🛠 Новый ЧПУ станок", "price": 500000, "profit_add": 9000, "raw_add": 6},
        "up2": {"name": "⚡ Автоматическая линия сборки", "price": 1100000, "profit_add": 20000, "raw_add": 12},
        "up3": {"name": "🤖 Роботизированный цех", "price": 2400000, "profit_add": 43000, "raw_add": 20}
    },
    "oil": {
        "name": "🛢 Нефтяная вышка",
        "price": 3500000,
        "base_profit": 95000,
        "raw_cost_per_unit": 700,
        "up1": {"name": "⚙️ Буровой бур нового поколения", "price": 1200000, "profit_add": 21000, "raw_add": 8},
        "up2": {"name": "🛞 Насосы высокого давления", "price": 2500000, "profit_add": 45000, "raw_add": 16},
        "up3": {"name": "🧪 Система очистки сырой нефти", "price": 5000000, "profit_add": 95000, "raw_add": 25}
    },
    "it": {
        "name": "💻 IT-компания",
        "price": 6000000,
        "base_profit": 170000,
        "raw_cost_per_unit": 1200,
        "up1": {"name": "🖥 Серверная стойка с RTX", "price": 2000000, "profit_add": 38000, "raw_add": 10},
        "up2": {"name": "🛡 Система кибербезопасности", "price": 4500000, "profit_add": 82000, "raw_add": 20},
        "up3": {"name": "🌐 Квантовый дата-центр", "price": 9000000, "profit_add": 175000, "raw_add": 30}
    },
    "space": {
        "name": "🚀 Космодром",
        "price": 15000000,
        "base_profit": 400000,
        "raw_cost_per_unit": 2500,
        "up1": {"name": "🛰 Стартовый комплекс", "price": 5000000, "profit_add": 90000, "raw_add": 15},
        "up2": {"name": "📡 РЛС дальнего действия", "price": 11000000, "profit_add": 200000, "raw_add": 30},
        "up3": {"name": "🌌 Межпланетный ангар", "price": 22000000, "profit_add": 420000, "raw_add": 45}
    }
}

CARS_CAT = {
    "granta": {"name": "🚗 Lada Granta", "price": 50000, "base_speed": 172, "accel": 11.8, "fuel_cons": 6.8, "tank": 50},
    "vesta": {"name": "🚗 Lada Vesta", "price": 120000, "base_speed": 188, "accel": 10.2, "fuel_cons": 7.3, "tank": 55},
    "rio": {"name": "🚗 Kia Rio", "price": 160000, "base_speed": 190, "accel": 10.3, "fuel_cons": 6.6, "tank": 50},
    "solaris": {"name": "🚗 Hyundai Solaris", "price": 170000, "base_speed": 192, "accel": 10.7, "fuel_cons": 6.5, "tank": 50},
    "octavia": {"name": "🚗 Skoda Octavia", "price": 250000, "base_speed": 219, "accel": 8.1, "fuel_cons": 6.5, "tank": 50},
    "camry": {"name": "🚗 Toyota Camry", "price": 380000, "base_speed": 210, "accel": 8.3, "fuel_cons": 7.8, "tank": 60},
    "m3": {"name": "🏎 BMW M3 E46", "price": 550000, "base_speed": 250, "accel": 5.2, "fuel_cons": 11.9, "tank": 63},
    "w222": {"name": "🚘 Mercedes-Benz S-Class", "price": 900000, "base_speed": 250, "accel": 4.6, "fuel_cons": 8.5, "tank": 80},
    "rs6": {"name": "🏎 Audi RS6 Avant", "price": 1250000, "base_speed": 305, "accel": 3.6, "fuel_cons": 11.5, "tank": 73},
    "gtr": {"name": "🏎 Nissan GT-R R35", "price": 1600000, "base_speed": 315, "accel": 2.7, "fuel_cons": 12.0, "tank": 74},
    "911": {"name": "🏎 Porsche 911 Turbo S", "price": 2200000, "base_speed": 330, "accel": 2.6, "fuel_cons": 11.1, "tank": 67},
    "huracan": {"name": "🏎 Lamborghini Huracan", "price": 3000000, "base_speed": 325, "accel": 2.9, "fuel_cons": 14.2, "tank": 83},
    "488": {"name": "🏎 Ferrari 488 Spider", "price": 3800000, "base_speed": 325, "accel": 3.0, "fuel_cons": 11.4, "tank": 78},
    "db11": {"name": "🏎 Aston Martin DB11", "price": 4600000, "base_speed": 322, "accel": 3.9, "fuel_cons": 11.3, "tank": 78},
    "chiron": {"name": "🏎 Bugatti Chiron", "price": 6000000, "base_speed": 420, "accel": 2.4, "fuel_cons": 22.5, "tank": 100},
    "phantom": {"name": "👑 Rolls-Royce Phantom", "price": 8000000, "base_speed": 250, "accel": 5.3, "fuel_cons": 13.9, "tank": 100},
    "koenigsegg": {"name": "🏎 Koenigsegg Jesko", "price": 14000000, "base_speed": 480, "accel": 2.5, "fuel_cons": 18.0, "tank": 72},
    "m5f90": {"name": "🏎 BMW M5 F90", "price": 0, "base_speed": 305, "accel": 3.3, "fuel_cons": 10.5, "tank": 68, "admin_only": True},
}

FUEL_TYPES = {
    92: {"name": "АИ-92", "price_per_liter": 50, "bonus": 0.0},
    95: {"name": "АИ-95", "price_per_liter": 58, "bonus": 0.05},
    100: {"name": "АИ-100", "price_per_liter": 70, "bonus": 0.12}
}

CAR_COLORS = [
    "🖤 Черный", "🤍 Белый", "🥈 Серебристый", "❤️ Красный", 
    "💙 Синий", "💛 Желтый", "💚 Зеленый", "💜 Фиолетовый"
]

APARTMENTS_CAT = {
    "room": {"name": "🏢 Комната в общежитии", "price": 20000},
    "studio": {"name": "🏢 Студия на окраине", "price": 50000},
    "1k": {"name": "🏢 1-комнатная квартира", "price": 120000},
    "2k": {"name": "🏢 2-комнатная квартира", "price": 220000},
    "3k": {"name": "🏢 3-комнатная в центре", "price": 350000},
    "loft": {"name": "🏢 Лофт в арт-квартале", "price": 700000},
    "penthouse": {"name": "🏢 Элитный пентхаус", "price": 1200000},
    "duplex": {"name": "🏢 Двухуровневые апартаменты", "price": 2500000},
    "skyscraper": {"name": "🏢 Небоскреб целиком", "price": 7000000},
}

HOUSES_CAT = {
    "dacha": {"name": "🏡 Дачный домик", "price": 200000},
    "townhouse": {"name": "🏡 Таунхаус за городом", "price": 450000},
    "cottage": {"name": "🏡 Загородный коттедж", "price": 800000},
    "modern": {"name": "🏡 Дом в стиле Хай-тек", "price": 1400000},
    "villa": {"name": "🏡 Элитная вилла с бассейном", "price": 2000000},
    "estate": {"name": "🏰 Поместье с парком", "price": 5000000},
    "castle": {"name": "🏰 Средневековый замок", "price": 7500000},
    "palace": {"name": "👑 Королевский особняк", "price": 10000000},
    "island": {"name": "🏝 Частный тропический остров", "price": 25000000},
}

FAMILY_HOUSES = {
    "cottage": {"name": "🏡 Загородный коттедж", "price": 800000},
    "modern": {"name": "🏡 Дом в стиле Хай-тек", "price": 1400000},
    "villa": {"name": "🏡 Элитная вилла с бассейном", "price": 2000000},
    "estate": {"name": "🏰 Поместье с парком", "price": 5000000},
    "castle": {"name": "🏰 Средневековый замок", "price": 7500000},
    "palace": {"name": "👑 Королевский особняк", "price": 10000000},
}

FAMILY_APTS = {
    "1k": {"name": "🏢 1-комнатная квартира", "price": 120000},
    "3k": {"name": "🏢 3-комнатная в центре", "price": 350000},
    "penthouse": {"name": "🏢 Элитный пентхаус", "price": 1200000},
    "duplex": {"name": "🏢 Двухуровневые апартаменты", "price": 2500000},
    "skyscraper": {"name": "🏢 Небоскреб целиком", "price": 7000000},
}

FAMILY_CARS = {
    "camry": {"name": "🚗 Toyota Camry", "price": 380000},
    "rs6": {"name": "🏎 Audi RS6 Avant", "price": 1250000},
    "db11": {"name": "🏎 Aston Martin DB11", "price": 4600000},
    "chiron": {"name": "🏎 Bugatti Chiron", "price": 6000000},
    "koenigsegg": {"name": "🏎 Koenigsegg Jesko", "price": 14000000},
}

WORK_COOLDOWNS = {}
INTIMATE_COOLDOWNS = {}
PENDING_MARRIAGES = {}
PENDING_RACES = {}

JOBS = {
    "1": {"name": "⛏ Шахтёр", "min_coins": 40, "max_coins": 90, "xp": 10},
    "2": {"name": "🛡 Стражник", "min_coins": 60, "max_coins": 130, "xp": 15},
    "3": {"name": "🧪 Алхимик", "min_coins": 90, "max_coins": 180, "xp": 22},
    "4": {"name": "🐉 Охотник на чудовищ", "min_coins": 130, "max_coins": 260, "xp": 30},
}

SHOP_EQUIPMENT = {
    "eq_1": {"name": "🪵 Деревянный меч", "price": 150, "duel_buff": 5, "desc": "Самодельное оружие. Дает +5% к победе в дуэли."},
    "eq_3": {"name": "🛡 Кожаная броня", "price": 250, "duel_buff": 10, "desc": "Защита торса. Дает +10% к победе в дуэли."},
    "eq_2": {"name": "⚔️ Железный меч", "price": 350, "duel_buff": 12, "desc": "Надежный клинок. Дает +12% к победе в дуэли."},
    "eq_5": {"name": "💍 Руническое кольцо", "price": 600, "duel_buff": 8, "desc": "Артефакт магов. Дает +8% к победе в дуэли."},
    "eq_6": {"name": "🔥 Пламенный клинок", "price": 1400, "duel_buff": 30, "desc": "Оружие дракоборцев. Дает +30% к победе в дуэли."},
    "eq_4": {"name": "🛡 Мифриловый щит", "price": 1800, "duel_buff": 25, "desc": "Несокрушимая защита. Дает +25% к победе в дуэли."},
    "eq_8": {"name": "⚡ Электрический посох", "price": 3200, "duel_buff": 40, "desc": "Бьет током врагов. Дает +40% к победе."},
    "eq_7": {"name": "👑 Корона победителя", "price": 5000, "duel_buff": 50, "desc": "Знак истинной власти. Дает +50% к победе в дуэли."},
    "eq_9": {"name": "💎 Клинки вечности", "price": 9500, "duel_buff": 70, "desc": "Оружие богов арены. Дает +70% к победе."},
}

SHOP_CONSUMABLES = {
    "chips": {"name": "🍟 Чипсы с сыром", "price": 50, "desc": "Вкусный снек. Дает +15 XP."},
    "pizza": {"name": "🍔 Пицца", "price": 80, "desc": "Горячая сытная еда. Дает +30 XP и +20 монет."},
    "energy": {"name": "⚡ Энергетик", "price": 90, "desc": "Бодрящий напиток. Дает +50 XP."},
    "cigars": {"name": "🚬 Сигареты", "price": 100, "desc": "Добавляет авторитета (+5 респекта) и никотиновую зависимость."},
    "beer_okhota": {"name": "🍺 Охота Крепкое", "price": 120, "desc": "Легендарное пиво. Мут на 2 мин + рандом монет."},
    "vodka": {"name": "🥃 Паленая водка", "price": 200, "desc": "Жесткий напиток. Мут на 5 мин и риск потерять/удвоить монеты."},
    "hookah": {"name": "💨 Кальян", "price": 450, "desc": "Ароматный дым. Дает +80 XP."},
    "whiskey": {"name": "🥃 Элитный Виски", "price": 900, "desc": "Дорогой алкоголь. Дает +40 респекта."},
    "chair": {"name": "💺 Геймерское кресло", "price": 2200, "desc": "Эргономика. Дает +100 респекта."},
    "pc": {"name": "💻 Игровой ПК", "price": 3500, "desc": "Топовая сборка с RTX. Дает +150 респекта."},
    "vr": {"name": "🥽 VR-шлем топовый", "price": 6000, "desc": "Погружение в виртуальную реальность (+220 респекта)."},
    "server": {"name": "🖥 Домашний сервер", "price": 12000, "desc": "Майнинг крипты и хостинг (+400 респекта)."},
}

SEX_SHOP = {
    "sex_oil": {"name": "🧴 Массажное масло", "price": 400, "desc": "Для безумно нежных касаний."},
    "sex_gag": {"name": "🔴 Кожаный кляп", "price": 500, "desc": "Чтобы стоны не мешали соседям."},
    "sex_mask": {"name": "🎭 Кружевная маска", "price": 600, "desc": "Атмосфера тайного греха."},
    "sex_cuff": {"name": "⛓️ Кожаные наручники", "price": 700, "desc": "Полный контроль над партнером."},
    "sex_vibe": {"name": "🟣 Вибратор", "price": 800, "desc": "Мощная игрушка для ярких эмоций."},
    "sex_maid": {"name": "👗 Костюм горничной", "price": 1000, "desc": "Соблазнительный наряд."},
    "sex_whip": {"name": "🖤 Кожаный хлыст", "price": 1200, "desc": "Добавляет перчинку в отношения."},
    "sex_dildo": {"name": "🍆 Неоновый фаллоимитатор", "price": 1900, "desc": "Светящийся монстр для страстных ночей."},
    "sex_chains": {"name": "🔗 Стальные цепи БДСМ", "price": 3400, "desc": "Максимальная фиксация и жесткость."},
}

SEX_DESCRIPTIONS = {
    "sex_vibe": "🟣 Вы включаете мощный вибратор на максимум, прижимая его к чувствительным точкам партнера. Комната наполняется громкими, сочными стонами, а тело партнера бьется в экстазе от непрерывных мощных вибраций.",
    "sex_gag": "🔴 Туго затянув кожаный кляп в рту партнера, вы лишаете его возможности кричать, оставляя лишь зычные всхлипы и сдавленные стоны, пока вы жестко и страстно берете его.",
    "sex_cuff": "⛓️ Намертво приковав руки партнера металлическими наручниками к спинке кровати, вы полностью подчиняете себе, оставляя беззащитным перед вашими дикими ласками и шлепками.",
    "sex_maid": "👗 Облачив партнера в соблазнительный костюм горничной с кружевами, вы срываете наряд в первые же секунды, погружаясь в неистовую, развратную плотскую утеху.",
    "sex_whip": "🖤 Резкие и хлесткие удары кожаным хлыстом оставляют алые следы на разгоряченной коже, доводя уровень адреналина и животной страсти до абсолютного пика.",
    "sex_oil": "🧴 Щупая и втирая теплое массажное масло в каждый сантиметр обнаженных тел, вы делаете движения максимально плавными, скользкими и безумно возбуждающими.",
    "sex_mask": "🎭 Надев на лицо кружевную маску, партнер отключает все мысли и полностью отдается вашей власти, принимая самые смелые и грязные фантазии в полумраке.",
    "sex_dildo": "🍆 Неоновый фаллоимитатор ярко пульсирует в темноте, задавая бешеный ритм глубоким проникновениям под дикие крики восторга.",
    "sex_chains": "🔗 Тяжелые стальные цепи надежно удерживают партнера намертво, превращая ночь в бескомпромиссное БДСМ-шоу."
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

async def get_menu_header(user: types.User, p: dict = None) -> str:
    if not p:
        p = await get_profile(user)
    uname = p.get('username') or user.first_name
    admin_tag = " 🟢 **(админ)**" if is_admin(user) else ""
    partner_tag = " ⭐️ **(партнер)**" if p.get("is_partner") else ""
    return f"👤 **Меню игрока: {uname}**{admin_tag}{partner_tag}\n"

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
            if user.username and user_data.get("username") != user.username:
                updates["username"] = user.username
                user_data["username"] = user.username
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
        "profile_music": "",
        "started_in_pm": False,
        "is_partner": False,
        "partner_given_today": 0,
        "partner_last_date": ""
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

async def get_family(uid: str):
    def _fetch():
        r1 = supabase.table("families").select("*").eq("partner1_id", uid).execute()
        if r1.data: return r1.data[0]
        r2 = supabase.table("families").select("*").eq("partner2_id", uid).execute()
        if r2.data: return r2.data[0]
        return None
    try:
        return await asyncio.to_thread(_fetch)
    except Exception as e:
        logging.error(f"Error fetching family: {e}")
    return None

async def update_businesses_for_user(uid: str):
    now = int(time.time())
    def _get_b():
        return supabase.table("user_businesses").select("*").eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_b)
    if not res.data:
        return

    for biz in res.data:
        last_time = int(biz.get("last_update_time") or now)
        if last_time == 0:
            last_time = now
            supabase.table("user_businesses").update({"last_update_time": now}).eq("id", biz["id"]).execute()
            continue

        hours_passed = (now - last_time) / 3600.0
        if hours_passed < 1.0:
            continue

        full_hours = int(hours_passed)
        b_cat = BUSINESSES_CAT.get(biz["business_type"], {})
        
        workers = biz.get("workers", 0)
        max_workers = biz.get("max_workers", 20)
        raw = biz.get("raw_material", 0)
        max_raw = biz.get("max_raw_material", 100)
        
        up1 = biz.get("up1_lvl", 0)
        up2 = biz.get("up2_lvl", 0)
        up3 = biz.get("up3_lvl", 0)

        base_raw_per_hour = int(max_raw * 0.1)
        raw_add_from_ups = (up1 * b_cat.get("up1", {}).get("raw_add", 0)) + \
                           (up2 * b_cat.get("up2", {}).get("raw_add", 0)) + \
                           (up3 * b_cat.get("up3", {}).get("raw_add", 0))
        total_raw_consumption = (base_raw_per_hour + raw_add_from_ups) * full_hours

        if raw <= 0:
            supabase.table("user_businesses").update({"last_update_time": now}).eq("id", biz["id"]).execute()
            continue

        worker_ratio = workers / max_workers if max_workers > 0 else 0
        if worker_ratio < 0.5:
            supabase.table("user_businesses").update({"last_update_time": now}).eq("id", biz["id"]).execute()
            continue

        profit_multiplier = worker_ratio
        earned = int(biz["profit_per_hour"] * full_hours * profit_multiplier)
        new_raw = max(0, raw - total_raw_consumption)
        new_balance = biz["balance_profit"] + earned
        new_last_time = last_time + (full_hours * 3600)

        def _upd_biz():
            supabase.table("user_businesses").update({
                "balance_profit": new_balance,
                "raw_material": new_raw,
                "last_update_time": new_last_time
            }).eq("id", biz["id"]).execute()
        await asyncio.to_thread(_upd_biz)

def get_main_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data=f"menu_profile_{user_id}"),
         InlineKeyboardButton(text="🎒 Инвентарь", callback_data=f"menu_inv_{user_id}")],
        [InlineKeyboardButton(text="⚔️ Оружейная", callback_data=f"menu_armory_{user_id}"),
         InlineKeyboardButton(text="🏎 Гараж и Авто", callback_data=f"menu_garage_{user_id}")],
        [InlineKeyboardButton(text="🛒 Магазины", callback_data=f"menu_shops_{user_id}")],
        [InlineKeyboardButton(text="🏢 Бизнесы", callback_data=f"menu_biz_{user_id}"),
         InlineKeyboardButton(text="🏠 Имущество", callback_data=f"menu_personal_{user_id}")],
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data=f"menu_top_{user_id}"),
         InlineKeyboardButton(text="💼 Биржа труда", callback_data=f"menu_work_{user_id}")],
        [InlineKeyboardButton(text="🏁 Уличные гонки", callback_data=f"menu_race_{user_id}"),
         InlineKeyboardButton(text="🎰 Казино и игры", callback_data=f"menu_casino_{user_id}")],
        [InlineKeyboardButton(text="💍 Отношения и Семья", callback_data=f"menu_marry_{user_id}"),
         InlineKeyboardButton(text="🆘 Техподдержка", callback_data=f"menu_support_{user_id}")]
    ])

@dp.message(Command(commands=["start", "help", "menu"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    
    if message.chat.type == "private" and not p.get("started_in_pm", False):
        def _upd_pm():
            supabase.table("users").update({"started_in_pm": True}).eq("user_id", uid).execute()
        await asyncio.to_thread(_upd_pm)
        p["started_in_pm"] = True

    header = await get_menu_header(message.from_user, p)
    text = (
        f"{header}\n"
        "🎮 Добро пожаловать в RPG бот!\n"
        "Используйте кнопки ниже для управления персонажем, бизнесами, оружейной, казино и гонками."
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
        p = await get_profile(callback.from_user)
        header = await get_menu_header(callback.from_user, p)
        text = f"{header}\n🎮 **ГЛАВНОЕ МЕНЮ:**"
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
        uid = str(callback.from_user.id)
        header = await get_menu_header(callback.from_user, p)
        
        if action == "biz":
            await update_businesses_for_user(uid)
            def _get_biz():
                return supabase.table("user_businesses").select("*").eq("user_id", uid).execute()
            res = await asyncio.to_thread(_get_biz)
            user_businesses = res.data if res.data else []

            text = f"{header}\n🏢 **ВАШИ БИЗНЕСЫ** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\n"
            buttons = []

            if not user_businesses:
                text += "У вас пока нет ни одного бизнеса. Приобретите их на бирже предприятий ниже!"
            else:
                for b in user_businesses:
                    workers = b["workers"]
                    max_w = b["max_workers"]
                    raw = b["raw_material"]
                    max_r = b["max_raw_material"]
                    profit_h = b["profit_per_hour"]
                    accumulated = b["balance_profit"]
                    
                    w_status = f"{workers}/{max_w}"
                    if workers < (max_w * 0.5):
                        w_status += " ⚠️ (Мало работников, простой!)"
                    
                    r_status = f"{raw}/{max_r}"
                    if raw <= 0:
                        r_status += " ❌ (Нет сырья!)"

                    text += f"🔹 **{b['business_name']}** (Ур. {b['level']})\n"
                    text += f"   💰 Прибыль: `{profit_h:,}` 🪙/час | Накоплено: `+{accumulated:,}` 🪙\n"
                    text += f"   👷 Работники: {w_status} | 📦 Сырье: {r_status}\n\n"
                    
                    buttons.append([InlineKeyboardButton(text=f"⚙️ Управление: {b['business_name']}", callback_data=f"biz_manage_{b['id']}_{uid}")])

            buttons.append([InlineKeyboardButton(text="📈 Биржа предприятий (Купить бизнес)", callback_data=f"biz_shop_list_{uid}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            return

        elif action == "profile":
            lvl = p.get('level', 1)
            title = LEVELS.get(lvl, {}).get("title", "Воин")
            pid, pname = p.get("partner_id"), p.get("partner_name")
            
            created_at = int(p.get("created_at") or time.time())
            bot_age = format_age(int(time.time()) - created_at)
            
            if pid and str(pid) != "0" and pname and str(pname).upper() != "EMPTY":
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
                car_res = supabase.table("user_cars").select("*").eq("user_id", uid).eq("is_active", True).execute()
                active_car = car_res.data[0] if car_res.data else None
                return active_car
            active_car = await asyncio.to_thread(_get_car_and_prop)
            car_info = f"🚗 Машина: **{active_car['car_name']}** ({active_car['color']})" if active_car else "🚗 Машина: ❌ Нет"
            apt_info = f"🏢 Квартира: `{p.get('personal_apartment', '❌ Нет')}`"
            house_info = f"🏡 Дом: `{p.get('personal_house', '❌ Нет')}`"
            
            text = (
                f"{header}\n"
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
            
            text = f"{header}\n⚔️ **ОРУЖЕЙНАЯ ИГРОКА** (Баланс: `{p.get('coins', 0):,}` 🪙)\n\n"
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
                    buttons.append([InlineKeyboardButton(text=f"⚔️ Надеть: {eq_data['name']}{is_eq}", callback_data=f"equip_item_{idx}_{eq_key}_{uid}")])
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
                text = f"{header}\n🎒 **Инвентарь игрока** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\nВаш инвентарь пуст."
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]])
            else:
                text = f"{header}\n🎒 **Инвентарь игрока** (Баланс: `{p.get('coins', 0):,}` 🪙):\nНажмите на предмет, чтобы использовать его:\n\n"
                buttons = []
                for idx, item_key in enumerate(items):
                    item_info = SHOP_CONSUMABLES.get(item_key) or SEX_SHOP.get(item_key) or {"name": item_key}
                    buttons.append([InlineKeyboardButton(text=f"🎁 Использовать: {item_info['name']}", callback_data=f"use_item_{idx}_{item_key}_{uid}")])
                buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
                kb = InlineKeyboardMarkup(inline_keyboard=buttons)
                
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "garage":
            def _get_cars():
                return supabase.table("user_cars").select("*").eq("user_id", uid).execute()
            cars_res = await asyncio.to_thread(_get_cars)
            user_cars = cars_res.data if cars_res and cars_res.data else []

            text = f"{header}\n🏎 **ВАШ ГАРАЖ И АВТОМОБИЛИ** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\n"
            buttons = []

            if not user_cars:
                text += "У вас пока нет машин. Купите их в автосалоне!"
            else:
                for car in user_cars:
                    active_mark = "🟢 [АКТИВНА]" if car['is_active'] else ""
                    car_base = CARS_CAT.get(car['car_key'], {"price": 100000, "base_speed": 200, "accel": 10.0, "fuel_cons": 8.0})
                    sell_price = int(car_base['price'] * 0.5)
                    
                    ftype = car.get('fuel_type', 92)
                    fliters = car.get('fuel_liters', 50.0)
                    m_tank = car.get('max_fuel_liters', 50)

                    text += f"🚗 **{car['car_name']}** | {car['color']} {active_mark}\n"
                    text += f"   🚀 Макс. скорость: `{car_base['base_speed']} км/ч` | Разгон 0-100: `{car_base['accel']}с`\n"
                    text += f"   ⛽ Расход: `{car_base['fuel_cons']} л/100км` | Топливо: `{fliters:.1f}/{m_tank} л` (`{ftype}`)\n"
                    text += f"   └ Двиг: Ур.{car['engine_lvl']} | Турбо: Ур.{car['turbo_lvl']} | Управл: Ур.{car['handling_lvl']}\n\n"
                    
                    if not car['is_active']:
                        buttons.append([InlineKeyboardButton(text=f"🔑 Сесть за руль: {car['car_name']}", callback_data=f"car_activate_{car['id']}_{uid}")])
                    buttons.append([InlineKeyboardButton(text=f"⛽ Заправить: {car['car_name']}", callback_data=f"car_refuel_menu_{car['id']}_{uid}")])
                    buttons.append([InlineKeyboardButton(text=f"⚙️ Тюнинг: {car['car_name']}", callback_data=f"car_tune_{car['id']}_{uid}")])
                    buttons.append([InlineKeyboardButton(text=f"🗑 Продать за {sell_price:,} 🪙", callback_data=f"car_sell_{car['id']}_{uid}")])

            buttons.append([InlineKeyboardButton(text="🛍 Автосалон (Купить авто)", callback_data=f"shop_cars_list_{uid}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "race":
            text = (
                f"{header}\n"
                "🏁 **УЛИЧНЫЕ ГОНКИ (PvP по согласию)**\n\n"
                "🏆 Чтобы бросить вызов сопернику, ответьте на его сообщение командой: `/race <ставка>` (например, `/race 5000`). Сопернику придет кнопка подтверждения."
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "shops":
            text = f"{header}\n🛒 **ВЫБЕРИТЕ МАГАЗИН** (Баланс: `{p.get('coins', 0):,}` 🪙):"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏎 Автосалон (Все модели)", callback_data=f"shop_cars_list_{uid}")],
                [InlineKeyboardButton(text="⚔️ Снаряжение", callback_data=f"shop_eq_list_{uid}")],
                [InlineKeyboardButton(text="🍺 Продукты и техника", callback_data=f"shop_cons_list_{uid}")],
                [InlineKeyboardButton(text="🍑 Секс-шоп (Игрушки)", callback_data=f"menu_sexshop_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "sexshop":
            text = f"{header}\n🍑 **СЕКС-ШОП** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\nПриобретайте игрушки (от дешевых к дорогим), они попадают в инвентарь:"
            buttons = []
            for item_id, data in SEX_SHOP.items():
                buttons.append([InlineKeyboardButton(text=f"{data['name']} — {data['price']:,} 🪙", callback_data=f"buy_sex_{item_id}_{uid}")])
            buttons.append([InlineKeyboardButton(text="🔙 В меню магазинов", callback_data=f"menu_shops_{uid}")])
            try:
                await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "personal":
            text = (
                f"{header}\n"
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
            text = f"{header}\n🏆 **ТОП-10 ИГРОКОВ:**\nНажмите на игрока, чтобы посмотреть его профиль:\n\n"
            buttons = []
            if res and res.data:
                for i, u in enumerate(res.data, 1):
                    lvl = u.get('level', 1)
                    title = LEVELS.get(lvl, {}).get("title", "")
                    text += f"{i}. **{u.get('username')}** — Ур. `{lvl}` (*{title}*) | 🪙 `{u.get('coins'):,}`\n"
                    buttons.append([InlineKeyboardButton(text=f"👤 Профиль: {u.get('username')}", callback_data=f"view_profile_{u.get('user_id')}_{uid}")])
            else:
                text += "Игроков пока нет."
            buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")])
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        elif action == "work":
            text = f"{header}\n💼 **БИРЖА ТРУДА** (Баланс: `{p.get('coins', 0):,}` 🪙):\n\nВыберите смену:"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⛏ Шахтёр (40-90 🪙)", callback_data=f"do_work_1_{uid}")],
                [InlineKeyboardButton(text="🛡 Стражник (60-130 🪙)", callback_data=f"do_work_2_{uid}")],
                [InlineKeyboardButton(text="🧪 Алхимик (90-180 🪙)", callback_data=f"do_work_3_{uid}")],
                [InlineKeyboardButton(text="🐉 Охотник (130-260 🪙)", callback_data=f"do_work_4_{uid}")],
                [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
            ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()
            
        elif action == "casino":
            text = (
                f"{header}\n"
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
            if pid and str(pid) != "0" and pname and str(pname).upper() != "EMPTY":
                fam = await get_family(uid)
                budget = fam.get("budget", 0) if fam else 0
                food = fam.get("food", 100) if fam else 100
                house = fam.get("house", "❌ Нет") if fam else "❌ Нет"
                apartment = fam.get("apartment", "❌ Нет") if fam else "❌ Нет"
                car = fam.get("car", "❌ Нет") if fam else "❌ Нет"
                child_name = fam.get("child_name", "❌ Нет") if fam else "❌ Нет"
                child_hunger = fam.get("child_hunger", 100) if fam else 100
                
                if fam and child_name and child_name != "❌ Нет":
                    birth_time = int(fam.get("child_birth_time") or time.time())
                    child_age = format_age(int(time.time()) - birth_time)
                    child_info = f"{child_name} (Возраст: {child_age}, Голод: {child_hunger})"
                else:
                    child_info = "❌ Нет"

                m_time = int(p.get("marriage_time") or time.time())
                md = format_age(int(time.time()) - m_time)
                
                text = (
                    f"{header}\n"
                    f"💍 **СЕМЕЙНЫЙ ОЧАГ И ИМУЩЕСТВО:**\n\n"
                    f"💍 В браке с: **{pname}** (уже `{md}`)\n"
                    f"💰 Семейный бюджет: `{budget:,}` 🪙\n"
                    f"🍖 Еда: `{food}`\n"
                    f"🏡 Дом: `{house}`\n"
                    f"🏢 Квартира: `{apartment}`\n"
                    f"🚗 Машина семьи: `{car}`\n"
                    f"👶 Ребенок: `{child_info}`\n\n"
                    f"👇 Управляйте своей семьей через кнопки ниже:"
                )
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🍑 Уединиться (Секс)", callback_data=f"family_sex_select_{uid}")],
                    [InlineKeyboardButton(text="👶 Завести ребенка", callback_data=f"family_child_prompt_{uid}"),
                     InlineKeyboardButton(text="🍖 Покормить ребенка", callback_data=f"family_feed_child_{uid}")],
                    [InlineKeyboardButton(text="💰 Внести в бюджет", callback_data=f"family_deposit_prompt_{uid}"),
                     InlineKeyboardButton(text="💸 Снять с бюджета", callback_data=f"family_withdraw_prompt_{uid}")],
                    [InlineKeyboardButton(text="🛒 Семейный магазин", callback_data=f"family_shop_menu_{uid}")],
                    [InlineKeyboardButton(text="💔 Развестись", callback_data=f"action_divorce_{uid}"),
                     InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            else:
                text = f"{header}\n💍 **ОТНОШЕНИЯ И СЕМЬЯ:**\n\n💍 Вы свободны. Сделайте предложение любимому человеку через ответ на его сообщение и команду `/marry`"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{uid}")]
                ])
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await callback.answer()

        elif action == "support":
            await prompt_support(callback, state)
            return

        await callback.answer()
    except Exception as e:
        logging.error(f"Error in callback_main_menu: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@dp.callback_query(F.data.startswith("biz_manage_"))
async def biz_manage_menu(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    biz_id = int(parts[2])
    owner_id = parts[3] if len(parts) > 3 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    await update_businesses_for_user(uid)

    def _get_b():
        return supabase.table("user_businesses").select("*").eq("id", biz_id).eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_b)
    if not res.data:
        await callback.answer("❌ Бизнес не найден!", show_alert=True)
        return

    b = res.data[0]
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)

    b_type = b["business_type"]
    b_cat = BUSINESSES_CAT.get(b_type, {})
    
    workers = b["workers"]
    max_w = b["max_workers"]
    raw = b["raw_material"]
    max_r = b["max_raw_material"]

    up1 = b.get("up1_lvl", 0)
    up2 = b.get("up2_lvl", 0)
    up3 = b.get("up3_lvl", 0)

    raw_cost = b_cat.get("raw_cost_per_unit", 20) * 10
    hire_cost = 20000

    status_text = "🟢 Работает"
    if raw <= 0:
        status_text = "🔴 Остановлен (Нет сырья!)"
    elif (workers / max_w) < 0.5:
        status_text = "🟡 Простой (Мало работников < 50%)!"

    text = (
        f"{header}\n"
        f"🏢 **УПРАВЛЕНИЕ: {b['business_name']}** (Ур. {b['level']})\n"
        f"📊 Статус: {status_text}\n"
        f"💰 Доход: `{b['profit_per_hour']:,}` 🪙/час\n"
        f"💵 Накопленная прибыль: `+{b['balance_profit']:,}` 🪙\n"
        f"👷 Работники: `{workers} / {max_w}`\n"
        f"📦 Сырье: `{raw} / {max_r}`\n\n"
        f"👇 **Улучшения бизнеса:**\n"
    )

    buttons = [
        [InlineKeyboardButton(text=f"📥 Снять прибыль (+{b['balance_profit']:,} 🪙)", callback_data=f"biz_withdraw_{biz_id}_{uid}")],
        [InlineKeyboardButton(text=f"📦 Купить сырье (+10 ед.) — {raw_cost:,} 🪙", callback_data=f"biz_buy_raw_{biz_id}_{uid}")],
        [InlineKeyboardButton(text=f"👷 Нанять работников (+5) — {hire_cost:,} 🪙", callback_data=f"biz_hire_{biz_id}_{uid}")],
    ]

    for i, up_key in enumerate(["up1", "up2", "up3"], 1):
        up_data = b_cat.get(up_key)
        current_lvl = locals()[f"up{i}"]
        if current_lvl < 3:
            cost = up_data["price"] * (current_lvl + 1)
            text += f"• {up_data['name']} (Ур. {current_lvl}/3) — `{cost:,}` 🪙\n"
            buttons.append([InlineKeyboardButton(text=f"⬆️ Купить: {up_data['name']} [Ур.{current_lvl+1}] ({cost:,} 🪙)", callback_data=f"biz_up_buy_{biz_id}_{i}_{uid}")])
        else:
            text += f"• {up_data['name']} — ⭐ [МАКС УРОВЕНЬ]\n"

    buttons.append([InlineKeyboardButton(text="🔙 Назад к списку бизнесов", callback_data=f"menu_biz_{uid}")])

    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("biz_up_buy_"))
async def biz_upgrade_unique(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    biz_id = int(parts[3])
    up_idx = int(parts[4])
    uid = parts[5]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    def _get_b():
        return supabase.table("user_businesses").select("*").eq("id", biz_id).eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_b)
    if not res.data:
        await callback.answer("❌ Бизнес не найден!", show_alert=True)
        return
    b = res.data[0]
    b_cat = BUSINESSES_CAT.get(b["business_type"], {})
    
    up_key = f"up{up_idx}"
    current_lvl = b.get(f"{up_key}_lvl", 0)
    if current_lvl >= 3:
        await callback.answer("❌ Достигнут максимальный уровень улучшения!", show_alert=True)
        return

    up_data = b_cat.get(up_key)
    cost = up_data["price"] * (current_lvl + 1)

    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < cost:
        await callback.answer(f"❌ Недостаточно монет! Нужно {cost:,} 🪙", show_alert=True)
        return

    new_coins = p["coins"] - cost
    new_lvl = current_lvl + 1
    new_profit = b["profit_per_hour"] + up_data["profit_add"]

    def _up():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_businesses").update({
            "profit_per_hour": new_profit,
            f"{up_key}_lvl": new_lvl
        }).eq("id", biz_id).execute()
    await asyncio.to_thread(_up)

    await callback.answer(f"🎉 Успешно улучшено до уровня {new_lvl}!", show_alert=True)
    callback.data = f"biz_manage_{biz_id}_{uid}"
    await biz_manage_menu(callback)

@dp.callback_query(F.data.startswith("biz_shop_list_"))
async def biz_shop_list(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    
    text = f"{header}\n📈 **БИРЖА ПРЕДПРИЯТИЙ** (Баланс: `{p.get('coins', 0):,}` 🪙):\nВыберите бизнес для покупки (в порядке возрастания цены):\n\n"
    buttons = []

    for k, biz in BUSINESSES_CAT.items():
        text += f"• **{biz['name']}** — `{biz['price']:,}` 🪙 (Доход: `{biz['base_profit']:,}` 🪙/час)\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {biz['name']} ({biz['price']:,} 🪙)", callback_data=f"buy_biz_{k}_{uid}")])

    buttons.append([InlineKeyboardButton(text="🔙 К моим бизнесам", callback_data=f"menu_biz_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("buy_biz_"))
async def buy_business_action(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    biz_key = parts[2]
    uid = parts[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    biz_info = BUSINESSES_CAT.get(biz_key)
    if not biz_info:
        await callback.answer("❌ Бизнес не найден!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < biz_info["price"]:
        await callback.answer(f"❌ Недостаточно монет! Нужно {biz_info['price']:,} 🪙", show_alert=True)
        return

    new_coins = p["coins"] - biz_info["price"]
    now = int(time.time())

    def _buy():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_businesses").insert({
            "user_id": uid,
            "business_type": biz_key,
            "business_name": biz_info["name"],
            "level": 1,
            "profit_per_hour": biz_info["base_profit"],
            "raw_material": 0,
            "max_raw_material": 100,
            "workers": 0,
            "max_workers": 20,
            "balance_profit": 0,
            "last_update_time": now,
            "up1_lvl": 0,
            "up2_lvl": 0,
            "up3_lvl": 0
        }).execute()
    await asyncio.to_thread(_buy)

    await callback.answer(f"🎉 Вы успешно приобрели «{biz_info['name']}»! (Завезите сырье и наймите работников)", show_alert=True)
    callback.data = f"menu_biz_{uid}"
    await callback_main_menu(callback, None)

@dp.callback_query(F.data.startswith("biz_withdraw_"))
async def biz_withdraw(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    biz_id = int(parts[2])
    uid = parts[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    await update_businesses_for_user(uid)
    def _get_b():
        return supabase.table("user_businesses").select("*").eq("id", biz_id).eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_b)
    if not res.data:
        await callback.answer("❌ Бизнес не найден!", show_alert=True)
        return

    b = res.data[0]
    profit = b["balance_profit"]
    if profit <= 0:
        await callback.answer("❌ На балансе бизнеса пока нет прибыли для снятия!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    new_coins = p.get("coins", 0) + profit

    def _withdraw():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_businesses").update({"balance_profit": 0}).eq("id", biz_id).execute()
    await asyncio.to_thread(_withdraw)

    await callback.answer(f"✅ Успешно снято `+{profit:,}` 🪙 на ваш баланс!", show_alert=True)
    callback.data = f"biz_manage_{biz_id}_{uid}"
    await biz_manage_menu(callback)

@dp.callback_query(F.data.startswith("biz_buy_raw_"))
async def biz_buy_raw(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    biz_id = int(parts[2])
    uid = parts[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    def _get_b():
        return supabase.table("user_businesses").select("*").eq("id", biz_id).eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_b)
    if not res.data:
        await callback.answer("❌ Бизнес не найден!", show_alert=True)
        return
    b = res.data[0]
    b_cat = BUSINESSES_CAT.get(b["business_type"], {})
    cost = b_cat.get("raw_cost_per_unit", 20) * 10

    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < cost:
        await callback.answer(f"❌ Недостаточно монет! Нужно {cost:,} 🪙", show_alert=True)
        return

    new_raw = min(b["max_raw_material"], b["raw_material"] + 10)
    new_coins = p["coins"] - cost

    def _buy_r():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_businesses").update({"raw_material": new_raw}).eq("id", biz_id).execute()
    await asyncio.to_thread(_buy_r)

    await callback.answer(f"✅ Сырье успешно закуплено за {cost:,} 🪙 (+10 ед.)!", show_alert=True)
    callback.data = f"biz_manage_{biz_id}_{uid}"
    await biz_manage_menu(callback)

@dp.callback_query(F.data.startswith("biz_hire_"))
async def biz_hire(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    biz_id = int(parts[2])
    uid = parts[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    def _get_b():
        return supabase.table("user_businesses").select("*").eq("id", biz_id).eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_b)
    if not res.data:
        await callback.answer("❌ Бизнес не найден!", show_alert=True)
        return
    b = res.data[0]
    cost = 20000

    if b["workers"] >= b["max_workers"]:
        await callback.answer("❌ Штат работников полностью укомплектован!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    if p.get("coins", 0) < cost:
        await callback.answer(f"❌ Недостаточно монет для найма! Нужно {cost:,} 🪙", show_alert=True)
        return

    new_workers = min(b["max_workers"], b["workers"] + 5)
    new_coins = p["coins"] - cost

    def _h():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_businesses").update({"workers": new_workers}).eq("id", biz_id).execute()
    await asyncio.to_thread(_h)

    await callback.answer(f"✅ Нанято +5 новых работников за {cost:,} 🪙!", show_alert=True)
    callback.data = f"biz_manage_{biz_id}_{uid}"
    await biz_manage_menu(callback)

@dp.callback_query(F.data.startswith("car_refuel_menu_"))
async def car_refuel_menu(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    uid = parts[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    def _get_car():
        return supabase.table("user_cars").select("*").eq("id", car_id).execute()
    res = await asyncio.to_thread(_get_car)
    if not res.data:
        await callback.answer("❌ Машина не найдена!", show_alert=True)
        return
    car = res.data[0]
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)

    text = (
        f"{header}\n"
        f"⛽ **ЗАПРАВОЧНАЯ СТАНЦИЯ: {car['car_name']}**\n"
        f"🔋 Текущий бак: `{car['fuel_liters']:.1f} / {car['max_fuel_liters']} л`\n"
        f"⛽ Текущий бензин: `{car.get('fuel_type', 92)}`\n"
        f"🪙 Ваш баланс: `{p.get('coins', 0):,}` 🪙\n\n"
        f"Выберите вид топлива для заправки полного бака:"
    )

    buttons = []
    for f_key, f_data in FUEL_TYPES.items():
        liters_needed = car['max_fuel_liters'] - car['fuel_liters']
        full_cost = int(liters_needed * f_data['price_per_liter'])
        bonus_str = f" (+{int(f_data['bonus']*100)}% к мощи)" if f_data['bonus'] > 0 else ""
        buttons.append([InlineKeyboardButton(text=f"⛽ {f_data['name']} ({f_data['price_per_liter']}🪙/л) {bonus_str} — {full_cost:,} 🪙", callback_data=f"refuel_do_{car_id}_{f_key}_{uid}")])

    buttons.append([InlineKeyboardButton(text="🔙 В гараж", callback_data=f"menu_garage_{uid}")])

    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("refuel_do_"))
async def refuel_execute(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    f_type = int(parts[3])
    uid = parts[4]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    def _get_car():
        return supabase.table("user_cars").select("*").eq("id", car_id).execute()
    res = await asyncio.to_thread(_get_car)
    if not res.data:
        await callback.answer("❌ Машина не найдена!", show_alert=True)
        return
    car = res.data[0]
    p = await get_profile(callback.from_user)

    liters_needed = car['max_fuel_liters'] - car['fuel_liters']
    if liters_needed <= 0:
        await callback.answer("❌ Бак уже полностью заполнен!", show_alert=True)
        return

    f_data = FUEL_TYPES[f_type]
    total_cost = int(liters_needed * f_data['price_per_liter'])

    if p.get("coins", 0) < total_cost:
        await callback.answer(f"❌ Недостаточно монет! Нужно {total_cost:,} 🪙", show_alert=True)
        return

    new_coins = p["coins"] - total_cost
    new_fuel = float(car['max_fuel_liters'])

    def _refuel_db():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_cars").update({
            "fuel_liters": new_fuel,
            "fuel_type": f_type
        }).eq("id", car_id).execute()
    await asyncio.to_thread(_refuel_db)

    await callback.answer(f"✅ Успешно заправлено {liters_needed:.1f} л топлива {f_data['name']}!", show_alert=True)
    callback.data = f"menu_garage_{uid}"
    await callback_main_menu(callback, None)

@dp.callback_query(F.data.startswith("car_sell_"))
async def car_sell_action(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    owner_id = parts[3] if len(parts) > 3 else None
    
    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)

    def _get_car():
        return supabase.table("user_cars").select("*").eq("id", car_id).eq("user_id", uid).execute()
    res = await asyncio.to_thread(_get_car)
    if not res.data:
        await callback.answer("❌ Машина не найдена!", show_alert=True)
        return
    car = res.data[0]
    car_price = CARS_CAT.get(car["car_key"], {"price": 100000}).get("price", 100000)
    sell_price = int(car_price * 0.5)

    p = await get_profile(callback.from_user)
    new_coins = p.get("coins", 0) + sell_price

    def _sell():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("user_cars").delete().eq("id", car_id).execute()
        left_res = supabase.table("user_cars").select("*").eq("user_id", uid).execute()
        if left_res.data:
            supabase.table("user_cars").update({"is_active": True}).eq("id", left_res.data[0]["id"]).execute()
    await asyncio.to_thread(_sell)

    await callback.answer(f"✅ Машина продана за {sell_price:,} 🪙 (50% от стоимости)!", show_alert=True)
    callback.data = f"menu_garage_{uid}"
    await callback_main_menu(callback, None)

async def prompt_support(callback: types.CallbackQuery, state: FSMContext):
    uid = str(callback.from_user.id)
    p = await get_profile(callback.from_user)
    
    await state.set_state(SupportState.waiting_for_message)
    header = await get_menu_header(callback.from_user, p)
    text = (
        f"{header}\n"
        "🆘 **СЛУЖБА ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ**\n\n"
        "Напишите ваше сообщение или вопрос администраторам бота следующим сообщением.\n"
        "Ваш запрос будет переслан напрямую создателям."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data=f"back_home_{uid}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.message(Command("support"))
async def cmd_support(message: types.Message, state: FSMContext):
    await state.set_state(SupportState.waiting_for_message)
    await message.answer(
        "🆘 **СЛУЖБА ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ**\n\nОпишите вашу проблему или запрос следующим сообщением:",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(SupportState.waiting_for_message)
async def process_support_message(message: types.Message, state: FSMContext):
    await state.clear()
    sender = message.from_user
    text = message.text or message.caption or "[Медиафайл]"
    
    admin_text = (
        f"🆘 **НОВОЕ ОБРАЩЕНИЕ В ТЕХПОДДЕРЖКУ!**\n\n"
        f"👤 Игрок: **{sender.first_name}** (@{sender.username or 'нет_юзернейма'})\n"
        f"🆔 ID: `{sender.id}`\n\n"
        f"💬 **Сообщение:**\n{text}"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_supp_{sender.id}")]
    ])
    
    for admin_username in ADMIN_USERNAMES:
        ap = await get_profile_by_username(admin_username)
        if ap and ap.get("user_id"):
            try:
                await bot.send_message(chat_id=int(ap["user_id"]), text=admin_text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logging.error(f"Failed to send support ticket to admin {admin_username}: {e}")
                
    await message.answer(
        "✅ **Ваше обращение успешно отправлено администрации!**\nМы ответим вам в ближайшее время.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data=f"back_home_{sender.id}")]])
    )

@dp.callback_query(F.data.startswith("reply_supp_"))
async def callback_reply_support(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user):
        await callback.answer("❌ Вы не являетесь администратором!", show_alert=True)
        return
    target_uid = callback.data.split("_")[2]
    await state.set_state(SupportState.waiting_for_reply)
    await state.update_data(target_uid=target_uid)
    await callback.message.answer(
        f"✍️ Введите ответ для пользователя с ID `{target_uid}`:",
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()

@dp.message(SupportState.waiting_for_reply)
async def send_support_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_uid = data.get("target_uid")
    await state.clear()
    
    if not target_uid:
        await message.answer("❌ Ошибка получателя.")
        return
        
    reply_text = message.text
    user_msg = (
        f"🔔 **ОТВЕТ ОТ ТЕХПОДДЕРЖКИ:**\n\n"
        f"{reply_text}"
    )
    
    try:
        await bot.send_message(chat_id=int(target_uid), text=user_msg, parse_mode=ParseMode.MARKDOWN)
        await message.answer(f"✅ Ответ успешно доставлен пользователю `{target_uid}`!", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(
            f"❌ Не удалось отправить сообщение пользователю `{target_uid}`.\n"
            f"Ошибка: {e}", 
            parse_mode=ParseMode.MARKDOWN
        )

@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    if not is_admin(message.from_user):
        await message.answer("❌ У вас нет прав админа!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❌ Использование: `/reply <user_id> <текст ответа>`", parse_mode=ParseMode.MARKDOWN)
        return
    target_uid, reply_text = args[1], args[2]
    user_msg = f"🔔 **ОТВЕТ ОТ ТЕХПОДДЕРЖКИ:**\n\n{reply_text}"
    try:
        await bot.send_message(chat_id=int(target_uid), text=user_msg, parse_mode=ParseMode.MARKDOWN)
        await message.answer(f"✅ Ответ отправлен пользователю `{target_uid}`!", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(
            f"❌ Не удалось отправить сообщение пользователю `{target_uid}`.\n"
            f"Ошибка: {e}", 
            parse_mode=ParseMode.MARKDOWN
        )

@dp.message(Command("setpartner"))
async def admin_set_partner(message: types.Message):
    if not is_admin(message.from_user):
        await message.answer("❌ У вас нет прав администратора!")
        return

    args = message.text.split()
    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        target_name = message.reply_to_message.from_user.first_name
    else:
        if len(args) < 2:
            await message.answer("❌ Использование: `/setpartner` (реплаем) или `/setpartner <@user/id>`", parse_mode=ParseMode.MARKDOWN)
            return
        target_id, target_name = await resolve_target_user(message, args, identifier_index=1)
        if not target_id:
            await message.answer(target_name, parse_mode=ParseMode.MARKDOWN)
            return

    p = await get_profile_by_id(target_id)
    if not p:
        p = await get_profile(types.User(id=int(target_id), is_bot=False, first_name=target_name))

    current_status = p.get("is_partner", False)
    new_status = not current_status

    def _upd():
        supabase.table("users").update({"is_partner": new_status}).eq("user_id", str(target_id)).execute()
    await asyncio.to_thread(_upd)

    status_str = "🟢 назначен партнером" if new_status else "🔴 снят с должности партнера"
    await message.answer(f"✅ Пользователь **{target_name}** теперь {status_str}!", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("giveme"))
async def partner_give_me(message: types.Message):
    user = message.from_user
    p = await get_profile(user)
    
    is_user_admin = is_admin(user)
    is_user_partner = p.get("is_partner", False)

    if not is_user_admin and not is_user_partner:
        await message.answer("❌ У вас нет доступа к этой команде!")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: `/giveme <сумма>`", parse_mode=ParseMode.MARKDOWN)
        return

    try:
        amount = int(args[1])
        if amount <= 0: raise ValueError()
    except ValueError:
        await message.answer("❌ Укажите корректную сумму числом!")
        return

    now_dt = datetime.now()
    today_str = now_dt.strftime("%Y-%m-%d")

    seconds_left = 86400 - (now_dt.hour * 3600 + now_dt.minute * 60 + now_dt.second)
    hours_left = seconds_left // 3600
    minutes_left = (seconds_left % 3600) // 60
    time_reset_str = f"{hours_left} ч. {minutes_left} мин."

    if not is_user_admin and is_user_partner:
        last_date = p.get("partner_last_date", "")
        given_today = p.get("partner_given_today", 0)

        if last_date != today_str:
            given_today = 0
            last_date = today_str

        if given_today + amount > 1000000:
            remaining = max(0, 1000000 - given_today)
            await message.answer(
                f"❌ **Превышен суточный лимит партнерской программы!**\n\n"
                f"📊 Выдано сегодня: `{given_today:,}` / 1,000,000 🪙\n"
                f"💡 Доступно для выдачи: `{remaining:,}` 🪙\n"
                f"⏳ До обновления лимита осталось: `{time_reset_str}`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        given_today += amount
        new_coins = p.get("coins", 0) + amount

        def _upd_partner():
            supabase.table("users").update({
                "coins": new_coins,
                "partner_given_today": given_today,
                "partner_last_date": last_date
            }).eq("user_id", str(user.id)).execute()
        await asyncio.to_thread(_upd_partner)

        await message.answer(
            f"⭐️ **Партнерская выдача успешна!**\n\n"
            f"🪙 Выдано себе: `+{amount:,}` 🪙\n"
            f"📊 Лимит сегодня: `{given_today:,}` / 1,000,000 🪙\n"
            f"💰 Ваш новый баланс: `{new_coins:,}` 🪙\n"
            f"⏳ До обновления лимита осталось: `{time_reset_str}`",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        new_coins = p.get("coins", 0) + amount
        def _upd_admin():
            supabase.table("users").update({"coins": new_coins}).eq("user_id", str(user.id)).execute()
        await asyncio.to_thread(_upd_admin)
        await message.answer(f"✅ Администратору начислено `+{amount:,}` 🪙 (Баланс: `{new_coins:,}` 🪙)", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("use_item_"))
async def use_inventory_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("❌ Ошибка предмета!", show_alert=True)
        return
    idx = int(parts[2])
    item_key = parts[3]
    owner_id = parts[4] if len(parts) > 4 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваш инвентарь!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    uid = str(callback.from_user.id)
    inv_str = p.get("inventory") or ""
    items = [i.strip() for i in inv_str.split(",") if i.strip()]
    
    if idx >= len(items) or items[idx] != item_key:
        await callback.answer("❌ Предмет не найден в инвентаре!", show_alert=True)
        callback.data = f"menu_inv_{uid}"
        await callback_main_menu(callback, state)
        return
        
    items.pop(idx)
    new_inv = ",".join(items)
    
    coins = p.get("coins", 0)
    xp = p.get("xp", 0)
    respect = p.get("respect", 0)
    smoke_lvl = p.get("smoking_level", 0)
    
    effect_text = ""
    if item_key == "energy":
        xp += 50
        effect_text = "⚡ Вы выпили энергетик! (+50 XP)"
    elif item_key == "pizza":
        xp += 30
        coins += 20
        effect_text = "🍔 Вы съели пиццу! (+30 XP, +20 🪙)"
    elif item_key == "beer_okhota":
        earned = random.randint(50, 200)
        coins += earned
        effect_text = f"🍺 Вы выпили Охоту Крепкое! Настроение поднялось (+{earned} 🪙)"
    elif item_key == "vodka":
        if random.random() > 0.5:
            win = 500
            coins += win
            effect_text = f"🥃 Паленая водка ударила в голову! Вы нашли заначку (+{win} 🪙)"
        else:
            loss = min(300, coins)
            coins -= loss
            effect_text = f"🥃 От паленой водки стало плохо... Потеряно {loss} 🪙"
    elif item_key == "pc":
        respect += 150
        effect_text = "💻 Вы установили мощный игровой ПК! (+150 респекта)"
    elif item_key == "vr":
        respect += 220
        effect_text = "🥽 Вы погрузились в VR-мир! (+220 респекта)"
    elif item_key == "server":
        respect += 400
        effect_text = "🖥 Домашний сервер запущен! (+400 респекта)"
    elif item_key == "cigars":
        smoke_lvl += 1
        respect += 5
        effect_text = f"🚬 Вы выкурили сигарету. (Никотиновая зависимость ур. {smoke_lvl}, +5 респекта)"
    elif item_key == "hookah":
        xp += 80
        effect_text = "💨 Густой дым кальяна расслабил вас! (+80 XP)"
    elif item_key == "chips":
        xp += 15
        effect_text = "🍟 Хрустящие чипсы дали сил! (+15 XP)"
    elif item_key == "whiskey":
        respect += 40
        coins += 50
        effect_text = "🥃 Элитный виски добавил солидности! (+40 респекта, +50 🪙)"
    elif item_key == "chair":
        respect += 100
        effect_text = "💺 Геймерское кресло обеспечило комфорт! (+100 респекта)"
    elif item_key.startswith("sex_"):
        sex_item = SEX_SHOP.get(item_key, {"name": "Игрушка"})
        respect += 25
        effect_text = f"🍑 Вы использовали «{sex_item['name']}»! Получено море эмоций (+25 респекта)"
    else:
        effect_text = f"🎁 Вы использовали предмет `{item_key}`!"

    new_level = p.get("level", 1)
    for lvl, d in sorted(LEVELS.items(), key=lambda x: x[0]):
        if xp >= d["xp"]: new_level = lvl

    def _upd():
        supabase.table("users").update({
            "inventory": new_inv,
            "coins": coins,
            "xp": xp,
            "respect": respect,
            "smoking_level": smoke_lvl,
            "level": new_level
        }).eq("user_id", uid).execute()
    await asyncio.to_thread(_upd)
    
    await callback.answer(effect_text, show_alert=True)
    callback.data = f"menu_inv_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("equip_item_"))
async def equip_item_handler(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("❌ Ошибка снаряжения!", show_alert=True)
        return
    eq_key = f"{parts[2]}_{parts[3]}"
    owner_id = parts[4] if len(parts) > 4 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваша оружейная!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    p = await get_profile(callback.from_user)
    armory_str = p.get("armory") or ""
    items = [i.strip() for i in armory_str.split(",") if i.strip()]
    
    if eq_key not in items:
        await callback.answer("❌ У вас нет этого предмета в оружейной!", show_alert=True)
        return
        
    def _upd():
        supabase.table("users").update({"equipped_item": eq_key}).eq("user_id", uid).execute()
    await asyncio.to_thread(_upd)
    
    eq_data = SHOP_EQUIPMENT.get(eq_key, {"name": eq_key})
    await callback.answer(f"✅ Вы надели: {eq_data['name']}!", show_alert=True)
    callback.data = f"menu_armory_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("unequip_item_"))
async def unequip_item_handler(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.data.split("_")[2]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
        
    def _upd():
        supabase.table("users").update({"equipped_item": ""}).eq("user_id", uid).execute()
    await asyncio.to_thread(_upd)
    
    await callback.answer("🛑 Экипировка снята.", show_alert=True)
    callback.data = f"menu_armory_{uid}"
    await callback_main_menu(callback, state)

@dp.callback_query(F.data.startswith("view_profile_"))
async def view_other_profile(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    target_uid = parts[2]
    owner_id = parts[3] if len(parts) > 3 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    p = await get_profile_by_id(target_uid)
    if not p:
        await callback.answer("❌ Профиль не найден!", show_alert=True)
        return

    lvl = p.get('level', 1)
    title = LEVELS.get(lvl, {}).get("title", "Воин")
    pid, pname = p.get("partner_id"), p.get("partner_name")
    
    created_at = int(p.get("created_at") or time.time())
    bot_age = format_age(int(time.time()) - created_at)
    
    if pid and str(pid) != "0" and pname and str(pname).upper() != "EMPTY":
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

    class DummyUser:
        def __init__(self, username):
            self.username = username
    
    dummy_u = DummyUser(p.get("username"))
    admin_tag = " 🟢 **(админ)**" if is_admin(dummy_u) else ""
    partner_tag = " ⭐️ **(партнер)**" if p.get("is_partner") else ""

    text = (
        f"👤 **Профиль игрока: {p.get('username')}**{admin_tag}{partner_tag} (Просмотр)\n"
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

@dp.callback_query(F.data.startswith("profile_music_menu_"))
async def profile_music_menu(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    has_music = bool(p.get("profile_music"))
    header = await get_menu_header(callback.from_user, p)
    
    text = (
        f"{header}\n"
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

@dp.callback_query(F.data.startswith("shop_cars_list_"))
async def shop_cars_list(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    text = f"{header}\n🏎 **АВТОСАЛОН** (Баланс: `{p.get('coins', 0):,}` 🪙):\nВыберите машину для покупки (от дешевых к дорогим):\n\n"
    buttons = []
    for k, car in CARS_CAT.items():
        if car.get("admin_only"):
            text += f"• **{car['name']}** — 🔒 *Эксклюзив (Только от админа)* (Скорость: {car['base_speed']} км/ч)\n"
        else:
            text += f"• **{car['name']}** — `{car['price']:,}` 🪙 (Скорость: {car['base_speed']} км/ч, Разгон: {car['accel']}с)\n"
            buttons.append([InlineKeyboardButton(text=f"Купить: {car['name']} ({car['price']:,} 🪙)", callback_data=f"buy_car_{k}_{uid}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 В меню магазинов", callback_data=f"menu_shops_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
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
            "is_active": is_first,
            "fuel_liters": float(car_info["tank"]),
            "max_fuel_liters": car_info["tank"],
            "fuel_type": 92
        }).execute()
    await asyncio.to_thread(_insert_car)

    await callback.answer(f"🎉 Вы успешно купили {car_info['name']} с полным баком!", show_alert=True)
    callback.data = f"menu_garage_{uid}"
    await callback_main_menu(callback, None)

@dp.callback_query(F.data.startswith("car_activate_"))
async def car_activate(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    owner_id = parts[3] if len(parts) > 3 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

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
    parts = callback.data.split("_")
    car_id = int(parts[2])
    owner_id = parts[3] if len(parts) > 3 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    def _get_car():
        return supabase.table("user_cars").select("*").eq("id", car_id).execute()
    res = await asyncio.to_thread(_get_car)
    if not res.data:
        await callback.answer("❌ Машина не найдена!", show_alert=True)
        return
    car = res.data[0]
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)

    engine_cost = car["engine_lvl"] * 20000
    turbo_cost = car["turbo_lvl"] * 35000
    handling_cost = car["handling_lvl"] * 15000
    car_base = CARS_CAT.get(car["car_key"], {"price": 100000})
    sell_price = int(car_base['price'] * 0.5)

    text = (
        f"{header}\n"
        f"⚙️ **ТЮНИНГ И ПОКРАСКА: {car['car_name']}**\n"
        f"🎨 Текущий цвет: {car['color']}\n"
        f"🪙 Ваш баланс: `{p.get('coins', 0):,}` 🪙\n\n"
        f"🔹 Двигатель (Ур. {car['engine_lvl']}) — ` апгрейд: {engine_cost:,} 🪙`\n"
        f"🔸 Турбина (Ур. {car['turbo_lvl']}) — `⚡ апгрейд: {turbo_cost:,} 🪙`\n"
        f"🟢 Подвеска (Ур. {car['handling_lvl']}) — `🛡 апгрейд: {handling_cost:,} 🪙`\n"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⬆️ Улучшить Двигатель ({engine_cost:,} 🪙)", callback_data=f"up_car_{car_id}_engine_{uid}")],
        [InlineKeyboardButton(text=f"⬆️ Улучшить Турбину ({turbo_cost:,} 🪙)", callback_data=f"up_car_{car_id}_turbo_{uid}")],
        [InlineKeyboardButton(text=f"⬆️ Улучшить Руль ({handling_cost:,} 🪙)", callback_data=f"up_car_{car_id}_handling_{uid}")],
        [InlineKeyboardButton(text="🎨 Выбрать цвет покраски (8 цветов)", callback_data=f"paint_car_menu_{car_id}_{uid}")],
        [InlineKeyboardButton(text=f"🗑 Продать за {sell_price:,} 🪙", callback_data=f"car_sell_{car_id}_{uid}")],
        [InlineKeyboardButton(text="🔙 В гараж", callback_data=f"menu_garage_{uid}")]
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
    owner_id = parts[4] if len(parts) > 4 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

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
    callback.data = f"car_tune_{car_id}_{p['user_id']}"
    await car_tune_menu(callback)

@dp.callback_query(F.data.startswith("paint_car_menu_"))
async def paint_car_menu(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[3])
    owner_id = parts[4] if len(parts) > 4 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    buttons = []
    for color in CAR_COLORS:
        buttons.append([InlineKeyboardButton(text=f"🎨 {color}", callback_data=f"set_color_{car_id}_{color}_{owner_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к тюнингу", callback_data=f"car_tune_{car_id}_{owner_id}")])

    try:
        await callback.message.edit_text("🎨 **ВЫБЕРИТЕ ЦВЕТ ДЛЯ ПОКРАСКИ МАШИНЫ:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("set_color_"))
async def set_car_color(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    car_id = int(parts[2])
    color = parts[3]
    owner_id = parts[4] if len(parts) > 4 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    def _update_color():
        supabase.table("user_cars").update({"color": color}).eq("id", car_id).execute()
    await asyncio.to_thread(_update_color)

    await callback.answer(f"🎨 Машина перекрашена в {color}!", show_alert=True)
    callback.data = f"car_tune_{car_id}_{owner_id}"
    await car_tune_menu(callback)

@dp.message(Command("race"))
async def cmd_race(message: types.Message):
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение соперника командой `/race <ставка>`, чтобы бросить ему вызов по согласию.", parse_mode=ParseMode.MARKDOWN)
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Укажите ставку: `/race <ставка>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        bet = int(args[1])
        if bet <= 0: raise ValueError()
    except ValueError:
        await message.answer("❌ Неверная ставка!")
        return
        
    challenger = message.from_user
    target = message.reply_to_message.from_user
    if challenger.id == target.id:
        await message.answer("❌ Нельзя соревноваться с самим собой!")
        return
    if target.is_bot:
        await message.answer("❌ Нельзя соревноваться с ботом!")
        return
        
    p1 = await get_profile(challenger)
    if p1.get("coins", 0) < bet:
        await message.answer("❌ У вас недостаточно монет для такой ставки!")
        return
        
    PENDING_RACES[str(target.id)] = {"challenger_id": str(challenger.id), "bet": bet}
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏁 Принять гонку", callback_data=f"race_accept_{target.id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"race_decline_{target.id}")]
    ])
    await message.answer(f"🏁 **{target.first_name}**, вас вызвали на уличную гонку со ставкой `{bet:,}` 🪙 от **{challenger.first_name}**!", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("race_accept_"))
async def race_accept(callback: types.CallbackQuery):
    target_id = callback.data.split("_")[2]
    if str(callback.from_user.id) != target_id:
        await callback.answer("❌ Вызов предназначался не вам!", show_alert=True)
        return

    data = PENDING_RACES.get(target_id)
    if not data:
        await callback.answer("❌ Вызов устарел!", show_alert=True)
        return
    challenger_id = data["challenger_id"]
    bet = data["bet"]
    
    p_challenger = await get_profile_by_id(challenger_id)
    p_target = await get_profile_by_id(target_id)
    if p_challenger["coins"] < bet or p_target["coins"] < bet:
        await callback.answer("❌ У кого-то из участников не хватает монет!", show_alert=True)
        return
        
    def _get_car(uid):
        res = supabase.table("user_cars").select("*").eq("user_id", uid).eq("is_active", True).execute()
        return res.data[0] if res.data else None
    car1 = _get_car(challenger_id)
    car2 = _get_car(target_id)
    if not car1 or not car2:
        await callback.answer("❌ У одного из участников нет активной машины в гараже!", show_alert=True)
        return

    if car1.get("fuel_liters", 0.0) < 3.0 or car2.get("fuel_liters", 0.0) < 3.0:
        await callback.answer("❌ У одного из участников в баке меньше 3 литров топлива! Заправьтесь.", show_alert=True)
        return
        
    c_info1 = CARS_CAT.get(car1["car_key"], {"base_speed": 200})
    c_info2 = CARS_CAT.get(car2["car_key"], {"base_speed": 200})

    bonus1 = FUEL_TYPES.get(car1.get("fuel_type", 92), {"bonus": 0.0})["bonus"]
    bonus2 = FUEL_TYPES.get(car2.get("fuel_type", 92), {"bonus": 0.0})["bonus"]

    power1 = (c_info1["base_speed"] + car1["engine_lvl"]*15 + car1["turbo_lvl"]*20) * (1.0 + bonus1)
    power2 = (c_info2["base_speed"] + car2["engine_lvl"]*15 + car2["turbo_lvl"]*20) * (1.0 + bonus2)
    
    win_challenger = power1 >= power2
    winner_id = challenger_id if win_challenger else target_id
    
    xp_gain = max(2, int(bet / 5000))
    
    def _execute_race():
        new_f1 = max(0.0, car1["fuel_liters"] - 3.0)
        new_f2 = max(0.0, car2["fuel_liters"] - 3.0)
        supabase.table("user_cars").update({"fuel_liters": new_f1}).eq("id", car1["id"]).execute()
        supabase.table("user_cars").update({"fuel_liters": new_f2}).eq("id", car2["id"]).execute()

        supabase.table("users").update({"coins": p_challenger["coins"] - bet}).eq("user_id", challenger_id).execute()
        supabase.table("users").update({"coins": p_target["coins"] - bet}).eq("user_id", target_id).execute()
        
        w_p = p_challenger if win_challenger else p_target
        new_xp = w_p["xp"] + xp_gain
        new_level = w_p["level"]
        for lvl, d in sorted(LEVELS.items(), key=lambda x: x[0]):
            if new_xp >= d["xp"]: new_level = lvl
            
        supabase.table("users").update({
            "coins": w_p["coins"] + bet * 2,
            "xp": new_xp,
            "level": new_level
        }).eq("user_id", winner_id).execute()
    await asyncio.to_thread(_execute_race)
    
    PENDING_RACES.pop(target_id, None)
    w_name = p_challenger["username"] if win_challenger else p_target["username"]
    await callback.message.edit_text(f"🏁 **ГОНКА ЗАВЕРШЕНА!** (Сжёг по 3л топлива)\n\n🏆 Победитель: **{w_name}**!\n💰 Выигрыш: `+{bet*2:,}` 🪙\n✨ Опыт: `+{xp_gain} XP`", parse_mode=ParseMode.MARKDOWN)
    await callback.answer("Гонка завершена!")

@dp.callback_query(F.data.startswith("race_decline_"))
async def race_decline(callback: types.CallbackQuery):
    target_id = callback.data.split("_")[2]
    if str(callback.from_user.id) != target_id:
        await callback.answer("❌ Вызов предназначался не вам!", show_alert=True)
        return
    PENDING_RACES.pop(target_id, None)
    await callback.message.edit_text("❌ Вызов на гонку отклонен.")
    await callback.answer("Отклонено")

@dp.callback_query(F.data.startswith("shop_eq_list_"))
async def callback_shop_eq(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    text = f"{header}\n⚔️ **МАГАЗИН СНАРЯЖЕНИЯ** (Баланс: `{p.get('coins', 0):,}` 🪙):\n(Отсортировано по возрастанию цены)\n\n"
    buttons = []
    for item_id, data in SHOP_EQUIPMENT.items():
        text += f"🔹 **{data['name']}** — `{data['price']:,}` 🪙\n   └ *{data['desc']}*\n\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']} ({data['price']:,} 🪙)", callback_data=f"buy_eq_{item_id}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 В меню магазинов", callback_data=f"menu_shops_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("shop_cons_list_"))
async def callback_shop_cons(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    text = f"{header}\n🍺 **ПРОДУКТЫ И ТЕХНИКА** (Баланс: `{p.get('coins', 0):,}` 🪙):\n(Отсортировано по возрастанию цены)\n\n"
    buttons = []
    for item_id, data in SHOP_CONSUMABLES.items():
        text += f"🔹 **{data['name']}** — `{data['price']:,}` 🪙\n   └ *{data['desc']}*\n\n"
        buttons.append([InlineKeyboardButton(text=f"Купить: {data['name']} ({data['price']:,} 🪙)", callback_data=f"buy_cons_{item_id}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 В меню магазинов", callback_data=f"menu_shops_{uid}")])
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
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
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

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
    callback.data = f"shop_cons_list_{uid}"
    await callback_shop_cons(callback)

@dp.callback_query(F.data.startswith("buy_sex_"))
async def buy_sex_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    uid = parts[-1]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

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
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    buttons = []
    for k, v in APARTMENTS_CAT.items():
        sell_p = int(v['price'] * 0.5)
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']:,} 🪙 (Продажа: {sell_p:,})", callback_data=f"pers_buy_apt_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    try:
        await callback.message.edit_text(f"{header}\n🏢 **РЫНОК КВАРТИР (от дешевых к элитным)**\nБаланс: `{p.get('coins', 0):,}` 🪙\nВыберите вариант:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("pers_shop_house_"))
async def pers_shop_house(callback: types.CallbackQuery):
    uid = callback.data.split("_")[3]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    buttons = []
    for k, v in HOUSES_CAT.items():
        sell_p = int(v['price'] * 0.5)
        buttons.append([InlineKeyboardButton(text=f"{v['name']} — {v['price']:,} 🪙 (Продажа: {sell_p:,})", callback_data=f"pers_buy_house_{k}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к имуществу", callback_data=f"menu_personal_{uid}")])
    try:
        await callback.message.edit_text(f"{header}\n🏡 **РЫНОК ДОМОВ (от дач до островов)**\nБаланс: `{p.get('coins', 0):,}` 🪙\nВыберите вариант:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

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

@dp.message(Command("work"))
async def cmd_work(message: types.Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    now = time.time()
    header = await get_menu_header(message.from_user, p)
    if now - WORK_COOLDOWNS.get(uid, 0) < 60:
        await message.answer(f"⏳ Отдохните еще `{int(60 - (now - WORK_COOLDOWNS.get(uid, 0)))}` сек.", parse_mode=ParseMode.MARKDOWN)
        return
    if len(args) < 2 or args[1] not in JOBS:
        text = f"{header}\n💼 **БИРЖА ТРУДА** (Баланс: `{p.get('coins', 0):,}` 🪙):\n"
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

@dp.callback_query(F.data.startswith("do_work_"))
async def do_work_callback(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    job_id = parts[2]
    uid = parts[3] if len(parts) > 3 else str(callback.from_user.id)
    
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
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
    
    text = f"{header}\n💼 **БИРЖА ТРУДА** (Баланс: `{new_coins:,}` 🪙):\n\n✅ Последняя смена ({job['name']}): `+{earned_coins} 🪙`, `+{earned_xp} XP`\n\nВыберите смену:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⛏ Шахтёр (40-90 🪙)", callback_data=f"do_work_1_{uid}")],
        [InlineKeyboardButton(text="🛡 Стражник (60-130 🪙)", callback_data=f"do_work_2_{uid}")],
        [InlineKeyboardButton(text="🧪 Алхимик (90-180 🪙)", callback_data=f"do_work_3_{uid}")],
        [InlineKeyboardButton(text="🐉 Охотник (130-260 🪙)", callback_data=f"do_work_4_{uid}")],
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

@dp.message(Command("marry"))
async def cmd_marry(message: types.Message):
    if not message.reply_to_message:
        await message.answer("💍 Ответьте на сообщение игрока командой `/marry`, чтобы сделать предложение о браке!", parse_mode=ParseMode.MARKDOWN)
        return
    user1 = message.from_user
    user2 = message.reply_to_message.from_user
    if user1.id == user2.id:
        await message.answer("❌ Нельзя жениться на себе!")
        return
    if user2.is_bot:
        await message.answer("❌ Нельзя жениться на боте!")
        return
        
    p1 = await get_profile(user1)
    p2 = await get_profile(user2)
    
    if p1.get("partner_id") and str(p1.get("partner_id")) != "0" and p1.get("partner_name") != "EMPTY":
        await message.answer("❌ Вы уже состоите в браке!")
        return
    if p2.get("partner_id") and str(p2.get("partner_id")) != "0" and p2.get("partner_name") != "EMPTY":
        await message.answer("❌ Этот игрок уже состоит в браке!")
        return
        
    PENDING_MARRIAGES[str(user2.id)] = str(user1.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💍 Принять", callback_data=f"marry_accept_{user1.id}_{user2.id}"),
         InlineKeyboardButton(text="💔 Отклонить", callback_data=f"marry_decline_{user2.id}")]
    ])
    await message.answer(f"💍 **{user2.first_name}**, вам сделали предложение от **{user1.first_name}**!", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("marry_accept_"))
async def marry_accept(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    target_id = parts[2]
    user2_id = parts[3]
    
    if str(callback.from_user.id) != user2_id:
        await callback.answer("❌ Предложение адресовано не вам!", show_alert=True)
        return

    if PENDING_MARRIAGES.get(user2_id) != target_id:
        await callback.answer("❌ Предложение неактуально!", show_alert=True)
        return
        
    p1 = await get_profile_by_id(target_id)
    p2 = await get_profile_by_id(user2_id)
    
    now = int(time.time())
    family_data = {
        "partner1_id": target_id,
        "partner2_id": user2_id,
        "budget": 0,
        "food": 100,
        "house": "❌ Нет",
        "apartment": "❌ Нет",
        "car": "❌ Нет",
        "child_name": "❌ Нет",
        "child_hunger": 100,
        "child_birth_time": now
    }
    def _ins():
        supabase.table("users").update({"partner_id": user2_id, "partner_name": p2["username"], "marriage_time": now}).eq("user_id", target_id).execute()
        supabase.table("users").update({"partner_id": target_id, "partner_name": p1["username"], "marriage_time": now}).eq("user_id", user2_id).execute()
        supabase.table("families").insert(family_data).execute()
    await asyncio.to_thread(_ins)
    PENDING_MARRIAGES.pop(user2_id, None)
    
    await callback.message.edit_text(f"💍 **ПОЗДРАВЛЯЕМ!** 🎉\n\n**{p1['username']}** и **{p2['username']}** официально заключили брак!", parse_mode=ParseMode.MARKDOWN)
    await callback.answer("💍 Брак заключен!")

@dp.callback_query(F.data.startswith("marry_decline_"))
async def marry_decline(callback: types.CallbackQuery):
    user2_id = callback.data.split("_")[2]
    if str(callback.from_user.id) != user2_id:
        await callback.answer("❌ Это предложение не вам!", show_alert=True)
        return
    PENDING_MARRIAGES.pop(user2_id, None)
    await callback.message.edit_text("💔 Предложение было отклонено.")
    await callback.answer("Отклонено")

@dp.message(Command("divorce"))
async def cmd_divorce_msg(message: types.Message):
    await process_divorce(message.from_user, message)

@dp.callback_query(F.data.startswith("action_divorce_"))
async def callback_divorce(callback: types.CallbackQuery, state: FSMContext):
    owner_id = callback.data.split("_")[2]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    await process_divorce(callback.from_user, callback.message, callback=callback)
    uid = str(callback.from_user.id)
    callback.data = f"menu_marry_{uid}"
    await callback_main_menu(callback, state)

async def process_divorce(user, message_obj, callback=None):
    uid = str(user.id)
    p = await get_profile(user)
    pid = p.get("partner_id")
    if not pid or str(pid) == "0" or p.get("partner_name") == "EMPTY":
        if callback: await callback.answer("❌ Вы не в браке!", show_alert=True)
        else: await message_obj.answer("❌ Вы не в браке!")
        return
        
    def _div():
        supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY", "marriage_time": 0}).eq("user_id", uid).execute()
        supabase.table("users").update({"partner_id": 0, "partner_name": "EMPTY", "marriage_time": 0}).eq("user_id", str(pid)).execute()
        supabase.table("families").delete().or_(f"partner1_id.eq.{uid},partner2_id.eq.{uid}").execute()
    await asyncio.to_thread(_div)
    
    text = "💔 Вы успешно развелись."
    if callback: await callback.answer(text, show_alert=True)
    else: await message_obj.answer(text)

@dp.callback_query(F.data.startswith("family_sex_select_"))
async def family_sex_select(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    owner_id = parts[3]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    p = await get_profile(callback.from_user)
    header = await get_menu_header(callback.from_user, p)
    pid = p.get("partner_id")
    if not pid or str(pid) == "0" or p.get("partner_name") == "EMPTY":
        await callback.answer("❌ У вас нет партнера!", show_alert=True)
        return
    
    inv_str = p.get("inventory") or ""
    items = [i.strip() for i in inv_str.split(",") if i.strip()]
    
    sex_items_unsorted = [item for item in items if item.startswith("sex_")]
    sex_items = sorted(sex_items_unsorted, key=lambda x: SEX_SHOP.get(x, {}).get("price", 0))
    
    text = f"{header}\n🍑 **ВЫБОР ИГРУШКИ ДЛЯ СТРАСТИ**\n\n(Отсортировано по возрастанию стоимости)\nВыберите игрушку из инвентаря или классику:"
    buttons = []
    for s_item in sex_items:
        item_data = SEX_SHOP.get(s_item, {"name": s_item, "price": 0})
        buttons.append([InlineKeyboardButton(text=f"🔥 {item_data['name']} — {item_data['price']:,} 🪙", callback_data=f"family_sex_do_{s_item}_{uid}")])
    buttons.append([InlineKeyboardButton(text="🔥 Без игрушек (Классика)", callback_data=f"family_sex_do_none_{uid}")])
    buttons.append([InlineKeyboardButton(text="💍 Назад в семью", callback_data=f"menu_marry_{uid}")])
    
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("family_sex_do_"))
async def family_sex_execute(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    uid = parts[-1]
    if str(callback.from_user.id) != uid:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    item_key = "_".join(parts[3:-1])
    now = time.time()
    if now - INTIMATE_COOLDOWNS.get(uid, 0) < 300:
        rem = int(300 - (now - INTIMATE_COOLDOWNS.get(uid, 0)))
        await callback.answer(f"⏳ Отдохните еще {rem // 60} мин. {rem % 60} сек.", show_alert=True)
        return
    
    p = await get_profile(callback.from_user)
    pid = p.get("partner_id")
    if not pid or str(pid) == "0" or p.get("partner_name") == "EMPTY":
        await callback.answer("❌ У вас нет партнера!", show_alert=True)
        return
    
    inv_str = p.get("inventory") or ""
    items = [i.strip() for i in inv_str.split(",") if i.strip()]
    
    toy_desc = ""
    if item_key != "none":
        if item_key in items:
            items.remove(item_key)
            new_inv = ",".join(items)
            supabase.table("users").update({"inventory": new_inv}).eq("user_id", uid).execute()
            toy_desc = SEX_DESCRIPTIONS.get(item_key, "")
    
    INTIMATE_COOLDOWNS[uid] = now
    xp_gain = random.randint(50, 120)
    respect_gain = random.randint(15, 35)
    
    new_xp = p.get("xp", 0) + xp_gain
    new_respect = p.get("respect", 0) + respect_gain
    
    new_level = p.get("level", 1)
    for lvl, d in sorted(LEVELS.items(), key=lambda x: x[0]):
        if new_xp >= d["xp"]: new_level = lvl
    
    supabase.table("users").update({
        "xp": new_xp,
        "respect": new_respect,
        "level": new_level
    }).eq("user_id", uid).execute()
    
    vulgar_desc = (
        f"🍑 **РАЗВУТНАЯ И СТРАСТНАЯ НОЧЬ С {str(p.get('partner_name')).upper()}** 🍑\n\n"
        f"Вы срываете друг с друга остатки одежды, обнажая жаждущие тела. Пул зычных стонов, горячее дыхание и неистовые прикосновения наполняют комнату. "
        f"Вы грубо прижимаете партнера к постели, впиваясь губами в шею и оставляя багровые следы. Ритм нарастает до бешеной скорости, каждый толчок отдается сладкой судорогой по всему телу, приводя обоих к дикому, изнуряющему оргазму.\n\n"
    )
    if toy_desc:
        vulgar_desc += f"{toy_desc}\n\n"
    
    vulgar_desc += f"✨ Получено опыта: `+{xp_gain} XP`\n❤️ Получено респекта: `+{respect_gain}`"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Повторить страсть", callback_data=f"family_sex_select_{uid}")],
        [InlineKeyboardButton(text="💍 В меню семьи", callback_data=f"menu_marry_{uid}")]
    ])
    try:
        await callback.message.edit_text(vulgar_desc, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.message.answer(vulgar_desc, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    await callback.answer("🔥 Было безумно жарко!")

@dp.callback_query(F.data.startswith("family_child_prompt_"))
async def family_child_prompt(callback: types.CallbackQuery, state: FSMContext):
    owner_id = callback.data.split("_")[3]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    fam = await get_family(uid)
    if not fam:
        await callback.answer("❌ У вас нет семьи!", show_alert=True)
        return
    if fam.get("child_name") and fam.get("child_name") != "❌ Нет":
        await callback.answer("❌ У вас уже есть ребенок!", show_alert=True)
        return
    await state.set_state(FamilyState.waiting_for_child_name)
    await callback.message.edit_text(
        "👶 **РОЖДЕНИЕ РЕБЕНКА**\n\nВведите имя для вашего будущего ребенка следующим сообщением:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в семью", callback_data=f"menu_marry_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(FamilyState.waiting_for_child_name)
async def process_child_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) > 30:
        await message.answer("❌ Имя слишком длинное! Введите короче:")
        return
    uid = str(message.from_user.id)
    fam = await get_family(uid)
    if fam:
        now = int(time.time())
        def _save_child():
            supabase.table("families").update({"child_name": name, "child_hunger": 100, "child_birth_time": now}).eq("family_id", fam["family_id"]).execute()
        await asyncio.to_thread(_save_child)
    await state.clear()
    
    await message.answer(
        f"🎉 **ПОЗДРАВЛЯЕМ!** У вас родился ребенок по имени **{name}**! 👶🍼",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💍 В меню семьи", callback_data=f"menu_marry_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.callback_query(F.data.startswith("family_feed_child_"))
async def family_feed_child(callback: types.CallbackQuery):
    owner_id = callback.data.split("_")[3]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    fam = await get_family(uid)
    if not fam or fam.get("child_name") == "❌ Нет":
        await callback.answer("❌ У вас нет ребенка!", show_alert=True)
        return
    if fam.get("child_hunger", 100) >= 100:
        await callback.answer("👶 Ребенок уже сыт!", show_alert=True)
        return
    if fam.get("food", 0) < 10:
        await callback.answer("❌ В семье закончилась еда! Купите еду в семейном магазине.", show_alert=True)
        return
        
    new_food = fam["food"] - 10
    new_hunger = min(100, fam["child_hunger"] + 30)
    def _feed():
        supabase.table("families").update({"food": new_food, "child_hunger": new_hunger}).eq("family_id", fam["family_id"]).execute()
    await asyncio.to_thread(_feed)
    await callback.answer(f"🍖 Вы покормили ребенка! Сытость: {new_hunger} (Еда семьи: {new_food})", show_alert=True)
    callback.data = f"menu_marry_{uid}"
    await callback_main_menu(callback, None)

@dp.callback_query(F.data.startswith("family_deposit_prompt_"))
async def family_deposit_prompt(callback: types.CallbackQuery, state: FSMContext):
    owner_id = callback.data.split("_")[3]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    fam = await get_family(uid)
    if not fam:
        await callback.answer("❌ Вы не в браке!", show_alert=True)
        return
    p = await get_profile(callback.from_user)
    await state.set_state(FamilyState.waiting_for_deposit_amount)
    await callback.message.edit_text(
        f"💰 **СЕМЕЙНЫЙ БЮДЖЕТ**\n\nВаш баланс: `{p.get('coins', 0):,}` 🪙\nВведите сумму, которую хотите положить в общий семейный бюджет:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в семью", callback_data=f"menu_marry_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(FamilyState.waiting_for_deposit_amount)
async def process_deposit_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount <= 0: raise ValueError()
    except ValueError:
        await message.answer("❌ Введите корректную сумму числом:")
        return
        
    uid = str(message.from_user.id)
    p = await get_profile(message.from_user)
    if p.get("coins", 0) < amount:
        await message.answer(f"❌ У вас недостаточно монет! На балансе `{p.get('coins', 0):,}` 🪙")
        return
        
    fam = await get_family(uid)
    if not fam:
        await message.answer("❌ Семья не найдена!")
        await state.clear()
        return

    new_coins = p.get("coins", 0) - amount
    new_budget = fam.get("budget", 0) + amount
    
    def _save_dep():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("families").update({"budget": new_budget}).eq("family_id", fam["family_id"]).execute()
    await asyncio.to_thread(_save_dep)
    await state.clear()
    
    await message.answer(
        f"✅ Вы успешно внесли `{amount:,}` 🪙 в семейный бюджет!\n💰 Общий семейный бюджет: `{new_budget:,}` 🪙",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💍 В меню семьи", callback_data=f"menu_marry_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.callback_query(F.data.startswith("family_withdraw_prompt_"))
async def family_withdraw_prompt(callback: types.CallbackQuery, state: FSMContext):
    owner_id = callback.data.split("_")[3]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    fam = await get_family(uid)
    if not fam:
        await callback.answer("❌ Вы не в браке!", show_alert=True)
        return
    await state.set_state(FamilyState.waiting_for_withdraw_amount)
    await callback.message.edit_text(
        f"💸 **СНЯТИЕ С БЮДЖЕТА**\n\nСемейный бюджет: `{fam.get('budget', 0):,}` 🪙\nВведите сумму для снятия:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в семью", callback_data=f"menu_marry_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(FamilyState.waiting_for_withdraw_amount)
async def process_withdraw_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount <= 0: raise ValueError()
    except ValueError:
        await message.answer("❌ Введите корректную сумму числом:")
        return
        
    uid = str(message.from_user.id)
    fam = await get_family(uid)
    if not fam or fam.get("budget", 0) < amount:
        await message.answer("❌ В семейном бюджете недостаточно средств!")
        return
        
    p = await get_profile(message.from_user)
    new_coins = p.get("coins", 0) + amount
    new_budget = fam.get("budget", 0) - amount
    
    def _save_wd():
        supabase.table("users").update({"coins": new_coins}).eq("user_id", uid).execute()
        supabase.table("families").update({"budget": new_budget}).eq("family_id", fam["family_id"]).execute()
    await asyncio.to_thread(_save_wd)
    await state.clear()
    
    await message.answer(
        f"✅ Вы сняли `{amount:,}` 🪙 из семейного бюджета в свой кошелек!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💍 В меню семьи", callback_data=f"menu_marry_{uid}")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.callback_query(F.data.startswith("family_shop_menu_"))
async def family_shop_menu(callback: types.CallbackQuery):
    owner_id = callback.data.split("_")[3]
    if str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    fam = await get_family(uid)
    if not fam:
        await callback.answer("❌ Семья не найдена!", show_alert=True)
        return
    text = (
        f"🛒 **СЕМЕЙНЫЙ МАГАЗИН ИМУЩЕСТВА**\n"
        f"💰 Бюджет семьи: `{fam.get('budget', 0):,}` 🪙\n\n"
        f"Покупайте имущество в общую собственность (отсортировано по возрастанию цены):"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏡 Коттедж (800k)", callback_data=f"fam_buy_house_cottage_{uid}")],
        [InlineKeyboardButton(text="🏢 Пентхаус (1.2M)", callback_data=f"fam_buy_apt_penthouse_{uid}")],
        [InlineKeyboardButton(text="🏡 Дом Хай-тек (1.4M)", callback_data=f"fam_buy_house_modern_{uid}")],
        [InlineKeyboardButton(text="🏡 Вилла (2M)", callback_data=f"fam_buy_house_villa_{uid}")],
        [InlineKeyboardButton(text="🏢 Двухуровневые (2.5M)", callback_data=f"fam_buy_apt_duplex_{uid}")],
        [InlineKeyboardButton(text="🏰 Поместье (5M)", callback_data=f"fam_buy_house_estate_{uid}")],
        [InlineKeyboardButton(text="🏎 Supercar (6M)", callback_data=f"fam_buy_car_chiron_{uid}")],
        [InlineKeyboardButton(text="🏰 Замок (7.5M)", callback_data=f"fam_buy_house_castle_{uid}")],
        [InlineKeyboardButton(text="👑 Особняк (10M)", callback_data=f"fam_buy_house_palace_{uid}")],
        [InlineKeyboardButton(text="🏎 Koenigsegg (14M)", callback_data=f"fam_buy_car_koenigsegg_{uid}")],
        [InlineKeyboardButton(text="🍖 Еда для семьи (+50 еды = 50k)", callback_data=f"fam_buy_food_none_{uid}")],
        [InlineKeyboardButton(text="🔙 В меню семьи", callback_data=f"menu_marry_{uid}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("fam_buy_"))
async def fam_buy_item(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    action = parts[2] 
    key = parts[3]
    owner_id = parts[4] if len(parts) > 4 else None

    if owner_id and str(callback.from_user.id) != owner_id:
        await callback.answer("❌ Это не ваше меню!", show_alert=True)
        return

    uid = str(callback.from_user.id)
    fam = await get_family(uid)
    if not fam:
        await callback.answer("❌ Семья не найдена!", show_alert=True)
        return
    
    budget = fam.get("budget", 0)
    cost = 0
    col = ""
    val = ""
    
    if action == "house":
        item = FAMILY_HOUSES.get(key)
        if not item: return
        cost = item["price"]
        col = "house"
        val = item["name"]
    elif action == "apt":
        item = FAMILY_APTS.get(key)
        if not item: return
        cost = item["price"]
        col = "apartment"
        val = item["name"]
    elif action == "car":
        item = FAMILY_CARS.get(key)
        if not item: return
        cost = item["price"]
        col = "car"
        val = item["name"]
    elif action == "food":
        cost = 50000
        col = "food"
        val = fam.get("food", 100) + 50
        
    if budget < cost:
        await callback.answer(f"❌ В семейном бюджете недостаточно средств! Нужно {cost:,} 🪙", show_alert=True)
        return
        
    new_budget = budget - cost
    def _buy():
        if action == "food":
            supabase.table("families").update({"budget": new_budget, "food": val}).eq("family_id", fam["family_id"]).execute()
        else:
            supabase.table("families").update({"budget": new_budget, col: val}).eq("family_id", fam["family_id"]).execute()
    await asyncio.to_thread(_buy)
    
    await callback.answer(f"🎉 Успешно приобретено для семьи!", show_alert=True)
    callback.data = f"family_shop_menu_{uid}"
    await family_shop_menu(callback)

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
        "1. `/setpartner` — назначить/снять партнера.\n"
        "2. `/give <сумма>` — выдать монеты.\n"
        "3. `/setcoins <сумма>` — точный баланс.\n"
        "4. `/givecar <ключ>` — выдать авто (например, `m5f90`).\n"
        "5. `/reply <user_id> <текст>` — ответить в техподдержку.\n"
        "6. `/admin` — открыть это меню.\n\n"
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
            "is_active": is_first,
            "fuel_liters": float(car_info["tank"]),
            "max_fuel_liters": car_info["tank"],
            "fuel_type": 92
        }).execute()
    
    try:
        await asyncio.to_thread(_insert_car)
        await message.answer(f"✅ Игроку **{target_name}** успешно выдана машина: **{car_info['name']}** с полным баком!", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error giving car: {e}")
        await message.answer("❌ Ошибка при выдаче машины в базу данных.")

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    commands = [
        BotCommand(command="start", description="Запустить бота / Главное меню"),
        BotCommand(command="marry", description="Сделать предложение о браке")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    
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
