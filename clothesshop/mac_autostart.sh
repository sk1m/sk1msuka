#!/usr/bin/env bash
# Автозапуск бота на Mac: работает в фоне без открытого Терминала и сам стартует после перезагрузки.
#   ./mac_autostart.sh         — включить
#   ./mac_autostart.sh off     — выключить
#   ./mac_autostart.sh restart — перезапустить (после изменения .env или products.py)
cd "$(dirname "$0")" || exit 1
DIR="$(pwd)"
LABEL="com.clothesshop.bot"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

case "$1" in
  off)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null
    rm -f "$PLIST"
    echo "Автозапуск выключен, бот остановлен."
    exit 0 ;;
  restart)
    launchctl kickstart -k "$DOMAIN/$LABEL" && echo "Бот перезапущен." || echo "Автозапуск не включён. Сначала: ./mac_autostart.sh"
    exit 0 ;;
esac

if [ ! -x .venv/bin/python ] || [ ! -f .env ]; then
  echo "Сначала один раз запусти ./start.sh — он установит компоненты и спросит настройки."
  echo "Потом останови его (Ctrl+C) и запусти ./mac_autostart.sh"
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$DIR/.venv/bin/python</string>
    <string>bot.py</string>
  </array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>EnvironmentVariables</key>
  <dict><key>PYTHONUNBUFFERED</key><string>1</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$DIR/bot.log</string>
  <key>StandardErrorPath</key><string>$DIR/bot.log</string>
</dict>
</plist>
PLISTEOF

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null
launchctl bootstrap "$DOMAIN" "$PLIST"
sleep 3
if launchctl print "$DOMAIN/$LABEL" 2>/dev/null | grep -q "state = running"; then
  echo "✅ Бот работает в фоне и будет запускаться сам после перезагрузки Mac."
else
  echo "⚠️ Бот не запустился. Посмотри ошибку: tail -n 30 bot.log"
fi
echo "   Логи:        tail -f bot.log"
echo "   Перезапуск:  ./mac_autostart.sh restart"
echo "   Выключить:   ./mac_autostart.sh off"
echo "   Важно: Mac не должен засыпать (Настройки → Аккумулятор/Экран → не переходить в сон)."
