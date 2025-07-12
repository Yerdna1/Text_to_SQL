#!/bin/bash

# IBM Sales Pipeline Analytics - Daytona Deployment Script

set -e

echo "🚀 Deploying IBM Sales Pipeline Analytics to Daytona..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

# Build and start the application
echo "📦 Building Docker containers..."
docker-compose build --no-cache

echo "🔧 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check backend health
echo "🔍 Checking backend health..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    echo "⏳ Backend not ready yet... (attempt $((retry_count + 1))/$max_retries)"
    sleep 2
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Backend failed to start properly"
    docker-compose logs backend
    exit 1
fi

# Check frontend health
echo "🔍 Checking frontend health..."
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        echo "✅ Frontend is healthy!"
        break
    fi
    echo "⏳ Frontend not ready yet... (attempt $((retry_count + 1))/$max_retries)"
    sleep 2
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Frontend failed to start properly"
    docker-compose logs frontend
    exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "📊 IBM Sales Pipeline Analytics is now running:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Go to 'Data Setup' tab and load demo data or upload your files"
echo "   3. Go to 'LLM Setup' tab and configure your preferred AI provider"
echo "   4. Start asking questions in the 'Query Interface' tab!"
echo ""
echo "🔧 Management commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop: docker-compose down"
echo "   - Restart: docker-compose restart"
echo ""