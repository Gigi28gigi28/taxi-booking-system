@echo off
cls
echo    DÉMARRAGE COMPLET - ARCHITECTURE MICROSERVICES
echo.
echo  Ordre de démarrage:
echo   1.  Consul (Service Registry)
echo   2.  RabbitMQ (Message Broker)
echo   3.  Auth-Service (Port 8000)
echo   4.  Ride-Service (Port 8001)
echo   5.  Traefik (API Gateway - Port 8080)
echo   6.  Matcher Worker
echo   7.  Notification Consumer
echo.
echo  Démarrage en cours...
echo.
timeout /t 2 /nobreak > nul

REM 1. Consul
echo [1/7]  Démarrage de Consul...
start "Consul Server" cmd /k start-consul.bat
timeout /t 5 /nobreak > nul
echo  Consul lancé
echo.

REM 2. RabbitMQ
echo [2/7]  Vérification de RabbitMQ...
sc query RabbitMQ > nul 2>&1
if %errorlevel% equ 0 (
    echo RabbitMQ installé - démarrage...
    net start RabbitMQ > nul 2>&1
    echo  RabbitMQ lancé
) else (
    echo  RabbitMQ non installé - ignoré
)
echo.
timeout /t 2 /nobreak > nul

REM 3. Auth-Service
echo [3/7]  Démarrage de Auth-Service...
start "Auth Service (8000)" cmd /k start-auth-service.bat
timeout /t 4 /nobreak > nul
echo  Auth-Service lancé
echo.

REM 4. Ride-Service
echo [4/7]  Démarrage de Ride-Service...
start "Ride Service (8001)" cmd /k start-ride-service.bat
timeout /t 4 /nobreak > nul
echo  Ride-Service lancé
echo.

REM 5. Traefik
echo [5/7]  Démarrage de Traefik...
start "Traefik Gateway (8080)" cmd /k start-traefik.bat
timeout /t 3 /nobreak > nul
echo  Traefik lancé
echo.

REM 6. Matcher Worker
echo [6/7]  Démarrage du Matcher Worker...
cd matcher-worker
start "Matcher Worker" cmd /k python matcher_worker.py
cd ..
timeout /t 2 /nobreak > nul
echo  Matcher Worker lancé
echo.

REM 7. Noti Démarrage du Notification Consumer...
cd matcher-worker
start "Notification Consumer" cmd /k python notification_consumer.py
cd ..
timeout /t 2 /nobreak > nul
echo  Notification Consumer lancé
echo.

echo    TOUS LES SERVICES SONT ACTIFS!
echo.
echo Dashboards disponibles:
echo    Consul UI:         http://localhost:8500
echo   Traefik Dashboard: http://localhost:8081
echo    RabbitMQ UI:       http://localhost:15672
echo.
echo Points dentrée:
echo    API Gateway:       http://localhost:8080
echo   Auth Direct:       http://localhost:8000
echo   Ride Direct:       http://localhost:8001
echo.
echo  Testez l API via Traefik:
echo   POST http://localhost:8080/accounts/api/login/
echo   GET  http://localhost:8080/api/rides/
echo.
echo  Pour tester le Load Balancing:
echo   1. Lancez: start-auth-service-replica.bat
echo   2. Exécutez: python test-load-balancing.py
echo.
echo  NE FERMEZ PAS CETTE FENÊTRE
echo    Elle sert de référence pour les URLs
echo.
pause