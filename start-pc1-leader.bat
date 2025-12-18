@echo off
echo ========================================
echo  PC 1 - CONSUL LEADER + GATEWAY
echo ========================================
echo.

set PC1_IP=192.168.1.38

echo [1/3] Starting Consul Leader...
start "Consul Leader" cmd /k ^
"consul agent ^
 -server ^
 -bootstrap-expect=1 ^
 -datacenter=dc1 ^
 -node=consul-leader-pc1 ^
 -data-dir=consul-data-pc1 ^
 -bind=%PC1_IP% ^
 -advertise=%PC1_IP% ^
 -client=0.0.0.0 ^
 -ui ^
 -log-level=INFO"

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
echo  PC 1 READY!
echo ========================================
echo.
echo Consul UI:      http://%PC1_IP%:8500
echo Traefik:        http://%PC1_IP%:8082
echo API Gateway:    http://%PC1_IP%:8080
echo Frontend:       http://%PC1_IP%:3000
echo.
echo Other machines should connect to: %PC1_IP%
echo.
pause



