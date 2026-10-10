"""Мастер настройки магазина: задаёт вопросы и сохраняет ответы в файл .env."""
import re
import secrets
import string

print("=" * 60)
print("  Настройка бота-магазина. Отвечай на вопросы и нажимай Enter.")
print("=" * 60)

while True:
    token = input("\n1) Вставь токен бота от @BotFather\n   (вида 7123456789:AAH...): ").strip()
    if re.fullmatch(r"\d{6,}:[\w-]{30,}", token):
        break
    print("   ❌ Это не похоже на токен. Скопируй его из сообщения BotFather целиком.")

while True:
    ids = input("\n2) Telegram ID админов (число от @userinfobot; несколько — через запятую).\n"
                "   Только они увидят админ-панель: ").replace(" ", "")
    if re.fullmatch(r"\d+(,\d+)*", ids):
        break
    print("   ❌ Нужны только цифры. Напиши боту @userinfobot — он пришлёт твой ID.")

suggested = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
password = input(f"\n3) Пароль для входа в админ-панель\n   (Enter — взять случайный {suggested}): ").strip() or suggested

shop = input("\n4) Название магазина (Enter — VANORG): ").strip() or "VANORG"
contact = input("\n5) Контакт продавца для кнопки «Связаться», например @skimsuka\n   (Enter — не показывать): ").strip()
if contact and not contact.startswith("@") and not contact.startswith("http"):
    contact = "@" + contact

with open(".env", "w", encoding="utf-8") as f:
    f.write(f"BOT_TOKEN={token}\nADMIN_IDS={ids}\nADMIN_PASSWORD={password}\nSHOP_NAME={shop}\n"
            f"CONTACT={contact}\nCURRENCY=₽\nDB_PATH=shop.db\n")

print("\n✅ Готово! Настройки сохранены в файл .env")
print(f"   Пароль админ-панели: {password}  — запиши его.")
print("   Поменять настройки: удали файл .env и запусти бота снова (или открой .env в редакторе).\n")
