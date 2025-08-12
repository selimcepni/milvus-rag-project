#!/bin/bash

# 🚀 Deployment script for Milvus RAG System
# Usage: ./deploy.sh [server-ip] [username]

SERVER_HOST=${1:-"your-server-ip"}
SERVER_USER=${2:-"ubuntu"}
PROJECT_PATH="/opt/milvus-rag"

if [ "$SERVER_HOST" = "your-server-ip" ]; then
    echo "❌ Please provide server IP address"
    echo "Usage: ./deploy.sh [server-ip] [username]"
    echo "Example: ./deploy.sh 192.168.1.100 ubuntu"
    exit 1
fi

echo "🚀 Deploying Milvus RAG System to $SERVER_USER@$SERVER_HOST..."

# Test SSH connection
echo "🔐 Testing SSH connection..."
if ! ssh -o ConnectTimeout=10 $SERVER_USER@$SERVER_HOST "echo 'SSH connection successful'"; then
    echo "❌ SSH connection failed. Please check your connection and try again."
    exit 1
fi

# 1. Create project directory on server
echo "📁 Creating project directory on server..."
ssh $SERVER_USER@$SERVER_HOST "sudo mkdir -p $PROJECT_PATH && sudo chown $SERVER_USER:$SERVER_USER $PROJECT_PATH"

# 2. Copy files to server (excluding unnecessary files)
echo "📤 Copying project files to server..."
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='logs' \
    . $SERVER_USER@$SERVER_HOST:$PROJECT_PATH/

# 3. Install dependencies on server
echo "📦 Installing dependencies on server..."
ssh $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && chmod +x scripts/*.sh && ./scripts/install.sh"

# 4. Setup systemd service
echo "⚙️ Setting up systemd service..."
ssh $SERVER_USER@$SERVER_HOST "sudo cp $PROJECT_PATH/systemd/milvus-rag.service /etc/systemd/system/ && sudo systemctl daemon-reload"

# 5. Enable and start service
echo "🔄 Starting service..."
ssh $SERVER_USER@$SERVER_HOST "sudo systemctl enable milvus-rag && sudo systemctl restart milvus-rag"

# 6. Wait a moment for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# 7. Check service status
echo "✅ Checking service status..."
ssh $SERVER_USER@$SERVER_HOST "sudo systemctl status milvus-rag --no-pager"

# 8. Test API endpoint
echo "🧪 Testing API endpoint..."
if ssh $SERVER_USER@$SERVER_HOST "curl -s http://localhost:5000/health" > /dev/null; then
    echo "✅ API is responding"
else
    echo "⚠️ API might not be ready yet. Check logs with: sudo journalctl -u milvus-rag -f"
fi

echo ""
echo "🎉 Deployment completed!"
echo "📊 Health check: curl http://$SERVER_HOST:5000/health"
echo "📝 View logs: ssh $SERVER_USER@$SERVER_HOST 'sudo journalctl -u milvus-rag -f'"
echo "🔄 Restart service: ssh $SERVER_USER@$SERVER_HOST 'sudo systemctl restart milvus-rag'"