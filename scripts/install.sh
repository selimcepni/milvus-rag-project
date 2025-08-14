#!/bin/bash

set -euo pipefail

echo "🔧 Installing Milvus RAG System..."

# Root olarak çalışıyorsa bilgilendir
if [[ $EUID -eq 0 ]]; then
   echo "ℹ️ Script root olarak çalışıyor. Devam ediliyor."
fi

# Update system
echo "📋 Updating system packages..."
sudo apt update

# Install Python and dependencies
echo "🐍 Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Create virtual environment
# Resolve virtual environment path (default: venv)
VENV_PATH=${VENV_PATH:-venv}
echo "🌐 Creating virtual environment at: $VENV_PATH"
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

## Upgrade pip and core build tools
echo "📦 Upgrading pip and build tools..."
python -m pip install --upgrade pip setuptools wheel packaging

# Pre-install grpcio as binary wheel to avoid building from source
echo "🔌 Ensuring grpcio binary wheel is available..."
if ! python -c "import grpc, sys; print(grpc.__version__)" >/dev/null 2>&1; then
  if ! python -m pip install --only-binary=:all: "grpcio>=1.68.0"; then
    echo "⚠️ grpcio wheel not found; installing build deps and retrying..."
    sudo apt install -y pkg-config libc-ares-dev libssl-dev zlib1g-dev || true
    python -m pip install "grpcio>=1.68.0"
  fi
fi

echo "🔌 Preinstalling grpcio binary wheel..."
if ! python -m pip install --only-binary=:all: "grpcio>=1.68.0"; then
  echo "⚠️ grpcio binary wheel not found; installing build deps and retrying..."
  sudo apt install -y pkg-config libc-ares-dev libssl-dev zlib1g-dev || true
  python -m pip install "grpcio>=1.68.0"
fi

echo "📦 Installing Python packages (prefer wheels)..."
python -m pip install --prefer-binary -r requirements.txt

# No NLTK/model downloads needed on server (client does embeddings)

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh

# Test installation (lightweight)
echo "🧪 Testing installation..."
python - <<'PY'
from milvus_client import MilvusClient
print('✅ Python deps OK. Milvus client importable.')
PY

echo "✅ Installation completed successfully!"
echo "🚀 To start the application:"
echo "   source $VENV_PATH/bin/activate"
echo "   python3 app.py"

# Opsiyonel: systemd servisini kur (root ise ve AUTOINSTALL_SYSTEMD=1 veya boş)
if [[ ${AUTOINSTALL_SYSTEMD:-1} -eq 1 && $EUID -eq 0 ]]; then
  echo "⚙️  Systemd servisi kuruluyor..."
  # Varsayılan ortam dosyası oluştur
  cat >/etc/default/milvus-rag <<'ENVEOF'
# Milvus RAG Service Environment
MILVUS_RAG_ROOT=/opt/milvus-rag
MILVUS_RAG_LOG_DIR=/opt/milvus-rag/logs
MILVUS_HOST=localhost
MILVUS_PORT=19530
# Venv python yolu
MILVUS_RAG_PYTHON=/opt/milvus-rag/venv/bin/python
ENVEOF

  # Servis dosyasını kopyala ve etkinleştir
  install -m 0644 systemd/milvus-rag.service /etc/systemd/system/milvus-rag.service
  systemctl daemon-reload
  systemctl enable milvus-rag
  systemctl restart milvus-rag || true
  echo "📝 Loglar: journalctl -u milvus-rag -f"
fi