@echo off
cd /d C:\tuntum_enchentes
start cmd /k "python -m uvicorn api_tuntum:app --reload"
timeout /t 3 >nul
cd /d C:\tuntum_enchentes\webapp
start cmd /k "npm run dev"
timeout /t 5 >nul
start http://localhost:5173
exit