#!/bin/bash

echo "🚀 Starting Milvus RAG System..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run this script from the project directory."
    exit 1
fi

# Activate virtual environment (supports VENV_PATH override)
VENV_PATH=${VENV_PATH:-venv}
if [ -d "$VENV_PATH" ]; then
    echo "🌐 Activating virtual environment at $VENV_PATH..."
    # shellcheck disable=SC1090
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Virtual environment not found at $VENV_PATH. Run install.sh first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check for production mode
if [ "$1" = "production" ]; then
    echo "🏭 Starting in production mode with Gunicorn..."
    # Bazı ortamlarda gunicorn script'i çalışmayabilir; güvenli yol: python -m gunicorn
    exec python -m gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 \
        --access-logfile logs/access.log --error-logfile logs/error.log app:app
else
    echo "🔧 Starting in development mode..."
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    python3 app.py
fi