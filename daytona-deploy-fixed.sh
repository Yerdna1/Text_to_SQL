#!/bin/bash

# IBM Sales Pipeline Analytics - Daytona Deployment Script

set -e

echo "🚀 Deploying IBM Sales Pipeline Analytics to Daytona..."

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Loaded environment variables from .env"
fi

# Check if Daytona API key is set
if [ -z "$DAYTONA_API_KEY" ]; then
    echo "❌ Error: DAYTONA_API_KEY not set. Please check your .env file."
    exit 1
fi

echo "🔑 Using Daytona API Key: ${DAYTONA_API_KEY:0:20}..."

# Check if daytona CLI is installed
if ! command -v daytona &> /dev/null; then
    echo "📦 Installing Daytona CLI..."
    
    # Install Daytona CLI
    curl -sf -L https://download.daytona.io/daytona/install.sh | sh
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.daytona/bin:"* ]]; then
        export PATH="$HOME/.daytona/bin:$PATH"
        echo 'export PATH="$HOME/.daytona/bin:$PATH"' >> ~/.bashrc
    fi
    
    echo "✅ Daytona CLI installed"
else
    echo "✅ Daytona CLI already installed"
fi

# Configure Daytona with API key
echo "🔧 Configuring Daytona..."
daytona profile add --api-key "$DAYTONA_API_KEY" --name ibm-analytics || true

# Create Daytona workspace
echo "🏗️ Creating Daytona workspace..."
WORKSPACE_NAME="ibm-pipeline-analytics-$(date +%Y%m%d-%H%M%S)"

# Create workspace configuration
cat > daytona-workspace.yaml << EOF
name: $WORKSPACE_NAME
image: ubuntu:22.04
projects:
  - name: ibm-analytics
    source:
      type: git
      url: .
    ide:
      type: vscode
    env:
      BACKEND_PORT: 8000
      FRONTEND_PORT: 3000
    ports:
      - 3000
      - 8000
EOF

echo "📋 Workspace configuration created"

# Deploy to Daytona
echo "🚀 Deploying to Daytona..."
daytona workspace create --config daytona-workspace.yaml

# Wait for workspace to be ready
echo "⏳ Waiting for workspace to be ready..."
sleep 30

# Get workspace info
echo "📊 Getting workspace information..."
WORKSPACE_URL=$(daytona workspace list --format json | jq -r '.[] | select(.name=="'$WORKSPACE_NAME'") | .url')

if [ -n "$WORKSPACE_URL" ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📍 Workspace Details:"
    echo "   Name: $WORKSPACE_NAME"
    echo "   URL: $WORKSPACE_URL"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Open the workspace in your browser: $WORKSPACE_URL"
    echo "   2. Wait for the environment to load"
    echo "   3. Open a terminal and run: ./deploy.sh"
    echo "   4. Access the application at the provided URLs"
    echo ""
    echo "📱 Application will be available at:"
    echo "   Frontend: $WORKSPACE_URL:3000"
    echo "   API: $WORKSPACE_URL:8000"
    echo ""
else
    echo "❌ Failed to get workspace URL. Check Daytona dashboard manually."
fi

# Open browser to workspace (if possible)
if command -v open &> /dev/null && [ -n "$WORKSPACE_URL" ]; then
    echo "🌐 Opening workspace in browser..."
    open "$WORKSPACE_URL"
elif command -v xdg-open &> /dev/null && [ -n "$WORKSPACE_URL" ]; then
    echo "🌐 Opening workspace in browser..."
    xdg-open "$WORKSPACE_URL"
fi

echo ""
echo "📋 Management commands:"
echo "   - List workspaces: daytona workspace list"
echo "   - Connect to workspace: daytona workspace connect $WORKSPACE_NAME"
echo "   - Delete workspace: daytona workspace delete $WORKSPACE_NAME"
echo ""
echo "🎯 Remember to configure your LLM API keys in the application UI!"
echo ""