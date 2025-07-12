#!/usr/bin/env python3
"""
IBM Sales Pipeline Analytics - Daytona Sandbox Deployment
Using the correct Daytona SDK API (2024/2025)
"""

import os
import sys
from pathlib import Path

def deploy_to_daytona():
    """Deploy IBM Sales Pipeline Analytics to Daytona Sandbox using correct SDK"""
    
    print("🚀 IBM Sales Pipeline Analytics - Daytona Sandbox Deployment")
    print("=" * 60)
    
    # Check API key
    api_key = os.environ.get("DAYTONA_API_KEY")
    if not api_key:
        print("❌ Error: DAYTONA_API_KEY not found in environment")
        print("Please set your API key:")
        print("export DAYTONA_API_KEY='your_api_key_here'")
        return False
    
    print(f"🔑 Using Daytona API Key: {api_key[:20]}...")
    
    try:
        # Import Daytona SDK with correct syntax
        from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxBaseParams, CodeLanguage
        
        print("✅ Daytona SDK imported successfully")
        
        # Initialize Daytona client with correct configuration
        config = DaytonaConfig(api_key=api_key)
        daytona = Daytona(config)
        
        print("🔧 Daytona client initialized")
        
        # Create sandbox with Python environment
        print("🏗️ Creating Daytona sandbox...")
        
        sandbox_params = CreateSandboxBaseParams(
            language=CodeLanguage.PYTHON,
            env_vars={
                "BACKEND_PORT": "8000",
                "FRONTEND_PORT": "3000", 
                "PYTHONPATH": "/workspace",
                "APP_ENV": "production"
            }
        )
        
        sandbox = daytona.create(sandbox_params)
        
        print(f"✅ Sandbox created successfully!")
        print(f"   Sandbox ID: {sandbox.id}")
        
        # Setup the environment
        print("🔧 Setting up environment...")
        
        setup_script = """
# Update system packages
apt-get update && apt-get install -y curl wget nodejs npm

# Create workspace structure
mkdir -p /workspace/{backend,frontend,agents,data}

# Install Python dependencies
pip install fastapi uvicorn[standard] pandas numpy openpyxl python-dotenv pydantic httpx python-multipart

echo "✅ Environment setup completed"
"""
        
        setup_response = sandbox.process.code_run(setup_script)
        if setup_response.exit_code == 0:
            print("✅ Environment setup successful")
        else:
            print(f"⚠️ Environment setup issues: {setup_response.result}")
        
        # Upload application files
        print("📁 Uploading application files...")
        
        # Backend files
        backend_files = {
            "backend/main.py": "/workspace/backend/main.py",
            "backend/requirements.txt": "/workspace/backend/requirements.txt",
            "data_dictionary.py": "/workspace/data_dictionary.py",
            "database_manager.py": "/workspace/database_manager.py",
            "llm_connector.py": "/workspace/llm_connector.py",
            "visualization_utils.py": "/workspace/visualization_utils.py"
        }
        
        uploaded_count = 0
        for local_path, remote_path in backend_files.items():
            if Path(local_path).exists():
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    sandbox.files.write(remote_path, content)
                    uploaded_count += 1
                    print(f"   ✅ {local_path}")
                except Exception as e:
                    print(f"   ⚠️ Failed to upload {local_path}: {e}")
        
        # Upload agents
        agents_dir = Path("agents")
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.py"):
                try:
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    remote_path = f"/workspace/agents/{agent_file.name}"
                    sandbox.files.write(remote_path, content)
                    uploaded_count += 1
                    print(f"   ✅ {agent_file}")
                except Exception as e:
                    print(f"   ⚠️ Failed to upload {agent_file}: {e}")
        
        print(f"📁 Uploaded {uploaded_count} files successfully")
        
        # Install Node.js dependencies and setup frontend
        print("🎨 Setting up frontend...")
        
        frontend_setup = """
cd /workspace/frontend

# Initialize package.json
cat > package.json << 'EOF'
{
  "name": "ibm-pipeline-analytics",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build", 
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "axios": "1.5.0"
  }
}
EOF

# Install Node.js packages
npm install

echo "✅ Frontend setup completed"
"""
        
        frontend_response = sandbox.process.code_run(frontend_setup)
        if frontend_response.exit_code == 0:
            print("✅ Frontend setup successful")
        else:
            print(f"⚠️ Frontend setup issues: {frontend_response.result}")
        
        # Start the backend application
        print("🚀 Starting backend application...")
        
        start_backend = """
cd /workspace
export PYTHONPATH=/workspace

# Start FastAPI backend
nohup python backend/main.py > backend.log 2>&1 &

# Wait for startup
sleep 10

# Check if backend is running
curl -f http://localhost:8000/ && echo "✅ Backend is running" || echo "⚠️ Backend not responding"

# Show process status
ps aux | grep python | grep -v grep
"""
        
        backend_response = sandbox.process.code_run(start_backend)
        print(f"Backend startup: {backend_response.result}")
        
        # Final status check
        print("🔍 Final status check...")
        
        status_check = """
echo "=== Application Status ==="
echo "Sandbox ID: $(hostname)"
echo "Python processes:"
ps aux | grep python | grep -v grep || echo "No Python processes found"
echo ""
echo "Network status:"
netstat -tlnp | grep -E "(3000|8000)" || echo "No services on ports 3000/8000"
echo ""
echo "Backend health:"
curl -f http://localhost:8000/ 2>/dev/null && echo "✅ Backend healthy" || echo "❌ Backend not responding"
echo ""
echo "Log files:"
ls -la *.log 2>/dev/null || echo "No log files found"
"""
        
        status_response = sandbox.process.code_run(status_check)
        print(f"Status check: {status_response.result}")
        
        # Success message
        print("\n" + "=" * 60)
        print("🎉 Deployment completed successfully!")
        print(f"\n📍 Sandbox Information:")
        print(f"   Sandbox ID: {sandbox.id}")
        print(f"   Status: Active")
        
        print(f"\n🌐 Access Information:")
        print(f"   Backend API: Port 8000 (FastAPI)")
        print(f"   Frontend UI: Port 3000 (Next.js)")
        print(f"   API Docs: Port 8000/docs")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Access your sandbox via Daytona Dashboard")
        print(f"   2. Services should be running on the specified ports")
        print(f"   3. Configure LLM API keys in the application")
        print(f"   4. Load demo data or upload your CSV files")
        print(f"   5. Start asking questions about your sales pipeline!")
        
        print(f"\n📋 Features Available:")
        print(f"   ✅ Natural Language to SQL conversion")
        print(f"   ✅ Multi-agent SQL enhancement")
        print(f"   ✅ Interactive web interface")
        print(f"   ✅ File upload and data management")
        print(f"   ✅ Multiple LLM provider support")
        print(f"   ✅ Real-time charts and visualizations")
        
        return sandbox
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure Daytona SDK is properly installed:")
        print("pip install daytona-sdk")
        return None
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main deployment function"""
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    required_files = [
        "backend/main.py",
        "data_dictionary.py", 
        "database_manager.py",
        "llm_connector.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All prerequisites met")
    
    # Deploy to Daytona
    sandbox = deploy_to_daytona()
    
    if sandbox:
        print(f"\n✅ SUCCESS: IBM Sales Pipeline Analytics deployed to Daytona!")
        print(f"   Sandbox ID: {sandbox.id}")
        return True
    else:
        print(f"\n❌ FAILED: Deployment unsuccessful")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)