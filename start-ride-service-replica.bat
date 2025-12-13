@echo off
echo  Démarrage Ride-Service REPLICA (Port 8003)
echo.

cd ride-service

REM Variables d'environnement pour Consul
set CONSUL_HOST=localhost
set CONSUL_PORT=8500
set SERVICE_NAME=ride-service
set SERVICE_PORT=8003
set SERVICE_HOST=127.0.0.1

REM Configuration Auth-Service (découverte via Consul)
set AUTH_VERIFY_URL=http://localhost:8080/accounts/api/verify/

echo ════════════════════════════════════════════
echo Configuration REPLICA:
echo   - Service: %SERVICE_NAME% (Instance 2)
echo   - Port: %SERVICE_PORT%
echo   - Consul: %CONSUL_HOST%:%CONSUL_PORT%
echo ════════════════════════════════════════════
echo.

echo  Lancement Django sur port %SERVICE_PORT%...
echo.

REM Lancer Django sur port différent
python manage.py runserver 0.0.0.0:8003

pause