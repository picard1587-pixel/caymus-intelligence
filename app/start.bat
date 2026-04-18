@echo off
echo ============================================
echo  Caymus Recruiting Dashboard
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if database exists, if not import CSV
if not exist "recruiting.db" (
    echo Creating database from CSV...
    python import_csv.py
    if errorlevel 1 (
        echo ERROR: Failed to import CSV
        pause
        exit /b 1
    )
)

echo.
echo Starting server...
echo.
echo Open your browser to: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.

python app.py

pause
