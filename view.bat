@echo off

setlocal

set PYTHONPATH=%~dp0;%PYTHONPATH%
set py=%~dp0.venv\Scripts\python.exe

start http://localhost:5000/
%py% viewer\app.py