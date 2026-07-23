$FimsRoot = $PSScriptRoot
$venvPython = Join-Path $FimsRoot "venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found at $venvPython. Run: python -m venv venv" -ForegroundColor Red
    exit 1
}

Set-Location $FimsRoot

Start-Job -ScriptBlock { Start-Sleep -Seconds 2; Start-Process "http://127.0.0.1:5050/" } | Out-Null

Write-Host "Starting FIMS dashboard at http://127.0.0.1:5050/ (Ctrl+C to stop)" -ForegroundColor Cyan
& $venvPython -m flask --app fims.dashboard.app run --port 5050
