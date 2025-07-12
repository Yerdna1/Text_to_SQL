#!/usr/bin/env python3
"""
Simple Daytona Sandbox Deployment
Using the Daytona SDK to deploy IBM Sales Pipeline Analytics
"""

import os
import sys

def deploy_with_daytona():
    """Deploy using Daytona SDK"""
    
    print("🚀 Deploying IBM Sales Pipeline Analytics to Daytona Sandbox...")
    
    # Check API key
    api_key = os.environ.get("DAYTONA_API_KEY")
    if not api_key:
        print("❌ Error: DAYTONA_API_KEY not found")
        print("Please set: export DAYTONA_API_KEY='your_api_key'")
        return False
    
    print(f"🔑 Using API Key: {api_key[:20]}...")
    
    try:
        # Import Daytona SDK
        from daytona_sdk import Daytona
        
        print("✅ Daytona SDK imported successfully")
        
        # Initialize client
        client = Daytona(api_key=api_key)
        
        print("🔧 Creating sandbox...")
        
        # Create sandbox
        sandbox = client.create(
            language="python",
            env_vars={
                "BACKEND_PORT": "8000",
                "FRONTEND_PORT": "3000",
                "PYTHONPATH": "/workspace"
            }
        )
        
        print(f"✅ Sandbox created: {sandbox.id}")
        
        # Install dependencies
        print("📦 Installing dependencies...")
        install_script = """
# Update system
apt-get update && apt-get install -y curl nodejs npm

# Install Python packages
pip install fastapi uvicorn pandas numpy openpyxl python-dotenv pydantic httpx python-multipart

# Install Node.js packages
cd /workspace
mkdir -p frontend
cd frontend
npm init -y
npm install next@14.0.0 react@18.2.0 react-dom@18.2.0 axios@1.5.0 tailwindcss@3.3.5

echo "✅ Dependencies installed"
"""
        
        result = sandbox.execute(install_script)
        print(f"Installation result: {result}")
        
        # Upload application files
        print("📁 Uploading application files...")
        
        # Read and upload key files
        files_to_upload = [
            ("backend/main.py", "/workspace/backend/main.py"),
            ("data_dictionary.py", "/workspace/data_dictionary.py"),
            ("database_manager.py", "/workspace/database_manager.py"),
            ("llm_connector.py", "/workspace/llm_connector.py"),
        ]
        
        for local_path, remote_path in files_to_upload:
            if os.path.exists(local_path):
                with open(local_path, 'r') as f:
                    content = f.read()
                try:
                    sandbox.files.write(remote_path, content)
                    print(f"✅ Uploaded {local_path}")
                except Exception as e:
                    print(f"⚠️ Failed to upload {local_path}: {e}")
        
        # Start the application
        print("🚀 Starting application...")
        start_script = """
cd /workspace
export PYTHONPATH=/workspace

# Start backend
nohup python backend/main.py > backend.log 2>&1 &

# Wait a bit
sleep 5

# Check if it's running
ps aux | grep python | grep main.py || echo "Backend may not be running"

echo "🎉 Application should be starting..."
echo "Check logs with: tail -f backend.log"
"""
        
        start_result = sandbox.execute(start_script)
        print(f"Start result: {start_result}")
        
        print("\n🎉 Deployment completed!")
        print(f"   Sandbox ID: {sandbox.id}")
        print("   Backend should be running on port 8000")
        print("   Access via Daytona dashboard")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Trying alternative import...")
        
        try:
            # Try alternative import
            import daytona_sdk
            print("✅ Found daytona_sdk module")
            # Continue with deployment using available methods
            
        except ImportError:
            print("❌ Daytona SDK not properly installed")
            return False
        
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deploy_with_daytona()
    if success:
        print("✅ Deployment successful!")
    else:
        print("❌ Deployment failed!")
        sys.exit(1)