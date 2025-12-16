@echo off
echo ==============================
echo DÉMARRAGE MACHINE 2 - Auth-Service
echo ==============================
echo.

REM Variables pour Consul
set CONSUL_SERVER=192.168.1.10
set CONSUL_PORT=8500

REM Démarrer l'agent Consul et rejoindre le leader
start "Consul Agent" cmd /k "consul agent -bind=%COMPUTERNAME% -retry-join=%CONSUL_SERVER% -client=0.0.0.0"

timeout /t 3 /nobreak > nul

REM Auth-Service
cd auth-service
start "Auth-Service" cmd /k "python manage.py runserver 0.0.0.0:8000"
cd ..

echo Machine 2 prête.
pause