"""Telegram-бот: AI-сравнение телефонов по подписке с кодами активации и админ-панелью."""
import asyncio
import html
import logging
import os
import time
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, Message, ReplyKeyboardMarkup)

from ai import PhoneAI
from db import DB, FOREVER


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
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x}
OWNER_CONTACT = os.getenv("OWNER_CONTACT", "@your_username")
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "50"))
MAX_ATTEMPTS, LOCK_SECONDS = 5, 15 * 60  # защита от подбора пароля админки
HISTORY_TURNS = 6                          # сколько последних сообщений помнит AI

db = DB(os.getenv("DB_PATH", "phonebot.db"))
ai = PhoneAI()
router = Router()

history: dict[int, list[dict]] = {}       # память диалога по пользователю
busy: set[int] = set()                     # у кого AI сейчас отвечает
attempts: dict[int, list[float]] = {}      # неудачные попытки входа в админку

BTN_COMPARE = "📱 Сравнить телефоны"
BTN_CODE = "🔑 Ввести код"
BTN_STATUS = "👤 Моя подписка"
BTN_BUY = "💳 Купить код"
BTN_ADMIN = "🛠 Админ-панель"
BUTTONS = {BTN_COMPARE, BTN_CODE, BTN_STATUS, BTN_BUY, BTN_ADMIN}


class S(StatesGroup):
    code = State()
    admin_password = State()
    revoke_id = State()


# ================= помощники =================
def has_access(user_id: int) -> bool:
    return db.is_admin(user_id) or db.sub_until(user_id) is not None


def fmt_until(until: datetime) -> str:
    return "навсегда" if until.isoformat(timespec="seconds") == FOREVER else f"до {until:%d.%m.%Y %H:%M}"


def main_kb(user_id: int) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=BTN_COMPARE)],
            [KeyboardButton(text=BTN_CODE), KeyboardButton(text=BTN_STATUS)],
            [KeyboardButton(text=BTN_BUY), KeyboardButton(text=BTN_ADMIN)]]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, input_field_placeholder="Например: iPhone 16 vs Galaxy S25")


def owner_url() -> str | None:
    nick = OWNER_CONTACT.lstrip("@")
    return f"https://t.me/{nick}" if nick and nick.replace("_", "").isalnum() else None


def locked_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="🔑 Ввести код", callback_data="enter_code")]]
    if owner_url():
        rows.append([InlineKeyboardButton(text=f"💬 Купить код у {OWNER_CONTACT}", url=owner_url())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


LOCKED_TEXT = (
    "⛔ <b>Доступ закрыт.</b> Подписка не активна.\n\n"
    "Чтобы пользоваться ботом, нужен код активации.\n"
    "Купить код: напиши мне в Telegram 👉 {owner}\n"
    "После оплаты я пришлю код — введи его кнопкой «🔑 Ввести код»."
)


def admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [b(text="➕ Создать код", callback_data="adm:new")],
        [b(text="📋 Коды", callback_data="adm:codes"), b(text="👥 Подписчики", callback_data="adm:subs")],
        [b(text="🚫 Отключить подписку", callback_data="adm:revoke"), b(text="📊 Статистика", callback_data="adm:stats")],
        [b(text="🚪 Выйти из админки", callback_data="adm:logout")],
    ])


def duration_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [b(text="7 дней", callback_data="adm:mk:7"), b(text="30 дней", callback_data="adm:mk:30")],
        [b(text="90 дней", callback_data="adm:mk:90"), b(text="♾ Навсегда", callback_data="adm:mk:0")],
        [b(text="← Назад", callback_data="adm:menu")],
    ])


def user_label(row) -> str:
    name = f"@{row['username']}" if row["username"] else html.escape(row["first_name"] or "без имени")
    return f"{name} (<code>{row['id']}</code>)"


async def notify_admins(bot: Bot, text: str):
    for admin_id in set(db.admin_ids()) | ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:  # админ мог не запускать бота — не мешаем пользователю
            logging.warning("Не удалось уведомить админа %s", admin_id)


