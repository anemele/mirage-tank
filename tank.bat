@echo off

setlocal

set PYTHONPATH=%~dp0;%PYTHONPATH%
set py=%~dp0.venv\Scripts\python.exe

%py% -m mirage_tank %*