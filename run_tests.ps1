$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "[ОШИБКА] Не найден $py" -ForegroundColor Red
    Write-Host "Создайте venv: py -3 -m venv .venv"
    Write-Host "Установите зависимости: .\.venv\Scripts\pip install -r requirements.txt"
    exit 1
}

& $py (Join-Path $PSScriptRoot "run_tests.py") @args
exit $LASTEXITCODE
