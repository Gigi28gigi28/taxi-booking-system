@echo off
echo   Démarrage de Traefik Reverse Proxy

REM Vérifier que Consul est actif
echo Vérification de Consul...
curl -s http://localhost:8500/v1/status/leader > nul
if errorlevel 1 (
    echo  ERREUR: Consul n'est pas actif!
    echo Lancez d'abord: start-consul.bat
    pause
    exit /b 1
)

echo Consul actif

REM Lancer Traefik en arrière-plan dans une nouvelle fenêtre
echo.
echo Lancement de Traefik...
start "Traefik Reverse Proxy" "C:\Traefik\traefik.exe" --configFile="C:\Users\ss\Desktop\Taxi-booking-system\traefik.yml" --log.level=DEBUG

timeout /t 3 /nobreak > nul

echo.
echo   Traefik est en cours d'exécution dans une fenêtre séparée
echo   Traefik Dashboard: http://localhost:8081
echo   API Gateway: http://localhost:8080
echo.
echo   Ne fermez pas la fenêtre Traefik!
pause