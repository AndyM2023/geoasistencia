@echo off
echo 🚀 INICIANDO ENTORNO DE DESARROLLO DJANGO
echo ==========================================

REM Activar entorno virtual
echo 📦 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar dependencias
echo 🔍 Verificando dependencias...
python run_dev.py

pause
