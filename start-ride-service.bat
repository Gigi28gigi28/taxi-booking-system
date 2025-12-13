@echo off
echo   Démarrage Ride-Service (Port 8001)

cd ride-service

REM Variables d'environnement pour Consul
set CONSUL_HOST=localhost
set CONSUL_PORT=8500
set SERVICE_NAME=ride-service
set SERVICE_PORT=8001
set SERVICE_HOST=127.0.0.1

REM Configuration Auth-Service pour middleware
set AUTH_VERIFY_URL=http://localhost:8080/accounts/api/verify/

echo.
echo Configuration Consul:
echo   - Host: %CONSUL_HOST%:%CONSUL_PORT%
echo   - Service: %SERVICE_NAME%
echo   - Port: %SERVICE_PORT%
echo.

REM Lancer Django
python manage.py runserver 0.0.0.0:8001

pause