async def send_long(message: Message, text: str):
    """Telegram режет сообщения длиннее 4096 символов — делим по абзацам."""
    while text:
        part = text[:4000]
        if len(text) > 4000 and "\n" in part:
            part = part[:part.rfind("\n")]
        await message.answer(part, parse_mode=None)
        text = text[len(part):].lstrip()


# ================= общие команды =================
@router.message.middleware()
async def remember_user(handler, event: Message, data):
    if event.from_user:
        db.touch_user(event.from_user.id, event.from_user.username, event.from_user.first_name)
    return await handler(event, data)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    status = "✅ Подписка активна" if has_access(uid) else "⛔ Подписка не активна"
    await message.answer(
        f"Привет, {html.escape(message.from_user.first_name or 'друг')}! 👋\n\n"
        "Я AI-бот, который сравнивает телефоны по характеристикам: процессор, камеры, экран, батарея, цена.\n"
        "Просто напиши, например: <i>iPhone 16 Pro или Galaxy S25 Ultra?</i>\n\n"
        f"{status}",
        reply_markup=main_kb(uid),
    )
    if not has_access(uid):
        await message.answer(LOCKED_TEXT.format(owner=OWNER_CONTACT), reply_markup=locked_kb())


@router.message(Command("status"))
@router.message(F.text == BTN_STATUS)
async def status(message: Message):
    uid = message.from_user.id
    if db.is_admin(uid):
        await message.answer("🛠 Ты администратор — бот для тебя бесплатный и без ограничений.")
        return
    until = db.sub_until(uid)
    if until:
        await message.answer(f"✅ <b>Подписка активна</b> {fmt_until(until)}")
    else:
        await message.answer(LOCKED_TEXT.format(owner=OWNER_CONTACT), reply_markup=locked_kb())


@router.message(Command("buy"))
@router.message(F.text == BTN_BUY)
async def buy(message: Message):
    u = message.from_user
    await message.answer(
        f"💳 Чтобы купить код, напиши мне: {OWNER_CONTACT}\n"
        "Я уже сообщил, что ты хочешь купить код. После оплаты пришлю код — введи его кнопкой «🔑 Ввести код».",
        reply_markup=locked_kb(),
    )
    name = f"@{u.username}" if u.username else html.escape(u.first_name or "")
    await notify_admins(message.bot, f"💳 Хочет купить код: {name} (<code>{u.id}</code>)")


@router.message(Command("new"))
async def new_chat(message: Message):
    history.pop(message.from_user.id, None)
    await message.answer("🧹 Начали новый диалог. Какие телефоны сравним?")


# ================= ввод кода =================
@router.message(Command("code"))
@router.message(F.text == BTN_CODE)
async def ask_code(message: Message, state: FSMContext):
    await state.set_state(S.code)
    await message.answer("🔑 Введи код активации (например <code>ABCD-EFGH-JKLM</code>):")


@router.callback_query(F.data == "enter_code")
async def ask_code_cb(cb: CallbackQuery, state: FSMContext):
    await state.set_state(S.code)
    await cb.message.answer("🔑 Введи код активации (например <code>ABCD-EFGH-JKLM</code>):")
    await cb.answer()


@router.message(S.code, F.text, ~F.text.in_(BUTTONS))
async def got_code(message: Message, state: FSMContext):
    uid = message.from_user.id
    until = db.redeem(uid, message.text)
    if not until:
        await message.answer("❌ Код неверный или уже использован. Проверь и попробуй ещё раз, или нажми /start.")
        return
    await state.clear()
    history.pop(uid, None)
    await message.answer(
        f"✅ <b>Подписка активна</b> {fmt_until(until)}\n\nТеперь бот работает. Напиши, какие телефоны сравнить 📱",
        reply_markup=main_kb(uid),
    )
    u = message.from_user
    name = f"@{u.username}" if u.username else html.escape(u.first_name or "")
    await notify_admins(message.bot, f"✅ Код активирован: {name} (<code>{uid}</code>), подписка {fmt_until(until)}")


