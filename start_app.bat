@echo off
REM Launcher for PingTest Streamlit Application
echo Starting PingTest Monitoring Application...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Error: Streamlit is not installed.
    echo Please install it with: python -m pip install streamlit
    pause
    exit /b 1
)

REM Launch the Streamlit application
python -m streamlit run "%~dp0app.py" --server.headless=true --server.port=8501

pause
