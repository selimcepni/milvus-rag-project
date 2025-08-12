#!/bin/bash

# Milvus RAG Project - Ubuntu Setup Script for v2.6.0
# Bu script projeyi Ubuntu'da Milvus v2.6.0 ile uyumlu hale getirir

echo "🚀 Milvus RAG Project v2.6.0 Setup Starting..."

# Python sürümünü kontrol et
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version is compatible with Milvus v2.6.0"
else
    echo "❌ Python $python_version is not compatible. Python 3.7+ required."
    exit 1
fi

# Sistem paketlerini güncelle
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Gerekli sistem paketlerini yükle
echo "📦 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev build-essential

# Virtual environment oluştur
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Virtual environment'ı aktifleştir
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Pip'i güncelle
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Milvus v2.6.0 uyumlu gereksinimleri yükle
echo "📦 Installing Milvus v2.6.0 compatible requirements..."
pip install -r requirements.txt

# Log dizinini oluştur
echo "📁 Creating log directory..."
sudo mkdir -p /opt/milvus-rag/logs
sudo chown -R $USER:$USER /opt/milvus-rag

# Milvus Docker container'ının çalıştığını kontrol et
echo "🔍 Checking Milvus Docker container..."
if docker ps | grep -q milvus; then
    echo "✅ Milvus container is running"
else
    echo "⚠️  Milvus container not found. Please start Milvus v2.6.0 with Docker:"
    echo "   docker run -d --name milvus -p 19530:19530 -p 9091:9091 milvusdb/milvus:v2.6.0-standalone"
fi

# Bağlantı testini çalıştır
echo "🧪 Testing Milvus connection..."
python3 -c "
try:
    from milvus_client import MilvusClient
    client = MilvusClient()
    health = client.health_check()
    if health['status'] == 'healthy':
        print('✅ Milvus v2.6.0 connection successful!')
        print(f'   Server version: {health.get(\"server_version\", \"Unknown\")}')
    else:
        print('❌ Milvus connection failed:', health.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Connection test failed:', str(e))
    print('   Make sure Milvus v2.6.0 is running on localhost:19530')
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Start the application: python3 app.py"
echo "   3. Test the API: curl http://localhost:5000/health"
echo ""
echo "🐳 If Milvus is not running, start it with:"
echo "   docker run -d --name milvus -p 19530:19530 -p 9091:9091 milvusdb/milvus:v2.6.0-standalone"
