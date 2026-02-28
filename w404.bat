@echo off
REM Wizard404 CLI - Windows. Desde la raiz del repo.
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
if exist "%ROOT%\backend\venv\Scripts\activate.bat" call "%ROOT%\backend\venv\Scripts\activate.bat"
set PYTHONPATH=%ROOT%\backend;%ROOT%\cli;%PYTHONPATH%
python -m wizard404_cli.main %*
