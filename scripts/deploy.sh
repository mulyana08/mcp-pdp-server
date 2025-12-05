#!/bin/bash
# Deploy script for MCP PDP Server
# Run this on the server to manually deploy

set -e

DEPLOY_PATH="${DEPLOY_PATH:-/home/devjc/mcp-pdp-server}"
IMAGE_NAME="ghcr.io/mulyana08/latihan_mcp:latest"

echo "🚀 Deploying MCP PDP Server..."

# Create deploy directory
mkdir -p $DEPLOY_PATH
cd $DEPLOY_PATH

# Pull latest image
echo "📦 Pulling latest Docker image..."
docker pull $IMAGE_NAME

# Stop existing container
echo "🛑 Stopping existing container..."
docker stop mcp-pdp-server 2>/dev/null || true
docker rm mcp-pdp-server 2>/dev/null || true

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << 'EOF'
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=uu-pdp-27-2022
EOF
    echo "❌ Please edit .env file with actual values and run again"
    exit 1
fi

# Start container with docker-compose
echo "🐳 Starting container..."
if [ -f docker-compose.yml ]; then
    docker-compose up -d
else
    # Fallback to docker run
    source .env
    docker run -d \
        --name mcp-pdp-server \
        --restart unless-stopped \
        -p 8000:8000 \
        -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
        -e PINECONE_API_KEY="$PINECONE_API_KEY" \
        -e PINECONE_INDEX_NAME="$PINECONE_INDEX_NAME" \
        $IMAGE_NAME
fi

# Wait and verify
sleep 5
if docker ps | grep -q mcp-pdp-server; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📋 Container status:"
    docker ps --filter name=mcp-pdp-server
else
    echo "❌ Deployment failed!"
    echo "📋 Container logs:"
    docker logs mcp-pdp-server
    exit 1
fi