# ================= админ-панель =================
@router.message(Command("admin"))
@router.message(F.text == BTN_ADMIN)
async def admin_entry(message: Message, state: FSMContext):
    uid = message.from_user.id
    if db.is_admin(uid):
        await message.answer("🛠 <b>Админ-панель</b>", reply_markup=admin_kb())
        return
    if ADMIN_IDS and uid not in ADMIN_IDS:
        await message.answer("⛔ Вход запрещён.")
        return
    recent = [t for t in attempts.get(uid, []) if time.time() - t < LOCK_SECONDS]
    attempts[uid] = recent
    if len(recent) >= MAX_ATTEMPTS:
        await message.answer("⛔ Слишком много неверных попыток. Попробуй через 15 минут.")
        return
    await state.set_state(S.admin_password)
    await message.answer("🔒 Введи код администратора:")


@router.message(S.admin_password, F.text, ~F.text.in_(BUTTONS))
async def admin_password(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    try:
        await message.delete()  # не оставляем пароль в переписке
    except Exception:
        pass
    if message.text.strip() != ADMIN_PASSWORD:
        attempts.setdefault(uid, []).append(time.time())
        await message.answer("⛔ Неверный код. Вход запрещён.")
        return
    attempts.pop(uid, None)
    db.set_admin(uid, True)
    await message.answer("✅ Вход выполнен. Для тебя всё бесплатно.\n\n🛠 <b>Админ-панель</b>", reply_markup=admin_kb())


@router.callback_query(F.data.startswith("adm:"))
async def admin_action(cb: CallbackQuery, state: FSMContext):
    uid = cb.from_user.id
    if not db.is_admin(uid):
        await cb.answer("⛔ Вход запрещён", show_alert=True)
        return
    action = cb.data.split(":", 2)[1:]
    msg = cb.message

    if action[0] == "menu":
        await msg.edit_text("🛠 <b>Админ-панель</b>", reply_markup=admin_kb())
    elif action[0] == "new":
        await msg.edit_text("➕ На сколько выдать подписку?", reply_markup=duration_kb())
    elif action[0] == "mk":
        days = int(action[1])
        code = db.create_code(days)
        period = "навсегда" if days == 0 else f"на {days} дн."
        await msg.answer(
            f"🎟 Код {period}:\n\n<code>{code}</code>\n\n"
            "Нажми на код, чтобы скопировать, и отправь клиенту. Код одноразовый."
        )
        await msg.answer("🛠 <b>Админ-панель</b>", reply_markup=admin_kb())
    elif action[0] == "codes":
        rows = db.recent_codes()
        lines = []
        for r in rows:
            period = "♾" if r["days"] == 0 else f"{r['days']} дн."
            if r["used_by"]:
                who = f"@{r['username']}" if r["username"] else r["used_by"]
                lines.append(f"✅ <code>{r['code']}</code> · {period} · {who}")
            else:
                lines.append(f"🆓 <code>{r['code']}</code> · {period} · свободен")
        text = "📋 <b>Последние коды</b>\n\n" + ("\n".join(lines) if lines else "Кодов пока нет.")
        await msg.edit_text(text, reply_markup=_back())
    elif action[0] == "subs":
        rows = db.active_subscribers()
        lines = [f"• {user_label(r)} — {fmt_until(datetime.fromisoformat(r['sub_until']))}" for r in rows[:50]]
        text = f"👥 <b>Активные подписки: {len(rows)}</b>\n\n" + ("\n".join(lines) if lines else "Пока никого.")
        await msg.edit_text(text, reply_markup=_back())
    elif action[0] == "stats":
        s = db.stats()
        await msg.edit_text(
            "📊 <b>Статистика</b>\n\n"
            f"Пользователей: {s['users']}\nАктивных подписок: {s['active']}\n"
            f"Кодов свободно: {s['codes_free']} · использовано: {s['codes_used']}\n"
            f"AI-запросов сегодня: {s['requests_today']} · всего: {s['requests_total']}",
            reply_markup=_back(),
        )
    elif action[0] == "revoke":
        await state.set_state(S.revoke_id)
        await msg.answer("🚫 Пришли Telegram ID пользователя (есть в списке «Подписчики»):")
    elif action[0] == "logout":
        db.set_admin(uid, False)
        await msg.edit_text("🚪 Ты вышел из админ-панели.")
    await cb.answer()


def _back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="adm:menu")]])


