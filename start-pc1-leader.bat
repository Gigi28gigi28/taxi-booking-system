@echo off
cls
echo ========================================
echo  PC1 - CONSUL LEADER + GATEWAY + UI
echo  IP: 10.70.95.95
echo ========================================
echo.

echo [1/3] Starting Consul Leader...
start "Consul Leader" cmd /k "consul agent -config-file=consul-config.json"
timeout /t 5 /nobreak > nul

echo [2/3] Starting Traefik Gateway...
start "Traefik Gateway" cmd /k "traefik --configFile=traefik.yml"
timeout /t 3 /nobreak > nul

echo [3/3] Starting Frontend...
cd ui
start "React Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo  PC1 READY!
echo ========================================
echo.
echo Consul UI:      http://10.70.95.95:8500
echo Traefik:        http://10.70.95.95:8082
echo API Gateway:    http://10.70.95.95:8080
echo Frontend:       http://10.70.95.95:3000
echo.
echo Other machines connect to: 10.70.95.95:8500
echo.
pause