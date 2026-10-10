"""Мастер настройки: задаёт вопросы и сохраняет ответы в файл .env."""
import re
import secrets
import string

print("=" * 60)
print("  Настройка бота. Отвечай на вопросы и нажимай Enter.")
print("=" * 60)

# 1. Токен
while True:
    token = input("\n1) Вставь токен бота от @BotFather\n   (вида 7123456789:AAH...): ").strip()
    if re.fullmatch(r"\d{6,}:[\w-]{30,}", token):
        break
    print("   ❌ Это не похоже на токен. Скопируй его из сообщения BotFather целиком.")

# 2. Пароль админки
suggested = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
password = input(f"\n2) Придумай пароль для админ-панели\n   (Enter — взять случайный {suggested}): ").strip() or suggested
if password == "1234":
    print("   ⚠️ Пароль 1234 легко подобрать. Обязательно заполни следующий пункт (свой ID).")

# 3. Telegram ID
while True:
    ids = input("\n3) Твой Telegram ID (число от @userinfobot; несколько — через запятую)\n   "
                "Только с этих аккаунтов можно войти в админку: ").replace(" ", "")
    if re.fullmatch(r"\d+(,\d+)*", ids):
        break
    print("   ❌ Нужны только цифры. Напиши боту @userinfobot — он пришлёт твой ID.")

# 4. Контакт
contact = input("\n4) Ник, куда писать за покупкой кода (Enter — @skimsuka): ").strip() or "@skimsuka"
if not contact.startswith("@"):
    contact = "@" + contact

with open(".env", "w", encoding="utf-8") as f:
    f.write(f"BOT_TOKEN={token}\nADMIN_PASSWORD={password}\nADMIN_IDS={ids}\nOWNER_CONTACT={contact}\nDB_PATH=phonebot.db\n")

print("\n✅ Готово! Настройки сохранены в файл .env")
print(f"   Пароль админки: {password}  — запиши его.")
print("   Поменять настройки: удали файл .env и запусти бота снова (или открой .env в Блокноте).\n")
