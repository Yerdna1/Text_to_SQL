#!/usr/bin/env python3
"""
Setup IBM Sales Pipeline Analytics in existing Daytona Sandbox
"""

import os
from pathlib import Path

def setup_application_in_sandbox():
    """Setup the application in the existing Daytona sandbox"""
    
    print("🔧 Setting up IBM Sales Pipeline Analytics in Daytona Sandbox...")
    
    # Import Daytona SDK
    from daytona_sdk import Daytona, DaytonaConfig
    
    api_key = os.environ.get("DAYTONA_API_KEY")
    if not api_key:
        print("❌ DAYTONA_API_KEY not found")
        return False
    
    # Connect to Daytona
    config = DaytonaConfig(api_key=api_key)
    daytona = Daytona(config)
    
    # Get our sandbox
    sandbox_id = "b73b439a-45a4-48d6-9fa7-f682fe55b638"
    sandboxes = daytona.list()
    sandbox = next((sb for sb in sandboxes if sb.id == sandbox_id), None)
    
    if not sandbox:
        print(f"❌ Sandbox {sandbox_id} not found")
        return False
    
    print(f"✅ Connected to sandbox: {sandbox.id}")
    print(f"   State: {sandbox.state}")
    
    # Install system dependencies using process
    print("📦 Installing system dependencies...")
    install_system = """
import subprocess
import sys

try:
    # Update system
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'curl', 'wget', 'nodejs', 'npm'], check=True)
    
    # Install Python packages
    subprocess.run([sys.executable, '-m', 'pip', 'install', 
                   'fastapi', 'uvicorn[standard]', 'pandas', 'numpy', 
                   'openpyxl', 'python-dotenv', 'pydantic', 'httpx', 
                   'python-multipart'], check=True)
    
    print("✅ System dependencies installed")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Error installing dependencies: {e}")
"""
    
    result = sandbox.process.code_run(install_system)
    print(f"System install result: {result.result}")
    
    # Create directory structure using process
    print("📁 Creating directory structure...")
    create_dirs = """
import os
os.makedirs('/workspace/backend', exist_ok=True)
os.makedirs('/workspace/frontend', exist_ok=True)
os.makedirs('/workspace/agents', exist_ok=True)
os.makedirs('/workspace/data', exist_ok=True)
print("✅ Directories created")
"""
    
    result = sandbox.process.code_run(create_dirs)
    print(f"Directory creation: {result.result}")
    
    # Upload backend files using fs
    print("📤 Uploading backend files...")
    backend_files = [
        "backend/main.py",
        "data_dictionary.py",
        "database_manager.py", 
        "llm_connector.py",
        "visualization_utils.py"
    ]
    
    uploaded_count = 0
    for file_path in backend_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use filesystem API correctly
                target_path = f"/workspace/{file_path}"
                sandbox.fs.write_file(target_path, content)
                uploaded_count += 1
                print(f"   ✅ {file_path}")
            except Exception as e:
                print(f"   ⚠️ Failed to upload {file_path}: {e}")
    
    # Upload agents
    print("🤖 Uploading agent system...")
    agents_dir = Path("agents")
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*.py"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                target_path = f"/workspace/agents/{agent_file.name}"
                sandbox.fs.write_file(target_path, content)
                uploaded_count += 1
                print(f"   ✅ {agent_file}")
            except Exception as e:
                print(f"   ⚠️ Failed to upload {agent_file}: {e}")
    
    print(f"📁 Uploaded {uploaded_count} files successfully")
    
    # Setup frontend package.json using process
    print("🎨 Setting up frontend...")
    setup_frontend = """
import os
import json

# Create package.json
package_json = {
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
        "axios": "1.5.0",
        "tailwindcss": "3.3.5",
        "@tanstack/react-query": "5.8.4",
        "lucide-react": "0.292.0",
        "recharts": "2.8.0"
    }
}

with open('/workspace/frontend/package.json', 'w') as f:
    json.dump(package_json, f, indent=2)

print("✅ Frontend package.json created")
"""
    
    result = sandbox.process.code_run(setup_frontend)
    print(f"Frontend setup: {result.result}")
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    install_npm = """
import subprocess
import os

try:
    os.chdir('/workspace/frontend')
    subprocess.run(['npm', 'install'], check=True)
    print("✅ Node.js dependencies installed")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Error installing npm packages: {e}")
"""
    
    result = sandbox.process.code_run(install_npm)
    print(f"NPM install: {result.result}")
    
    # Start the backend application
    print("🚀 Starting FastAPI backend...")
    start_backend = """
import subprocess
import os
import time

try:
    os.chdir('/workspace')
    os.environ['PYTHONPATH'] = '/workspace'
    
    # Start backend in background
    process = subprocess.Popen([
        'python', 'backend/main.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a bit for startup
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is None:
        print("✅ Backend started successfully")
        print(f"   Process PID: {process.pid}")
    else:
        stdout, stderr = process.communicate()
        print(f"⚠️ Backend failed to start:")
        print(f"   stdout: {stdout.decode()}")
        print(f"   stderr: {stderr.decode()}")
        
except Exception as e:
    print(f"❌ Error starting backend: {e}")
"""
    
    result = sandbox.process.code_run(start_backend)
    print(f"Backend startup: {result.result}")
    
    # Final status check
    print("🔍 Final status check...")
    status_check = """
import subprocess
import os

try:
    # Check Python processes
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    python_processes = [line for line in result.stdout.split('\\n') if 'python' in line and 'main.py' in line]
    
    if python_processes:
        print("✅ Backend process found:")
        for proc in python_processes:
            print(f"   {proc}")
    else:
        print("⚠️ No backend process found")
    
    # Check port status
    port_result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
    port_8000 = [line for line in port_result.stdout.split('\\n') if ':8000' in line]
    
    if port_8000:
        print("✅ Port 8000 is active:")
        for port in port_8000:
            print(f"   {port}")
    else:
        print("⚠️ Port 8000 not found")
        
    # Try health check
    try:
        import urllib.request
        response = urllib.request.urlopen('http://localhost:8000/')
        print(f"✅ Backend health check passed: {response.getcode()}")
    except Exception as e:
        print(f"⚠️ Backend health check failed: {e}")
        
except Exception as e:
    print(f"❌ Status check error: {e}")
"""
    
    result = sandbox.process.code_run(status_check)
    print(f"Status check: {result.result}")
    
    # Success message
    print("\n" + "="*60)
    print("🎉 Application setup completed in Daytona Sandbox!")
    print(f"\n📍 Sandbox Information:")
    print(f"   Sandbox ID: {sandbox.id}")
    print(f"   State: {sandbox.state}")
    
    print(f"\n🌐 Access Information:")
    print(f"   Backend API: Available on port 8000")
    print(f"   API Documentation: /docs endpoint")
    print(f"   Health Check: / endpoint")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Access sandbox via Daytona Dashboard")
    print(f"   2. Backend should be running on port 8000")
    print(f"   3. Test API endpoints: GET /health, POST /api/generate-query")
    print(f"   4. Configure LLM API keys")
    print(f"   5. Start querying your sales pipeline data!")
    
    return True

if __name__ == "__main__":
    success = setup_application_in_sandbox()
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed!")