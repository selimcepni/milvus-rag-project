#!/bin/bash

echo "🔧 Installing Milvus RAG System..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Update system
echo "📋 Updating system packages..."
sudo apt update

# Install Python and dependencies
echo "🐍 Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Create virtual environment
echo "🌐 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt')"

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh

# Test installation
echo "🧪 Testing installation..."
python3 -c "from text_processor import TextProcessor; from milvus_client import MilvusClient; print('✅ Installation test passed')"

echo "✅ Installation completed successfully!"
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   python3 app.py"