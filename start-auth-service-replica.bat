@echo off
echo  Démarrage Auth-Service REPLICA (Port 8002)
echo.

cd auth-service

REM Variables d'environnement pour Consul
set CONSUL_HOST=localhost
set CONSUL_PORT=8500
set SERVICE_NAME=auth-service
set SERVICE_PORT=8002
set SERVICE_HOST=127.0.0.1

echo ════════════════════════════════════════════
echo Configuration REPLICA:
echo   - Service: %SERVICE_NAME% (Instance 2)
echo   - Port: %SERVICE_PORT%
echo   - Consul: %CONSUL_HOST%:%CONSUL_PORT%
echo ════════════════════════════════════════════
echo.

echo ⏳ Lancement Django sur port %SERVICE_PORT%...
echo.

REM Lancer Django sur port différent
python manage.py runserver 0.0.0.0:8002

pause