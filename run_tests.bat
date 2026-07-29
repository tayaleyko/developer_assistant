@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Не найден .venv\Scripts\python.exe
    echo Создайте окружение: py -3 -m venv .venv
    echo Затем: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "%~dp0run_tests.py" %*
set EXITCODE=%ERRORLEVEL%
if "%EXITCODE%" neq "0" pause
exit /b %EXITCODE%
