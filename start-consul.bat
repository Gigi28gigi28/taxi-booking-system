@echo off
echo   Démarrage de Consul en mode Dev

REM Créer le dossier data si inexistant
if not exist "consul-data" mkdir consul-data

REM Lancer Consul avec le fichier de config
consul agent -dev -config-file=consul-config.json

echo.
echo Consul UI accessible sur: http://localhost:8500
echo.
pause