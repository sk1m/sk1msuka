@echo off
chcp 65001 >nul
cd /d "%~dp0"
title PhoneBot

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Python не найден.
  echo  Установи его с https://www.python.org/downloads/
  echo  и при установке поставь галочку "Add Python to PATH".
  echo.
  pause
  exit /b
)

if not exist ".venv\Scripts\python.exe" (
  echo  Первый запуск: устанавливаю нужные компоненты, это займёт 1-2 минуты...
  python -m venv .venv
  ".venv\Scripts\python.exe" -m pip install --upgrade pip -q
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt -q
  if errorlevel 1 (
    echo  Не удалось установить компоненты. Проверь интернет и запусти ещё раз.
    pause
    exit /b
  )
)

if not exist ".env" ".venv\Scripts\python.exe" setup_env.py

echo.
echo  Запускаю бота. Пока это окно открыто, бот работает.
echo  Чтобы остановить, закрой окно или нажми Ctrl+C.
echo.
".venv\Scripts\python.exe" bot.py
pause
