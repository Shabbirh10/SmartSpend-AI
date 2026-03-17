#!/bin/bash
set -e
echo "🚀 Starting SmartSpend AI..."

BASE_DIR=$(pwd)

# Backend venv + deps
if [ ! -d ".venv" ]; then
  echo "🐍 Creating Python venv..."
  python3 -m venv .venv
fi

echo "📦 Installing backend dependencies..."
. .venv/bin/activate
pip install -r backend/requirements.txt

# Frontend deps
if [ ! -d "frontend/node_modules" ]; then
  echo "📦 Installing frontend dependencies..."
  (cd frontend && npm ci)
fi

# Train Model if not exists
if [ ! -f "ml_engine/models/classifier.pkl" ]; then
    echo "🧠 Training ML Model..."
    export PYTHONPATH=$BASE_DIR
    python3 ml_engine/training/train_model.py
fi

# Init DB
echo "🗄️ Initializing Database..."
export PYTHONPATH=$BASE_DIR
python3 backend/init_db.py

# Start Backend
echo "🐍 Starting Flask Backend (Port 8000)..."
cd backend
export PYTHONPATH=$BASE_DIR
python3 run.py &
BACKEND_PID=$!

# Start Frontend
echo "⚛️ Starting Next.js Frontend (Port 3000)..."
cd ../frontend 
npx next dev -H 127.0.0.1 -p 3000 &
FRONTEND_PID=$!

echo "✅ App is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
