"""Telegram-бот магазина одежды: каталог с фото и размерами, кнопка «Купить», заявки владельцу и скрытая админ-панель."""
import asyncio
import html
import logging
import os
import re
import time

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (BotCommand, BotCommandScopeChat, CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup)

from db import DB, sizes_of


def load_env(path: str = ".env"):
    """Читает .env рядом с ботом (без сторонних библиотек)."""
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env()
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x.isdigit()}
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
SHOP_NAME = os.getenv("SHOP_NAME", "Мой магазин")
CONTACT = os.getenv("CONTACT", "")
CURRENCY = os.getenv("CURRENCY", "₽")
BANNER = os.path.join("assets", "banner.png")
MAX_ATTEMPTS, LOCK_SECONDS = 5, 15 * 60

db = DB(os.getenv("DB_PATH", "shop.db"))
router = Router()
attempts: dict[int, list[float]] = {}

BTN_CATALOG = "🛍 Каталог"
BTN_CONTACT = "💬 Связаться с продавцом"
BTN_ADMIN = "🛠 Админ-панель"
BUTTONS = {BTN_CATALOG, BTN_CONTACT, BTN_ADMIN}


class A(StatesGroup):
    password = State()
    new_category = State()
    new_brand = State()
    name = State()
    price = State()
    sizes = State()
    color = State()
    stock = State()
    photo = State()
    description = State()
    edit = State()         # ввод нового значения поля товара
    rename = State()       # переименование категории / подкатегории
    broadcast = State()


# ================= помощники =================
def b(text, data=None, url=None):
    return InlineKeyboardButton(text=text, callback_data=data, url=url)


def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[list(r) for r in rows if r])


def grid(buttons, cols=2):
    return [buttons[i:i + cols] for i in range(0, len(buttons), cols)]


def esc(s) -> str:
    return html.escape(str(s or ""))


def money(v) -> str:
    return f"{v:,}".replace(",", " ") + f" {CURRENCY}"


def is_owner(uid: int) -> bool:
    """ID в списке админов — видит кнопку панели."""
    return uid in ADMIN_IDS


def is_admin(uid: int) -> bool:
    """ID в списке и пароль введён."""
    return uid in ADMIN_IDS and db.has_session(uid)


