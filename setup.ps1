python -m venv venv

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env creado desde .env.example"
} else {
    Write-Host ".env ya existe, no se sobreescribe"
}

Write-Host "Listo. Activa el entorno con: venv\Scripts\Activate.ps1"