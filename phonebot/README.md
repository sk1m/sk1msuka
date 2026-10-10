# PhoneBot — сравнение техники Apple в Telegram

Бот сравнивает iPhone, iPad, Mac, Apple Watch и AirPods по характеристикам.
Работает **бесплатно**: без AI и платных сервисов, все данные лежат внутри бота (`products.py`).
Пользоваться ботом можно только по подписке: без кода активации доступ закрыт.

## Что умеет
- Сравнивать 2–3 устройства: по каждой характеристике ✅ у лучшего значения и итог в конце.
- Выбор кнопками (категория → модель) или текстом: «iPhone 15 vs 16 Pro», «макбук эйр м1 или м4», «AirPods Pro 2 vs Pro 3».
- Карточка одной модели, если написать только её («айфон 17 про макс»).
- Можно сравнивать разные категории, например iPhone с iPad: тогда показываются общие характеристики.

В базе 90 устройств: iPhone с XR (2018) до 17 Pro Max и Air, iPad (обычные, mini, Air, Pro),
MacBook Air и Pro от M1 до M5, iMac, Mac mini, Mac Studio, Apple Watch SE / Series 9–11 / Ultra 2–3, AirPods 4 / Pro 2 / Pro 3 / Max.

## Как работает подписка
1. Человек запускает бота и видит «⛔ Подписка не активна» и кнопку «💬 Купить код у @skimsuka».
2. Он нажимает «💳 Купить код», тебе приходит уведомление, вы договариваетесь в личке.
3. Ты заходишь в «🛠 Админ-панель», жмёшь «➕ Создать код», выбираешь срок (7 / 30 / 90 дней или навсегда) и отправляешь код клиенту.
4. Клиент жмёт «🔑 Ввести код», вводит его и видит «✅ Подписка активна до …». Бот заработал.

Коды одноразовые. Если ввести новый код при действующей подписке, срок продлевается.

## Админ-панель
Вход: кнопка «🛠 Админ-панель» или /admin, затем пароль из `ADMIN_PASSWORD` (по умолчанию `1234`).
Для админа всё бесплатно. В панели: создать код, список кодов, подписчики, отключить подписку, статистика.
После 5 неверных паролей вход блокируется на 15 минут, сообщение с паролем бот удаляет.

> ⚠️ Пароль `1234` легко подобрать. Поставь свой длинный пароль в `ADMIN_PASSWORD`
> и впиши свой Telegram ID в `ADMIN_IDS`: тогда в админку не пустит никого, кроме тебя.

## Запуск
1. Создай бота у [@BotFather](https://t.me/BotFather) (`/newbot`) и возьми токен.
2. Узнай свой Telegram ID у [@userinfobot](https://t.me/userinfobot).
3. Установи Python 3.10+ с [python.org](https://www.python.org/downloads/) (на Windows поставь галочку «Add Python to PATH»).
4. В папке `phonebot` выполни:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   copy .env.example .env          # Mac/Linux: cp .env.example .env
   ```
5. Открой `.env` и впиши `BOT_TOKEN`, `ADMIN_PASSWORD`, `ADMIN_IDS`.
6. Запусти: `python bot.py`. Когда появится `Start polling`, бот работает.

Бот отвечает, пока запущен скрипт. Чтобы он работал круглосуточно, его нужно держать на компьютере,
который не выключается, или на сервере (см. ниже).

## Настройки (`.env`)
| Переменная | Что это |
|---|---|
| `BOT_TOKEN` | токен от BotFather |
| `ADMIN_PASSWORD` | пароль админки |
| `ADMIN_IDS` | твой Telegram ID (через запятую, если несколько) |
| `OWNER_CONTACT` | ник, куда писать за кодом (по умолчанию @skimsuka) |
| `DB_PATH` | файл базы SQLite с подписками и кодами |

## Круглосуточная работа на сервере (Ubuntu)
```bash
apt update && apt install -y python3-venv
cd /root/phonebot && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cat > /etc/systemd/system/phonebot.service <<'UNIT'
[Unit]
Description=PhoneBot
After=network-online.target

[Service]
WorkingDirectory=/root/phonebot
ExecStart=/root/phonebot/.venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
UNIT
systemctl enable --now phonebot
```
Логи: `journalctl -u phonebot -f`. Перезапуск после правки `.env`: `systemctl restart phonebot`.

## Как добавить устройство
Открой `products.py` и допиши строку в нужный раздел по образцу соседних, например для iPhone:
```python
_iphone("iPhone 18", 2026, "A20", '6,3" OLED 120 Гц ProMotion', "48 Мп + 48 Мп ширик", "18 Мп", 30,
        "256/512 ГБ", 177, "Face ID", "USB-C (USB 2)", 799, "что нового"),
```
Перезапусти бота, и модель появится в кнопках и поиске.

Данные взяты из официальных характеристик Apple на момент выхода. Цены стартовые, в долларах США.
