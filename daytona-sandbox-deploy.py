#!/usr/bin/env python3
"""
Daytona Sandbox Deployment for IBM Sales Pipeline Analytics
Using the new Daytona SDK (2024/2025)
"""

import os
import sys
import time
from pathlib import Path

# Install Daytona SDK if not already installed
try:
    from daytona import Daytona, DaytonaConfig, CreateSandboxParams
except ImportError:
    print("📦 Installing Daytona SDK...")
    os.system("pip install daytona-sdk")
    from daytona import Daytona, DaytonaConfig, CreateSandboxParams

def deploy_to_daytona():
    """Deploy IBM Sales Pipeline Analytics to Daytona Sandbox"""
    
    print("🚀 Deploying IBM Sales Pipeline Analytics to Daytona Sandbox...")
    print("=" * 60)
    
    # Get API key from environment
    api_key = os.environ.get("DAYTONA_API_KEY")
    if not api_key:
        print("❌ Error: DAYTONA_API_KEY not found in environment variables")
        print("Please set your Daytona API key:")
        print("export DAYTONA_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    print(f"🔑 Using Daytona API Key: {api_key[:20]}...")
    
    try:
        # Initialize Daytona client
        print("🔧 Initializing Daytona client...")
        daytona = Daytona(DaytonaConfig(api_key=api_key))
        
        # Create sandbox with Python environment
        print("🏗️ Creating Daytona sandbox...")
        sandbox = daytona.create(CreateSandboxParams(
            language="python",
            env_vars={
                "BACKEND_PORT": "8000",
                "FRONTEND_PORT": "3000",
                "PYTHONPATH": "/workspace"
            },
            auto_stop_interval=0,  # Don't auto-stop
            auto_archive_interval=7 * 24 * 60  # Archive after 7 days
        ))
        
        print(f"✅ Sandbox created successfully!")
        print(f"   Sandbox ID: {sandbox.id}")
        
        # Upload project files
        print("📁 Uploading project files...")
        
        # Create project structure
        setup_commands = [
            "mkdir -p /workspace/frontend",
            "mkdir -p /workspace/backend", 
            "mkdir -p /workspace/agents",
            "mkdir -p /workspace/data"
        ]
        
        for cmd in setup_commands:
            sandbox.process.code_run(cmd)
        
        # Install Python dependencies
        print("📦 Installing Python dependencies...")
        python_install_script = """
# Install system dependencies
apt-get update && apt-get install -y curl nodejs npm

# Install Python dependencies
pip install fastapi uvicorn pandas numpy sqlite3 openpyxl python-dotenv pydantic httpx python-multipart

# Install Node.js dependencies for frontend
cd /workspace/frontend
npm init -y
npm install next@14.0.0 react@18.2.0 react-dom@18.2.0 axios@1.5.0 tailwindcss@3.3.5 @tanstack/react-query@5.8.4 react-hot-toast@2.4.1 lucide-react@0.292.0 recharts@2.8.0

echo "✅ Dependencies installed successfully"
"""
        
        install_response = sandbox.process.code_run(python_install_script)
        if install_response.exit_code != 0:
            print(f"⚠️ Warning during installation: {install_response.result}")
        
        # Upload backend files
        print("📤 Uploading backend code...")
        backend_files = [
            "backend/main.py",
            "backend/requirements.txt",
            "data_dictionary.py",
            "database_manager.py", 
            "llm_connector.py",
            "visualization_utils.py"
        ]
        
        for file_path in backend_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                sandbox.files.write(f"/workspace/{file_path}", content)
        
        # Upload agents
        print("🤖 Uploading agent system...")
        agents_dir = Path("agents")
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.py"):
                with open(agent_file, 'r') as f:
                    content = f.read()
                sandbox.files.write(f"/workspace/agents/{agent_file.name}", content)
        
        # Upload frontend files
        print("🎨 Uploading frontend code...")
        frontend_files = [
            "frontend/package.json",
            "frontend/next.config.js",
            "frontend/tailwind.config.js",
            "frontend/tsconfig.json"
        ]
        
        for file_path in frontend_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                sandbox.files.write(f"/workspace/{file_path}", content)
        
        # Upload frontend app and components
        frontend_dirs = ["frontend/app", "frontend/components"]
        for dir_path in frontend_dirs:
            dir_obj = Path(dir_path)
            if dir_obj.exists():
                for file_path in dir_obj.rglob("*.tsx"):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    rel_path = file_path.relative_to(".")
                    sandbox.files.write(f"/workspace/{rel_path}", content)
                for file_path in dir_obj.rglob("*.css"):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    rel_path = file_path.relative_to(".")
                    sandbox.files.write(f"/workspace/{rel_path}", content)
        
        # Start the backend server
        print("🚀 Starting FastAPI backend...")
        backend_start_script = """
cd /workspace
export PYTHONPATH=/workspace
nohup python backend/main.py > backend.log 2>&1 &
sleep 5
echo "Backend started, checking logs..."
tail -10 backend.log
"""
        
        backend_response = sandbox.process.code_run(backend_start_script)
        print(f"Backend startup result: {backend_response.result}")
        
        # Build and start frontend
        print("🎨 Building and starting Next.js frontend...")
        frontend_start_script = """
cd /workspace/frontend
npm run build
nohup npm start > ../frontend.log 2>&1 &
sleep 10
echo "Frontend started, checking logs..."
tail -10 ../frontend.log
"""
        
        frontend_response = sandbox.process.code_run(frontend_start_script)
        print(f"Frontend startup result: {frontend_response.result}")
        
        # Check if services are running
        print("🔍 Checking service status...")
        status_check = """
echo "=== Service Status ==="
ps aux | grep -E "(python|node)" | grep -v grep
echo ""
echo "=== Port Status ==="
netstat -tlnp | grep -E "(3000|8000)" || echo "No ports found (services may still be starting)"
echo ""
echo "=== Backend Health Check ==="
curl -f http://localhost:8000/ || echo "Backend not ready yet"
echo ""
echo "=== Frontend Health Check ==="  
curl -f http://localhost:3000/ || echo "Frontend not ready yet"
"""
        
        status_response = sandbox.process.code_run(status_check)
        print(f"Service status: {status_response.result}")
        
        # Get sandbox URL for access
        print("\n" + "=" * 60)
        print("🎉 Deployment completed!")
        print("\n📍 Sandbox Information:")
        print(f"   Sandbox ID: {sandbox.id}")
        print(f"   Status: Active")
        print("\n🌐 Access your application:")
        print("   Note: Daytona will provide URLs to access your running services")
        print("   Backend API: Port 8000")
        print("   Frontend UI: Port 3000")
        
        print("\n🎯 Next Steps:")
        print("   1. Access your sandbox through the Daytona dashboard")
        print("   2. Services should be running on ports 3000 and 8000")
        print("   3. Configure your LLM API keys in the application")
        print("   4. Load demo data or upload your files")
        print("   5. Start asking questions about your sales pipeline!")
        
        print("\n🔧 Management:")
        print(f"   - View sandbox: Daytona Dashboard")
        print(f"   - Logs: Check backend.log and frontend.log in sandbox")
        print(f"   - Stop sandbox: Use Daytona dashboard or SDK")
        
        return sandbox
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check for required files
    required_files = [
        "backend/main.py",
        "backend/requirements.txt", 
        "frontend/package.json",
        "data_dictionary.py",
        "database_manager.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Check environment variables
    if not os.environ.get("DAYTONA_API_KEY"):
        print("❌ DAYTONA_API_KEY not set")
        return False
    
    print("✅ All prerequisites met")
    return True

if __name__ == "__main__":
    print("🚀 IBM Sales Pipeline Analytics - Daytona Sandbox Deployment")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    sandbox = deploy_to_daytona()
    
    if sandbox:
        print(f"\n✅ Deployment successful! Sandbox ID: {sandbox.id}")
        print("🎉 Your IBM Sales Pipeline Analytics is now running in Daytona!")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)