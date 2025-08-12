#!/bin/bash

set -euo pipefail

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

## Upgrade pip and core build tools
echo "📦 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel packaging

echo "🔌 Preinstalling grpcio binary wheel..."
if ! pip install --only-binary=:all: "grpcio>=1.62,<1.66"; then
  echo "⚠️ grpcio binary wheel not found; installing build deps and retrying..."
  sudo apt install -y pkg-config libc-ares-dev libssl-dev zlib1g-dev || true
  pip install "grpcio>=1.62,<1.66"
fi

echo "📦 Installing Python packages (prefer wheels)..."
pip install --prefer-binary -r requirements.txt

# No NLTK/model downloads needed on server (client does embeddings)

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh

# Test installation (lightweight)
echo "🧪 Testing installation..."
python3 - <<'PY'
from milvus_client import MilvusClient
print('✅ Python deps OK. Milvus client importable.')
PY

echo "✅ Installation completed successfully!"
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   python3 app.py"