#!/usr/bin/env bash
# Запуск бота на Mac и Linux: ./start.sh
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python не найден. Установи его с https://www.python.org/downloads/ и запусти снова."
  exit 1
fi

# Нужен Python 3.10+. На Mac встроенный python3 бывает 3.9 — тогда берём установленный с python.org или Homebrew
PY=python3
for cand in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
    PY="$cand"; break
  fi
done
if ! "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
  echo "Нужен Python 3.10 или новее, а сейчас: $(python3 --version 2>&1)."
  echo "Установи свежий Python с https://www.python.org/downloads/ (или: brew install python) и запусти снова."
  exit 1
fi

if [ -x ".venv/bin/python" ] && ! .venv/bin/python -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
  echo "Старое окружение на устаревшем Python — пересоздаю..."
  rm -rf .venv
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Первый запуск: устанавливаю нужные компоненты, это займёт 1-2 минуты..."
  "$PY" -m venv .venv || { echo "Не удалось создать окружение. На Ubuntu выполни: sudo apt install python3-venv"; exit 1; }
  .venv/bin/python -m pip install --upgrade pip -q
  .venv/bin/python -m pip install -r requirements.txt -q || { echo "Не удалось установить компоненты. Проверь интернет."; exit 1; }
fi

[ -f .env ] || .venv/bin/python setup_env.py

echo
echo "Запускаю бота. Пока это окно открыто, бот работает. Остановить: Ctrl+C."
echo
exec .venv/bin/python bot.py