@router.message(S.revoke_id, F.text, ~F.text.in_(BUTTONS))
async def revoke(message: Message, state: FSMContext):
    await state.clear()
    if not db.is_admin(message.from_user.id):
        return
    if not message.text.strip().isdigit():
        await message.answer("Нужен числовой ID.", reply_markup=admin_kb())
        return
    ok = db.revoke(int(message.text.strip()))
    await message.answer("✅ Подписка отключена." if ok else "Пользователь не найден.", reply_markup=admin_kb())


# ================= сравнение телефонов =================
@router.message(Command("compare"))
@router.message(F.text == BTN_COMPARE)
async def compare_hint(message: Message):
    if not has_access(message.from_user.id):
        await message.answer(LOCKED_TEXT.format(owner=OWNER_CONTACT), reply_markup=locked_kb())
        return
    await message.answer(
        "📱 Напиши модели, которые сравнить. Примеры:\n"
        "• iPhone 16 Pro vs Galaxy S25 Ultra\n"
        "• Что лучше по камере: Pixel 9 или Xiaomi 15?\n"
        "• Телефон до 30 000 ₽ с хорошей батареей\n\n"
        "Можно задавать уточняющие вопросы. Новый диалог: /new"
    )


@router.message(F.text & ~F.text.startswith("/"))
async def ask_ai(message: Message):
    uid = message.from_user.id
    if not has_access(uid):
        await message.answer(LOCKED_TEXT.format(owner=OWNER_CONTACT), reply_markup=locked_kb())
        return
    if uid in busy:
        await message.answer("⏳ Ещё отвечаю на прошлый вопрос, подожди немного.")
        return
    if not db.is_admin(uid) and not db.count_request(uid, DAILY_LIMIT):
        await message.answer(f"Лимит {DAILY_LIMIT} запросов в сутки исчерпан. Возвращайся завтра 🙂")
        return
    if db.is_admin(uid):
        db.count_request(uid, 0)

    busy.add(uid)
    try:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await message.answer("🔎 Сравниваю, это займёт до минуты…")
        turns = history.setdefault(uid, [])
        turns.append({"role": "user", "content": message.text[:2000]})
        answer = await ai.answer(turns[-HISTORY_TURNS:])
        turns.append({"role": "assistant", "content": answer})
        del turns[:-HISTORY_TURNS]
        await send_long(message, answer)
    finally:
        busy.discard(uid)


@router.message()
async def other(message: Message):
    await message.answer("Я понимаю только текст. Напиши, какие телефоны сравнить 📱")


# ================= запуск =================
async def main():
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Укажи BOT_TOKEN в файле .env (см. .env.example)")
    if ADMIN_PASSWORD == "1234":
        logging.warning("Пароль админки 1234 — его легко подобрать. Поменяй ADMIN_PASSWORD в .env и укажи ADMIN_IDS.")
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    # меню команд внизу слева в Telegram
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="compare", description="Сравнить телефоны"),
        BotCommand(command="code", description="Ввести код активации"),
        BotCommand(command="status", description="Моя подписка"),
        BotCommand(command="buy", description="Купить код"),
        BotCommand(command="new", description="Новый диалог"),
        BotCommand(command="admin", description="Админ-панель"),
    ])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
