#!/usr/bin/env bash
# Установка на сервер Ubuntu/Debian с автозапуском. Запуск из папки бота: sudo bash server_install.sh
set -e
cd "$(dirname "$(readlink -f "$0")")"
DIR="$(pwd)"

echo "==> Устанавливаю Python..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv >/dev/null

echo "==> Устанавливаю компоненты бота..."
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -r requirements.txt -q

[ -f .env ] || .venv/bin/python setup_env.py

echo "==> Настраиваю автозапуск..."
cat > /etc/systemd/system/phonebot.service <<UNIT
[Unit]
Description=PhoneBot Telegram bot
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now phonebot
sleep 3
systemctl --no-pager status phonebot | head -5
echo
echo "✅ Готово. Бот работает круглосуточно и сам запускается после перезагрузки."
echo "   Логи:        journalctl -u phonebot -f"
echo "   Перезапуск:  systemctl restart phonebot"
echo "   Остановка:   systemctl stop phonebot"