def main_kb(uid: int) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=BTN_CATALOG)], [KeyboardButton(text=BTN_CONTACT)]]
    if is_owner(uid):  # остальные кнопку не видят
        rows.append([KeyboardButton(text=BTN_ADMIN)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def card_text(p) -> str:
    sizes = sizes_of(p)
    lines = [f"<b>{esc(p['name'])}</b>", f"📂 {esc(p['category'])} · {esc(p['brand'])}", "",
             f"💰 Цена: <b>{money(p['price'])}</b>",
             "✅ В наличии" if p["in_stock"] else "❌ Нет в наличии"]
    if p["color"]:
        lines.append(f"🎨 Цвет: {esc(p['color'])}")
    if p["in_stock"] and sizes:
        lines.append("📏 Размеры в наличии: " + ", ".join(esc(c) for c in sizes))
    if p["description"]:
        lines += ["", esc(p["description"])]
    return "\n".join(lines)


async def replace(cb: CallbackQuery, text: str, markup=None, photo=None):
    """Показывает новый экран вместо старого (фото и текст нельзя менять друг на друга — пересоздаём)."""
    msg = cb.message
    if photo is None and msg.text is not None:
        await msg.edit_text(text, reply_markup=markup)
        return
    try:
        await msg.delete()
    except Exception:
        pass
    if photo:
        await msg.answer_photo(photo, caption=text, reply_markup=markup)
    else:
        await msg.answer(text, reply_markup=markup)


def parse_price(text: str) -> int | None:
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits and len(digits) <= 9 else None


def parse_sizes(text: str) -> list[str]:
    """«xs, s, m» или «42 44 46» → ['XS', 'S', 'M']. «-» — без размеров (например, сумка)."""
    text = text.strip()
    if text in {"-", "—", "нет", "Нет"}:
        return []
    parts = re.split(r"[,;\n/]", text) if re.search(r"[,;\n/]", text) else text.split()
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # буквенные размеры — заглавными (xs → XS), остальное как написано (One size, 42-44)
        out.append(part.upper() if re.fullmatch(r"[a-zA-Z]{1,4}", part) else part)
    return list(dict.fromkeys(out))[:20]


def parse_text_or_dash(text: str, limit: int) -> str:
    text = text.strip()
    return "" if text in {"-", "—"} else text[:limit]


def user_link(uid, username, first_name) -> str:
    if username:
        return f"@{esc(username)}"
    return f'<a href="tg://user?id={uid}">{esc(first_name or "покупатель")}</a> (без юзернейма)'


async def notify_admins(bot: Bot, text: str, markup=None):
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid, text, reply_markup=markup)
        except Exception:
            logging.warning("Не удалось отправить сообщение админу %s (он ещё не запускал бота?)", aid)


# ================= старт и проверка возраста =================
@router.message.middleware()
async def remember_user(handler, event: Message, data):
    if event.from_user:
        db.touch_user(event.from_user.id, event.from_user.username, event.from_user.first_name)
    return await handler(event, data)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await welcome(message, message.from_user.id)


async def welcome(message: Message, uid: int):
    text = (f"👋 Добро пожаловать в <b>{esc(SHOP_NAME)}</b>!\n\n"
            "Открывай «🛍 Каталог», выбирай вещь и свой размер, жми «Купить» — продавец свяжется с тобой.")
    if os.path.exists(BANNER):
        await message.answer_photo(FSInputFile(BANNER), caption=text, reply_markup=main_kb(uid))
    else:
        await message.answer(text, reply_markup=main_kb(uid))


@router.message(F.text == BTN_CONTACT)
async def contact(message: Message):
    if CONTACT:
        await message.answer(f"💬 Пиши продавцу: {esc(CONTACT)}")
    else:
        await message.answer("💬 Выбери товар в каталоге и нажми «Купить» — продавец сам тебе напишет.")


# ================= каталог для покупателей =================
def categories_kb(prefix: str):
    cats = db.categories()
    rows = grid([b(f"{c['name']} ({c['n']})", f"{prefix}c:{c['id']}") for c in cats])
    return cats, rows


@router.message(F.text == BTN_CATALOG)
@router.message(Command("catalog"))
async def catalog(message: Message, state: FSMContext):
    await state.clear()
    cats, rows = categories_kb("")
    if not cats:
        hint = "\n\nДобавь товары через «🛠 Админ-панель» → «➕ Добавить товар»." if is_owner(message.from_user.id) else ""
        await message.answer("🛍 Каталог пока пуст. Загляни чуть позже!" + hint)
        return
    await message.answer("🛍 <b>Каталог</b>\nВыбери категорию:", reply_markup=kb(*rows))


@router.callback_query(F.data == "cat")
async def cb_catalog(cb: CallbackQuery):
    cats, rows = categories_kb("")
    await replace(cb, "🛍 <b>Каталог</b>\nВыбери категорию:" if cats else "🛍 Каталог пока пуст.", kb(*rows))
    await cb.answer()


@router.callback_query(F.data.startswith("c:"))
async def cb_category(cb: CallbackQuery):
    cid = int(cb.data[2:])
    cat = db.category(cid)
    if not cat:
        await cb.answer("Раздел больше не существует", show_alert=True)
        return
    rows = grid([b(f"{br['name']} ({br['n']})", f"b:{br['id']}") for br in db.brands(cid)])
    await replace(cb, f"📂 <b>{esc(cat['name'])}</b>\nВыбери раздел:", kb(*rows, [b("← Каталог", "cat")]))
    await cb.answer()


@router.callback_query(F.data.startswith("b:"))
async def cb_brand(cb: CallbackQuery):
    br = db.brand(int(cb.data[2:]))
    if not br:
        await cb.answer("Раздел больше не существует", show_alert=True)
        return
    rows = [[b(f"{'✅' if p['in_stock'] else '❌'} {p['name']} — {money(p['price'])}", f"p:{p['id']}")]
            for p in db.products(br["id"])]
    await replace(cb, f"📂 {esc(br['category'])} → <b>{esc(br['name'])}</b>\nВыбери вещь:",
                  kb(*rows, [b("← Назад", f"c:{br['category_id']}")]))
    await cb.answer()


def product_kb(p, uid: int) -> InlineKeyboardMarkup:
    rows = []
    if p["in_stock"]:
        sizes = sizes_of(p)
        if sizes:
            rows += grid([b(f"🛒 Купить — {c}", f"buy:{p['id']}:{i}") for i, c in enumerate(sizes)], 2 if len(sizes) > 3 else 1)
        else:
            rows.append([b("🛒 Купить", f"buy:{p['id']}:-1")])
    if is_admin(uid):
        rows.append([b("✏️ Редактировать (админ)", f"ap:{p['id']}")])
    rows.append([b("← Назад", f"b:{p['brand_id']}")])
    return kb(*rows)


@router.callback_query(F.data.startswith("p:"))
async def cb_product(cb: CallbackQuery):
    p = db.product(int(cb.data[2:]))
    if not p:
        await cb.answer("Товар больше не продаётся", show_alert=True)
        return
    await replace(cb, card_text(p), product_kb(p, cb.from_user.id), photo=p["photo"] or None)
    await cb.answer()


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(cb: CallbackQuery):
    _, pid, idx = cb.data.split(":")
    p = db.product(int(pid))
    if not p or not p["in_stock"]:
        await cb.answer("Увы, этого товара уже нет в наличии 😔", show_alert=True)
        return
    sizes = sizes_of(p)
    size = sizes[int(idx)] if 0 <= int(idx) < len(sizes) else None
    u = cb.from_user
    oid = db.add_order(u.id, u.username, u.first_name, p, size)
    item = f"{esc(p['name'])}" + (f", размер {esc(size)}" if size else "")
    await cb.message.answer(
        f"✅ <b>Заявка №{oid} принята!</b>\n\n{item} — {money(p['price'])}\n\n"
        "⏳ Ждите, скоро продавец вам ответит."
        + ("" if u.username else "\n\n⚠️ У тебя нет юзернейма в Telegram. Чтобы продавец смог написать, "
                                 "добавь его в настройках Telegram или напиши продавцу сам.")
    )
    write = b("💬 Написать покупателю", url=f"https://t.me/{u.username}") if u.username else None
    await notify_admins(
        cb.bot,
        f"🛒 <b>Новая заявка №{oid}</b>\n\n"
        f"👤 Покупатель: {user_link(u.id, u.username, u.first_name)}\n"
        f"🆔 ID: <code>{u.id}</code>\n"
        f"📦 Товар: {esc(p['category'])} → {esc(p['brand'])} → <b>{esc(p['name'])}</b>\n"
        + (f"📏 Размер: <b>{esc(size)}</b>\n" if size else "")
        + (f"🎨 Цвет: {esc(p['color'])}\n" if p["color"] else "")
        + f"💰 Цена: {money(p['price'])}",
        kb([write] if write else None, [b("✅ Отметить обработанной", f"od:{oid}")]),
    )
    await cb.answer("Заявка отправлена!")


# ================= вход в админ-панель =================
@router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
@router.message(F.text == BTN_ADMIN, F.from_user.id.in_(ADMIN_IDS))
async def admin_entry(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    if db.has_session(uid):
        await show_admin_menu(message)
        return
    recent = [t for t in attempts.get(uid, []) if time.time() - t < LOCK_SECONDS]
    attempts[uid] = recent
    if len(recent) >= MAX_ATTEMPTS:
        await message.answer("⛔ Слишком много неверных попыток. Попробуй через 15 минут.")
        return
    await state.set_state(A.password)
    await message.answer("🔒 Введи пароль админ-панели:")


@router.message(A.password, F.text)
async def admin_password(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    try:
        await message.delete()  # не оставляем пароль в переписке
    except Exception:
        pass
    if not ADMIN_PASSWORD or message.text.strip() != ADMIN_PASSWORD:
        attempts.setdefault(uid, []).append(time.time())
        await message.answer("⛔ Неверный пароль.")
        return
    attempts.pop(uid, None)
    db.open_session(uid)
    await message.answer("✅ Вход выполнен.")
    await show_admin_menu(message)


def admin_menu_kb():
    return kb([b("➕ Добавить товар", "a:add")],
              [b("📦 Товары и цены", "a:prods"), b("🗂 Разделы", "a:sections")],
              [b("📋 Заявки", "a:orders"), b("📊 Статистика", "a:stats")],
              [b("📣 Рассылка", "a:bcast")],
              [b("🚪 Выйти", "a:logout")])


async def show_admin_menu(message: Message):
    await message.answer("🛠 <b>Админ-панель</b>", reply_markup=admin_menu_kb())


def cancel_kb():
    return kb([b("✖️ Отмена", "a:menu")])


async def admin_guard(cb: CallbackQuery) -> bool:
    """True, если доступа нет (и сообщает об этом)."""
    if is_admin(cb.from_user.id):
        return False
    await cb.answer("⛔ Нет доступа", show_alert=True)
    return True


@router.callback_query(F.data.startswith("a:"))
async def admin_menu(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    action = cb.data[2:]
    await state.clear()
    if action == "menu":
        await replace(cb, "🛠 <b>Админ-панель</b>", admin_menu_kb())
    elif action == "add":
        await state.update_data(mode="add")
        await ask_category(cb)
    elif action == "prods":
        cats, rows = categories_kb("a")
        await replace(cb, "📦 <b>Товары</b>\nВыбери категорию:" if cats else "Товаров пока нет. Нажми «➕ Добавить товар».",
                      kb(*rows, [b("← Меню", "a:menu")]))
    elif action == "sections":
        rows = []
        for c in db.categories():
            rows.append([b(f"📂 {c['name']}", f"rn:c:{c['id']}")])
            rows += [[b(f"    🏷 {br['name']}", f"rn:b:{br['id']}")] for br in db.brands(c["id"])]
        await replace(cb, "🗂 <b>Разделы</b>\nНажми на категорию или подкатегорию, чтобы переименовать.\n"
                          "Пустые разделы удаляются сами.", kb(*rows, [b("← Меню", "a:menu")]))
    elif action == "orders":
        orders = db.recent_orders()
        lines = [f"{'✅' if o['done'] else '🆕'} №{o['id']} · {user_link(o['user_id'], o['username'], o['first_name'])} · "
                 f"{esc(o['product'].split(' → ')[-1])}{', ' + esc(o['size']) if o['size'] else ''} · {money(o['price'])}"
                 for o in orders]
        await replace(cb, "📋 <b>Последние заявки</b>\n\n" + ("\n".join(lines) if lines else "Заявок пока нет."),
                      kb([b("← Меню", "a:menu")]))
    elif action == "stats":
        s = db.stats()
        await replace(cb, "📊 <b>Статистика</b>\n\n"
                          f"👥 Покупателей: {s['users']}\n📦 Товаров: {s['products']} (в наличии {s['in_stock']})\n"
                          f"🛒 Заявок: {s['orders']} · сегодня {s['orders_today']} · не обработано {s['orders_open']}",
                      kb([b("← Меню", "a:menu")]))
    elif action == "bcast":
        await state.set_state(A.broadcast)
        await replace(cb, "📣 Пришли сообщение для рассылки всем покупателям: текст или фото с подписью.\n"
                          "Например: «🔥 Новая коллекция уже в каталоге!»", cancel_kb())
    elif action == "logout":
        db.close_session(cb.from_user.id)
        await replace(cb, "🚪 Ты вышел из админ-панели. Для входа снова понадобится пароль.")
    await cb.answer()


# ---------- выбор / создание категории и подкатегории (для добавления и переноса товара) ----------
async def ask_category(cb_or_msg):
    rows = grid([b(c["name"], f"wc:{c['id']}") for c in db.categories()])
    text = "📂 <b>Шаг 1/8.</b> Выбери категорию или создай новую (например «Худи», «Футболки», «Брюки», «Аксессуары»):"
    markup = kb(*rows, [b("➕ Новая категория", "wc:new")], [b("✖️ Отмена", "a:menu")])
    if isinstance(cb_or_msg, CallbackQuery):
        await replace(cb_or_msg, text, markup)
    else:
        await cb_or_msg.answer(text, reply_markup=markup)


async def ask_brand(target, cid: int):
    rows = grid([b(br["name"], f"wb:{br['id']}") for br in db.brands(cid)])
    text = "🏷 <b>Шаг 2/8.</b> Выбери подкатегорию или создай новую (например «Мужское», «Женское», «Новая коллекция»):"
    markup = kb(*rows, [b("➕ Новая подкатегория", "wb:new")], [b("✖️ Отмена", "a:menu")])
    if isinstance(target, CallbackQuery):
        await replace(target, text, markup)
    else:
        await target.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("wc:"))
async def wizard_category(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    value = cb.data[3:]
    if value == "new":
        await state.set_state(A.new_category)
        await replace(cb, "✍️ Напиши название новой категории:", cancel_kb())
    else:
        await state.update_data(cid=int(value))
        await ask_brand(cb, int(value))
    await cb.answer()


@router.message(A.new_category, F.text, ~F.text.in_(BUTTONS))
async def wizard_new_category(message: Message, state: FSMContext):
    cid = db.add_category(message.text.strip()[:40])
    await state.update_data(cid=cid)
    await ask_brand(message, cid)


@router.callback_query(F.data.startswith("wb:"))
async def wizard_brand(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    value = cb.data[3:]
    if value == "new":
        await state.set_state(A.new_brand)
        await replace(cb, "✍️ Напиши название подкатегории:", cancel_kb())
    else:
        await brand_chosen(cb.message, state, int(value), from_cb=cb)
    await cb.answer()


@router.message(A.new_brand, F.text, ~F.text.in_(BUTTONS))
async def wizard_new_brand(message: Message, state: FSMContext):
    data = await state.get_data()
    if "cid" not in data:
        await state.clear()
        await message.answer("Что-то пошло не так, начни заново.", reply_markup=admin_menu_kb())
        return
    bid = db.add_brand(data["cid"], message.text.strip()[:40])
    await brand_chosen(message, state, bid)


async def brand_chosen(message: Message, state: FSMContext, bid: int, from_cb: CallbackQuery | None = None):
    data = await state.get_data()
    if data.get("mode") == "move":  # перенос существующего товара
        db.update_product(data["pid"], brand_id=bid)
        await state.clear()
        await send_edit_menu(message, data["pid"], "✅ Товар перенесён.")
        if from_cb:
            await from_cb.message.delete()
        return
    await state.update_data(bid=bid)
    await state.set_state(A.name)
    text = "✍️ <b>Шаг 3/8.</b> Напиши название вещи (например «Худи оверсайз»):"
    if from_cb:
        await replace(from_cb, text, cancel_kb())
    else:
        await message.answer(text, reply_markup=cancel_kb())


# ---------- остальные шаги добавления товара ----------
@router.message(A.name, F.text, ~F.text.in_(BUTTONS))
async def wizard_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip()[:60])
    await state.set_state(A.price)
    await message.answer(f"💰 <b>Шаг 4/8.</b> Цена в {CURRENCY}, только число (например 2490):", reply_markup=cancel_kb())


@router.message(A.price, F.text, ~F.text.in_(BUTTONS))
async def wizard_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Нужно число, например 2490. Попробуй ещё раз:")
        return
    await state.update_data(price=price)
    await state.set_state(A.sizes)
    await message.answer("📏 <b>Шаг 5/8.</b> Размеры в наличии через запятую, например «XS, S, M, L» или «42, 44, 46».\n"
                         "Если размера нет (сумка, кепка one size) — отправь «-».", reply_markup=cancel_kb())


@router.message(A.sizes, F.text, ~F.text.in_(BUTTONS))
async def wizard_sizes(message: Message, state: FSMContext):
    await state.update_data(sizes=parse_sizes(message.text))
    await state.set_state(A.color)
    await message.answer("🎨 <b>Шаг 6/8.</b> Цвет вещи (например «Чёрный» или «Графит»). Если не нужно — отправь «-».",
                         reply_markup=cancel_kb())


@router.message(A.color, F.text, ~F.text.in_(BUTTONS))
async def wizard_color(message: Message, state: FSMContext):
    await state.update_data(color=parse_text_or_dash(message.text, 40))
    await state.set_state(A.stock)
    await message.answer("📦 <b>Шаг 7/8.</b> Вещь есть в наличии?",
                         reply_markup=kb([b("✅ Есть в наличии", "ws:1"), b("❌ Нет в наличии", "ws:0")],
                                         [b("✖️ Отмена", "a:menu")]))


@router.callback_query(A.stock, F.data.startswith("ws:"))
async def wizard_stock(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    await state.update_data(in_stock=cb.data == "ws:1")
    await state.set_state(A.photo)
    await replace(cb, "🖼 <b>Шаг 8/8.</b> Пришли фото вещи (как обычную картинку, не файлом).",
                  kb([b("Пропустить без фото", "wp:skip")], [b("✖️ Отмена", "a:menu")]))
    await cb.answer()


@router.message(A.photo, F.photo)
async def wizard_photo(message: Message, state: FSMContext):
    await finish_product(message, state, message.photo[-1].file_id)


@router.callback_query(A.photo, F.data == "wp:skip")
async def wizard_photo_skip(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    await cb.message.delete()
    await finish_product(cb.message, state, None)
    await cb.answer()


@router.message(A.photo)
async def wizard_photo_wrong(message: Message):
    await message.answer("Нужна именно картинка. Отправь фото (не файлом) или нажми «Пропустить без фото».")


async def finish_product(message: Message, state: FSMContext, photo):
    d = await state.get_data()
    await state.clear()
    pid = db.add_product(d["bid"], d["name"], d["price"], d["sizes"], d.get("color", ""), d["in_stock"], photo, "")
    await send_edit_menu(message, pid, "✅ <b>Товар добавлен!</b> Так его видят покупатели:")


# ---------- просмотр и редактирование товаров ----------
@router.callback_query(F.data.startswith("ac:"))
async def admin_category(cb: CallbackQuery):
    if await admin_guard(cb):
        return
    cid = int(cb.data[3:])
    cat = db.category(cid)
    if not cat:
        await cb.answer("Раздела больше нет", show_alert=True)
        return
    rows = grid([b(f"{br['name']} ({br['n']})", f"ab:{br['id']}") for br in db.brands(cid)])
    await replace(cb, f"📦 <b>{esc(cat['name'])}</b>\nВыбери подкатегорию:", kb(*rows, [b("← Назад", "a:prods")]))
    await cb.answer()


@router.callback_query(F.data.startswith("ab:"))
async def admin_brand(cb: CallbackQuery):
    if await admin_guard(cb):
        return
    br = db.brand(int(cb.data[3:]))
    if not br:
        await cb.answer("Раздела больше нет", show_alert=True)
        return
    rows = [[b(f"{'✅' if p['in_stock'] else '❌'} {p['name']} — {money(p['price'])}", f"ap:{p['id']}")]
            for p in db.products(br["id"])]
    await replace(cb, f"📦 {esc(br['category'])} → <b>{esc(br['name'])}</b>\nВыбери товар:",
                  kb(*rows, [b("← Назад", f"ac:{br['category_id']}")]))
    await cb.answer()


def edit_kb(p) -> InlineKeyboardMarkup:
    pid = p["id"]
    return kb([b("❌ Сделать «нет в наличии»" if p["in_stock"] else "✅ Сделать «в наличии»", f"at:{pid}")],
              [b("💰 Цена", f"ae:{pid}:price"), b("📏 Размеры", f"ae:{pid}:sizes")],
              [b("🎨 Цвет", f"ae:{pid}:color"), b("📝 Описание", f"ae:{pid}:description")],
              [b("🖼 Фото", f"ae:{pid}:photo"), b("✏️ Название", f"ae:{pid}:name")],
              [b("📂 Перенести", f"am:{pid}"), b("🗑 Удалить", f"ad:{pid}")],
              [b("← К разделу", f"ab:{p['brand_id']}"), b("🛠 Меню", "a:menu")])


async def send_edit_menu(message: Message, pid: int, title: str = "✏️ <b>Редактирование</b>"):
    p = db.product(pid)
    if not p:
        await message.answer("Товар не найден.", reply_markup=admin_menu_kb())
        return
    text = f"{title}\n\n{card_text(p)}"
    if p["photo"]:
        await message.answer_photo(p["photo"], caption=text, reply_markup=edit_kb(p))
    else:
        await message.answer(text + "\n\n🖼 <i>Фото не добавлено</i>", reply_markup=edit_kb(p))


@router.callback_query(F.data.startswith("ap:"))
async def admin_product(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    await state.clear()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await send_edit_menu(cb.message, int(cb.data[3:]))
    await cb.answer()


@router.callback_query(F.data.startswith("at:"))
async def admin_toggle_stock(cb: CallbackQuery):
    if await admin_guard(cb):
        return
    pid = int(cb.data[3:])
    p = db.product(pid)
    if not p:
        await cb.answer("Товар не найден", show_alert=True)
        return
    db.update_product(pid, in_stock=0 if p["in_stock"] else 1)
    await cb.message.delete()
    await send_edit_menu(cb.message, pid, "✅ Наличие обновлено.")
    await cb.answer()


EDIT_PROMPTS = {
    "price": f"💰 Напиши новую цену в {CURRENCY} (только число):",
    "sizes": "📏 Напиши размеры в наличии через запятую (например «S, M, L»), или «-», если размера нет:",
    "color": "🎨 Напиши цвет вещи, или «-», чтобы убрать:",
    "photo": "🖼 Пришли новое фото товара (картинкой, не файлом):",
    "name": "✏️ Напиши новое название:",
    "description": "📝 Напиши описание (состав, посадка, уход…), или «-», чтобы убрать:",
}


@router.callback_query(F.data.startswith("ae:"))
async def admin_edit_field(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    _, pid, field = cb.data.split(":")
    if field not in EDIT_PROMPTS:
        await cb.answer()
        return
    await state.set_state(A.edit)
    await state.update_data(pid=int(pid), field=field)
    await cb.message.answer(EDIT_PROMPTS[field], reply_markup=kb([b("✖️ Отмена", f"ap:{pid}")]))
    await cb.answer()


@router.message(A.edit)
async def admin_edit_value(message: Message, state: FSMContext):
    d = await state.get_data()
    pid, field = d["pid"], d["field"]
    if message.text in BUTTONS:
        await state.clear()
        return
    if field == "photo":
        if not message.photo:
            await message.answer("Нужна картинка. Пришли фото (не файлом):")
            return
        db.update_product(pid, photo=message.photo[-1].file_id)
    elif not message.text:
        await message.answer("Напиши текстом:")
        return
    elif field == "price":
        price = parse_price(message.text)
        if price is None:
            await message.answer("Нужно число, например 2490:")
            return
        db.update_product(pid, price=price)
    elif field == "sizes":
        db.update_product(pid, sizes=parse_sizes(message.text))
    elif field == "color":
        db.update_product(pid, color=parse_text_or_dash(message.text, 40))
    elif field == "name":
        db.update_product(pid, name=message.text.strip()[:60])
    elif field == "description":
        text = message.text.strip()
        db.update_product(pid, description="" if text in {"-", "—"} else text[:700])
    await state.clear()
    await send_edit_menu(message, pid, "✅ Сохранено.")


@router.callback_query(F.data.startswith("am:"))
async def admin_move(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    await state.clear()
    await state.update_data(mode="move", pid=int(cb.data[3:]))
    await cb.message.delete()
    await ask_category(cb.message)
    await cb.answer()


@router.callback_query(F.data.startswith("ad:"))
async def admin_delete_ask(cb: CallbackQuery):
    if await admin_guard(cb):
        return
    pid = int(cb.data[3:])
    p = db.product(pid)
    if not p:
        await cb.answer("Уже удалён", show_alert=True)
        return
    await cb.message.answer(f"🗑 Удалить «{esc(p['name'])}» насовсем?",
                            reply_markup=kb([b("Да, удалить", f"ay:{pid}"), b("Нет", f"ap:{pid}")]))
    await cb.answer()


@router.callback_query(F.data.startswith("ay:"))
async def admin_delete(cb: CallbackQuery):
    if await admin_guard(cb):
        return
    db.delete_product(int(cb.data[3:]))
    await replace(cb, "🗑 Товар удалён.", admin_menu_kb())
    await cb.answer()


# ---------- переименование разделов ----------
@router.callback_query(F.data.startswith("rn:"))
async def admin_rename_ask(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    _, kind, rid = cb.data.split(":")
    await state.set_state(A.rename)
    await state.update_data(kind=kind, rid=int(rid))
    await cb.message.answer("✍️ Напиши новое название:", reply_markup=cancel_kb())
    await cb.answer()


@router.message(A.rename, F.text, ~F.text.in_(BUTTONS))
async def admin_rename(message: Message, state: FSMContext):
    d = await state.get_data()
    await state.clear()
    name = message.text.strip()[:40]
    try:
        (db.rename_category if d["kind"] == "c" else db.rename_brand)(d["rid"], name)
        await message.answer("✅ Переименовано.", reply_markup=admin_menu_kb())
    except Exception:
        await message.answer("Такое название уже есть.", reply_markup=admin_menu_kb())


# ---------- заявки и рассылка ----------
@router.callback_query(F.data.startswith("od:"))
async def order_done(cb: CallbackQuery):
    if await admin_guard(cb):
        return
    oid = int(cb.data[3:])
    db.set_order_done(oid)
    await cb.message.edit_text(cb.message.html_text + f"\n\n✅ <b>Обработана</b> ({esc(cb.from_user.first_name)})")
    await cb.answer("Готово")


@router.message(A.broadcast, ~F.text.in_(BUTTONS))
async def broadcast_preview(message: Message, state: FSMContext):
    if not (message.text or message.photo):
        await message.answer("Пришли текст или фото с подписью.")
        return
    await state.update_data(chat=message.chat.id, msg=message.message_id)
    n = len(db.user_ids())
    await message.answer(f"Отправить это сообщение {n} покупателям?",
                         reply_markup=kb([b(f"📣 Отправить ({n})", "bc:go")], [b("✖️ Отмена", "a:menu")]))


@router.callback_query(A.broadcast, F.data == "bc:go")
async def broadcast_send(cb: CallbackQuery, state: FSMContext):
    if await admin_guard(cb):
        return
    d = await state.get_data()
    await state.clear()
    await cb.message.edit_text("📣 Отправляю…")
    ok = 0
    for uid in db.user_ids():
        try:
            await cb.bot.copy_message(uid, d["chat"], d["msg"])
            ok += 1
        except Exception:
            pass  # пользователь заблокировал бота
        await asyncio.sleep(0.05)  # не превышаем лимиты Telegram
    await cb.message.answer(f"✅ Рассылка завершена: доставлено {ok}.", reply_markup=admin_menu_kb())
    await cb.answer()


# ================= всё остальное =================
@router.message()
async def other(message: Message, state: FSMContext):
    await message.answer("Не понял 🤔 Нажми «🛍 Каталог», чтобы выбрать товар.", reply_markup=main_kb(message.from_user.id))


# ================= запуск =================
async def main():
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("❌ Не найден BOT_TOKEN. Запусти start.bat / start.sh — мастер настройки спросит токен.")
    if not ADMIN_IDS or not ADMIN_PASSWORD:
        logging.warning("ADMIN_IDS или ADMIN_PASSWORD не заданы — в админ-панель никто не сможет войти.")
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await bot.set_my_commands([BotCommand(command="start", description="Главное меню"),
                                   BotCommand(command="catalog", description="Каталог")])
        for aid in ADMIN_IDS:  # команда /admin в меню видна только админам
            try:
                await bot.set_my_commands([BotCommand(command="start", description="Главное меню"),
                                           BotCommand(command="catalog", description="Каталог"),
                                           BotCommand(command="admin", description="Админ-панель")],
                                          scope=BotCommandScopeChat(chat_id=aid))
            except Exception:
                pass  # админ ещё не запускал бота
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run():
    from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
    from aiogram.utils.token import TokenValidationError
    try:
        asyncio.run(main())
    except (TokenValidationError, TelegramUnauthorizedError):
        raise SystemExit("❌ Telegram не принял токен. Проверь BOT_TOKEN в файле .env.")
    except TelegramNetworkError:
        raise SystemExit("❌ Нет связи с Telegram. Проверь интернет (в России может понадобиться VPN).")
    except KeyboardInterrupt:
        print("Бот остановлен.")


if __name__ == "__main__":
    run()
