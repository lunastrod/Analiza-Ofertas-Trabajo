# Python-venv-plantilla

## Setup

1. Ejecuta el script de configuración (activa el entorno automáticamente):
```powershell
   .\setup.ps1
```

2. Activa el entorno:
```powershell
   venv\Scripts\Activate.ps1
```

3. Instala las dependencias:
```powershell
   pip install -r requirements.txt
```

## Guardar dependencias
```powershell
pip freeze > requirements.txt
```

## Desactivar el entorno
```powershell
deactivate
```