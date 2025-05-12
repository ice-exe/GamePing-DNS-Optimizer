@echo off
echo Starting DNS Tester...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6 or higher.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Run the DNS Tester
python dns_tester.py %*

REM Exit with the same error code as the Python script
exit /b %errorlevel%