# ===== start_backend.sh (Linux/macOS) =====
#!/bin/bash

echo "🚀 Starting AI Recruitr Backend..."
echo "======================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please run 'python -m venv venv' first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if Gemini API key is set
if grep -q "your_gemini_api_key_here" .env; then
    echo "⚠️  Please set your GEMINI_API_KEY in the .env file."
    exit 1
fi

echo "🔧 Installing/updating dependencies..."
pip install -r requirements.txt

echo "🔍 Validating configuration..."
python -c "from config.settings import validate_settings; validate_settings()"

echo "🌐 Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"

python -m backend.main

# ===== start_backend.bat (Windows) =====
@echo off
echo 🚀 Starting AI Recruitr Backend...
echo ======================================

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Please run 'python -m venv venv' first.
    pause
    exit /b 1
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

echo 🔧 Installing/updating dependencies...
pip install -r requirements.txt

echo 🔍 Validating configuration...
python -c "from config.settings import validate_settings; validate_settings()"

echo 🌐 Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ======================================

python -m backend.main

# ===== start_frontend.sh (Linux/macOS) =====
#!/bin/bash

echo "🎨 Starting AI Recruitr Frontend..."
echo "==================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please run 'python -m venv venv' first."
    exit 1
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "⚠️  Backend is not running. Please start the backend first."
    echo "   Run: ./start_backend.sh or python -m backend.main"
    exit 1
fi

echo "🎯 Starting Streamlit frontend..."
echo "Frontend will be available at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==================================="

# Set environment variables for Streamlit
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=localhost

streamlit run frontend/app.py

# ===== start_frontend.bat (Windows) =====
@echo off
echo 🎨 Starting AI Recruitr Frontend...
echo ===================================

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Please run 'python -m venv venv' first.
    pause
    exit /b 1
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate

echo 🔍 Checking backend connection...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running!
) else (
    echo ⚠️  Backend is not running. Please start the backend first.
    echo    Run: start_backend.bat or python -m backend.main
    pause
    exit /b 1
)

echo 🎯 Starting Streamlit frontend...
echo Frontend will be available at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ===================================

REM Set environment variables for Streamlit
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=localhost

streamlit run frontend/app.py

# ===== run_all.sh (Linux/macOS) =====
#!/bin/bash

echo "🚀 Starting AI Recruitr - Full Stack"
echo "===================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your GEMINI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Validate configuration
echo "🔍 Validating configuration..."
python -c "from config.settings import validate_settings; validate_settings()" || exit 1

echo "🌐 Starting both backend and frontend..."
echo "======================================"

# Start backend in background
echo "Starting backend..."
python -m backend.main &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Check if backend started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend started successfully!"
else
    echo "❌ Backend failed to start!"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "Starting frontend..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo ""
echo "🎉 AI Recruitr is now running!"
echo "================================"
echo "📱 Frontend: http://localhost:8501"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo "================================"

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# Keep script running
wait

# ===== run_all.bat (Windows) =====
@echo off
echo 🚀 Starting AI Recruitr - Full Stack
echo ====================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo 📋 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your GEMINI_API_KEY
    echo    Then run this script again.
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Validate configuration
echo 🔍 Validating configuration...
python -c "from config.settings import validate_settings; validate_settings()"
if %errorlevel% neq 0 (
    pause
    exit /b 1
)

echo 🌐 Starting both backend and frontend...
echo ======================================

REM Start backend in background
echo Starting backend...
start "AI Recruitr Backend" cmd /c "call venv\Scripts\activate && python -m backend.main"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Check if backend started successfully
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend started successfully!
) else (
    echo ❌ Backend failed to start!
    pause
    exit /b 1
)

REM Start frontend
echo Starting frontend...
start "AI Recruitr Frontend" cmd /c "call venv\Scripts\activate && streamlit run frontend/app.py"

echo.
echo 🎉 AI Recruitr is now running!
echo ================================
echo 📱 Frontend: http://localhost:8501
echo 🔗 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Both services are running in separate windows.
echo Close the command windows to stop the services.
echo ================================
pause