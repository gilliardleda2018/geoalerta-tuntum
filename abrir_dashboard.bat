@echo off
cd /d C:\tuntum_enchentes
call .venv\Scripts\activate
streamlit run dashboard_tuntum.py
pause