@echo off
REM Wrapper script for liriklagu on Windows
setlocal

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
set "PARENT_DIR=%SCRIPT_DIR%.."

REM Try to activate virtual environment if it exists
if exist "%PARENT_DIR%\venv\Scripts\activate.bat" (
    call "%PARENT_DIR%\venv\Scripts\activate.bat"
)

REM Run the main script
python "%PARENT_DIR%\src\main.py" %*

REM If python command fails, try python3
if %ERRORLEVEL% NEQ 0 (
    python3 "%PARENT_DIR%\src\main.py" %*
)

endlocal