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

# Install core Python packages (except torch first)
echo "📦 Installing core Python packages (prefer wheels)..."
grep -v '^torch' requirements.txt > /tmp/req-no-torch.txt
pip install --prefer-binary -r /tmp/req-no-torch.txt

# Install torch from official CPU wheels (compatible with many Python versions)
echo "🧠 Installing PyTorch (CPU) ..."
pip install "torch>=2.3,<3" --index-url https://download.pytorch.org/whl/cpu

# Download NLTK data
echo "📚 Downloading NLTK data..."
python3 - <<'PY'
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
print('✅ NLTK ready')
PY

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh

# Test installation (avoid heavy model load here)
echo "🧪 Testing installation..."
python3 - <<'PY'
from milvus_client import MilvusClient
print('✅ Python deps OK. Milvus client importable.')
PY

echo "✅ Installation completed successfully!"
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   python3 app.py"