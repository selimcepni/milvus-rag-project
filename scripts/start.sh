#!/bin/bash

echo "🚀 Starting Milvus RAG System..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run this script from the project directory."
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🌐 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run install.sh first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check for production mode
if [ "$1" = "production" ]; then
    echo "🏭 Starting in production mode with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --access-logfile logs/access.log --error-logfile logs/error.log app:app
else
    echo "🔧 Starting in development mode..."
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    python3 app.py
fi