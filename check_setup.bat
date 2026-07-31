@echo off
REM ============================================================================
REM Quick Setup Check for Document Processing Pipeline (Windows)
REM ============================================================================

echo.
echo ================================================================================
echo   Document Processing Pipeline - Setup Checker
echo ================================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Python is not installed or not in PATH
    echo     Install Python 3.8+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [✓] Python is installed
python --version

REM Check if requirements are installed
echo.
echo Checking Python dependencies...
python test_installation.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo   Setup is complete! Ready to process documents.
    echo ================================================================================
    echo.
    echo Try: python app.py --pdf your_document.pdf
    echo.
) else (
    echo.
    echo ================================================================================
    echo   Setup needs attention. Please follow the instructions above.
    echo ================================================================================
    echo.
)

pause
