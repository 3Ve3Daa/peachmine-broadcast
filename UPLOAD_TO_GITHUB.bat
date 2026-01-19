@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo 🚀 Загрузка на GitHub...
echo.

git add .
git commit -m "Fix: Remove tokens from documentation"

echo.
echo 📤 Отправка на GitHub...
git push origin main --force

if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════
    echo   ⚠️ GitHub заблокировал push из-за токена
    echo ═══════════════════════════════════════════
    echo.
    echo Что делать:
    echo.
    echo 1. Перейди по ссылке которую показал GitHub
    echo 2. Нажми "Allow secret" чтобы разрешить
    echo 3. Запусти этот файл снова
    echo.
    echo ИЛИ:
    echo.
    echo Скопируй и выполни вручную:
    echo   git push origin main --force
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════
echo   ✅ Готово! Код залит на GitHub!
echo ═══════════════════════════════════════════
echo.
echo 📋 Следующие шаги:
echo 1. Зайди на railway.app
echo 2. New Project - Deploy from GitHub repo
echo 3. Добавь Variables (см. peachmine-broadcast/.env)
echo 4. Start Command: python bot.py
echo 5. Deploy!
echo.
pause
