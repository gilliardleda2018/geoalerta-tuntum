@echo off
cd /d C:\tuntum_enchentes
python -m uvicorn api_tuntum:app --reload
pause