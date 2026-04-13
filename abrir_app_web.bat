@echo off
cd /d C:\tuntum_enchentes\webapp
start cmd /k "npm run dev"
timeout /t 3 >nul
start http://localhost:5173
exit