@echo off
echo   Démarrage Auth-Service (Port 8000)

cd auth-service

REM Variables d'environnement pour Consul
set CONSUL_HOST=localhost
set CONSUL_PORT=8500
set SERVICE_NAME=auth-service
set SERVICE_PORT=8000
set SERVICE_HOST=127.0.0.1

echo.
echo Configuration Consul:
echo   - Host: %CONSUL_HOST%:%CONSUL_PORT%
echo   - Service: %SERVICE_NAME%
echo   - Port: %SERVICE_PORT%
echo.

REM Lancer Django
python manage.py runserver 0.0.0.0:8000

pause