@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo 🧹 Очистка истории Git от токенов...
echo.
echo ⚠️ Это удалит старые коммиты и создаст новую историю
echo.
pause

echo.
echo 📝 Создание нового начального коммита...

REM Удаляем .git папку
rd /s /q .git

REM Инициализируем заново
git init
git branch -M main

REM Добавляем remote
git remote add origin https://github.com/3Ve3Daa/peachmine-broadcast.git

REM Добавляем все файлы
git add .

REM Создаем первый коммит
git commit -m "Initial commit: Clean Railway deployment structure"

echo.
echo 📤 Force push на GitHub...
git push origin main --force

if errorlevel 1 (
    echo.
    echo ❌ Ошибка при отправке!
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════
echo   ✅ Готово! История очищена!
echo ═══════════════════════════════════════════
echo.
echo Теперь можешь деплоить на Railway!
echo.
pause
