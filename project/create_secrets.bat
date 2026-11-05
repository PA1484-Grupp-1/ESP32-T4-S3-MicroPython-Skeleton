@echo off
cd /d "%~dp0"
copy "secrets_example.py" "secrets_env.py" /-Y
