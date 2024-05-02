@echo off
cd /d "%~dp0"
start /B py -m pipenv run python "test.py"
pause