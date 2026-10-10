#!/usr/bin/env bash
# Запуск бота на Mac и Linux: ./start.sh
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python не найден. Установи его с https://www.python.org/downloads/ и запусти снова."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Первый запуск: устанавливаю нужные компоненты, это займёт 1-2 минуты..."
  python3 -m venv .venv || { echo "Не удалось создать окружение. На Ubuntu выполни: sudo apt install python3-venv"; exit 1; }
  .venv/bin/python -m pip install --upgrade pip -q
  .venv/bin/python -m pip install -r requirements.txt -q || { echo "Не удалось установить компоненты. Проверь интернет."; exit 1; }
fi

[ -f .env ] || .venv/bin/python setup_env.py

echo
echo "Запускаю бота. Пока это окно открыто, бот работает. Остановить: Ctrl+C."
echo
exec .venv/bin/python bot.py
