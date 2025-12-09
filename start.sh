#!/bin/bash

# Function to kill processes on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "Starting Backend..."
cd backend
# Check if venv exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: No virtual environment found in backend/venv"
fi

# Install dependencies if needed (optional, but good for first run)
# pip install -r requirements.txt

# Start FastAPI
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID"

cd ..

echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID"

# Wait for processes
wait
