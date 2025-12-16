@echo off
echo ═══════════════════════════════════════════════
echo    Démarrage de Traefik Reverse Proxy
echo ═══════════════════════════════════════════════
echo.

REM Vérifier que Consul est actif
echo 🔍 Vérification de Consul...
curl -s http://localhost:8500/v1/status/leader > nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERREUR: Consul n'est pas actif!
    echo.
    echo Lancez d'abord: start-consul.bat
    echo.
    pause
    exit /b 1
)

echo  Consul actif
echo.

REM Vérifier que le fichier de config existe
if not exist "traefik.yml" (
    echo  ERREUR: fichier traefik.yml introuvable!
    echo Assurez-vous d'être dans le bon répertoire
    pause
    exit /b 1
)

echo  Configuration trouvée: traefik.yml
echo.

REM Lancer Traefik
echo  Lancement de Traefik...
echo.
echo ════════════════════════════════════════════
echo   Traefik est maintenant actif!
echo ════════════════════════════════════════════
echo.
echo  Dashboard: http://localhost:8082
echo  API Gateway: http://localhost:8080
echo.
echo  Testez vos services:
echo   - Auth:  http://localhost:8080/accounts/api/...
echo   - Rides: http://localhost:8080/api/rides/
echo.
echo  Ne fermez pas cette fenêtre!
echo.

REM Lancer Traefik avec le fichier de config du répertoire courant
traefik --configFile=traefik.yml --log.level=DEBUG

pause