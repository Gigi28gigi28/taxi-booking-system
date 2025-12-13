@echo off
echo   DÉMARRAGE COMPLET DE L'ARCHITECTURE MICROSERVICES
echo.
echo Ordre de démarrage:
echo   1. Consul (Service Registry)
echo   2. Auth-Service (Port 8000)
echo   3. Ride-Service (Port 8001)
echo   4. Traefik (API Gateway - Port 8080)
echo   5. RabbitMQ (Message Broker)
echo   6. Matcher Worker
echo.
echo.

REM 1. Consul
echo [1/6] Démarrage de Consul...
start "Consul Server" cmd /k start-consul.bat
timeout /t 5 /nobreak > nul

REM 2. Auth-Service
echo [2/6] Démarrage de Auth-Service...
start "Auth Service" cmd /k start-auth-service.bat
timeout /t 3 /nobreak > nul

REM 3. Ride-Service
echo [3/6] Démarrage de Ride-Service...
start "Ride Service" cmd /k start-ride-service.bat
timeout /t 3 /nobreak > nul

REM 4. Traefik
echo [4/6] Démarrage de Traefik...
start "Traefik Gateway" cmd /k start-traefik.bat
timeout /t 3 /nobreak > nul

REM 5. RabbitMQ (si installé localement)
echo [5/6] Vérification de RabbitMQ...
sc query RabbitMQ > nul 2>&1
if %errorlevel% equ 0 (
    echo RabbitMQ détecté - démarrage...
    net start RabbitMQ
) else (
    echo RabbitMQ non installé - lancez Docker si nécessaire
)

REM 6. Matcher Worker
echo [6/6] Démarrage du Matcher Worker...
cd matcher-worker
start "Matcher Worker" cmd /k python matcher_worker.py
cd ..

echo.
echo    TOUS LES SERVICES SONT EN COURS DE DÉMARRAGE
echo.
echo Interfaces disponibles:
echo   - Consul UI:         http://localhost:8500
echo   - Traefik Dashboard: http://localhost:8082
echo   - API Gateway:       http://localhost:8080
echo   - Auth-Service:      http://localhost:8000
echo   - Ride-Service:      http://localhost:8001
echo.
echo Testez l'API via Traefik:
echo   POST http://localhost:8080/accounts/api/login/
echo   GET  http://localhost:8080/api/rides/
echo.
pause