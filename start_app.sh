#!/bin/bash
echo "🚀 Starting SmartSpend AI..."

# Get absolute path to backend
BASE_DIR=$(pwd)

# Train Model if not exists
if [ ! -f "ml_engine/models/classifier.pkl" ]; then
    echo "🧠 Training ML Model..."
    export PYTHONPATH=$BASE_DIR/backend
    python ml_engine/training/train_model.py
fi

# Init DB
echo "🗄️ Initializing Database..."
export PYTHONPATH=$BASE_DIR/backend
python backend/init_db.py

# Start Backend
echo "🐍 Starting Flask Backend (Port 8000)..."
cd backend
export PYTHONPATH=$BASE_DIR/backend
python run.py &
BACKEND_PID=$!

# Start Frontend
echo "⚛️ Starting Next.js Frontend (Port 3000)..."
cd ../frontend 
npm run dev &
FRONTEND_PID=$!

echo "✅ App is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
