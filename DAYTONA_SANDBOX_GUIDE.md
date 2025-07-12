# 🚀 Daytona Sandbox Deployment Guide

## Updated Daytona (2024/2025) - Sandboxes

Based on the latest Daytona documentation, here's how to deploy your IBM Sales Pipeline Analytics application using the new **Daytona Sandboxes** infrastructure.

## 📋 What is Daytona Sandboxes?

Daytona has evolved into a **Secure and Elastic Infrastructure for Running AI-Generated Code** with:

- ✅ **Sub 90ms sandbox creation** from code to execution
- ✅ **Isolated environments** with 1 vCPU, 1GB RAM, 3GiB disk (customizable)
- ✅ **Multi-region support** (North America, Europe, Asia)
- ✅ **Auto-stop after 15 minutes** of inactivity (configurable)
- ✅ **Auto-archive after 7 days** (configurable)
- ✅ **ISO 27001, SOC 2, GDPR compliant**

## 🔑 Get Your API Key

1. Go to the **Daytona Dashboard**: https://www.daytona.io/
2. Create an account or sign in
3. Generate a new **API key**
4. Save it securely (it won't be shown again)

## 🚀 Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# Set your API key
export DAYTONA_API_KEY="your_api_key_here"

# Run the deployment script
python daytona-sandbox-deploy.py
```

### Option 2: Manual SDK Setup

```bash
# Install Daytona SDK
pip install daytona-sdk

# Use the Python script
python3 -c "
import os
from daytona import Daytona, DaytonaConfig, CreateSandboxParams

# Initialize client
daytona = Daytona(DaytonaConfig(api_key=os.environ['DAYTONA_API_KEY']))

# Create sandbox
sandbox = daytona.create(CreateSandboxParams(
    language='python',
    env_vars={
        'BACKEND_PORT': '8000',
        'FRONTEND_PORT': '3000'
    }
))

print(f'Sandbox created: {sandbox.id}')
"
```

## 📊 What Gets Deployed

Your deployment includes:

### Backend (Port 8000)
- ✅ FastAPI server with all endpoints
- ✅ Multi-agent SQL system
- ✅ Database manager with SQLite
- ✅ LLM connectors (Gemini, DeepSeek, OpenAI, etc.)
- ✅ File upload and data management

### Frontend (Port 3000)  
- ✅ Next.js React application
- ✅ Modern UI components
- ✅ Interactive query interface
- ✅ Data setup and LLM configuration
- ✅ Real-time charts and tables

### Features
- ✅ Natural Language to SQL conversion
- ✅ Multi-agent enhancement system  
- ✅ Demo data loading
- ✅ File upload (CSV/Excel)
- ✅ Multiple LLM provider support
- ✅ Mobile-responsive design

## 🔧 Configuration Options

### Custom Resources
```python
from daytona import CreateSandboxParams, Resources

sandbox = daytona.create(CreateSandboxParams(
    language="python",
    resources=Resources(
        cpu=2,           # 2 vCPUs
        memory=4096,     # 4GB RAM  
        disk=10240       # 10GB disk
    )
))
```

### Environment Variables
```python
sandbox = daytona.create(CreateSandboxParams(
    language="python",
    env_vars={
        "GEMINI_API_KEY": "your_gemini_key",
        "DEEPSEEK_API_KEY": "your_deepseek_key", 
        "BACKEND_PORT": "8000",
        "FRONTEND_PORT": "3000"
    }
))
```

### Auto-Stop Configuration
```python
sandbox = daytona.create(CreateSandboxParams(
    language="python",
    auto_stop_interval=60,      # Stop after 1 hour of inactivity
    auto_archive_interval=1440  # Archive after 24 hours of being stopped
))
```

## 🌍 Multi-Region Deployment

Choose your preferred region for optimal performance:

```python
sandbox = daytona.create(CreateSandboxParams(
    language="python",
    region="us-east-1"  # or "eu-west-1", "ap-southeast-1"
))
```

## 📱 Access Your Application

After deployment:

1. **Sandbox URL**: Provided by Daytona dashboard
2. **Frontend**: `{sandbox_url}:3000`
3. **Backend API**: `{sandbox_url}:8000`
4. **API Documentation**: `{sandbox_url}:8000/docs`

## 🔍 Monitoring and Management

### Check Status
```python
# List all sandboxes
sandboxes = daytona.list()

# Get sandbox info
sandbox_info = daytona.get(sandbox_id)
```

### Execute Commands
```python
# Run commands in sandbox
response = sandbox.process.code_run("ps aux | grep python")
print(response.result)
```

### File Operations
```python
# Upload files
sandbox.files.write("/path/to/file.py", file_content)

# Download files
content = sandbox.files.read("/path/to/file.py")
```

## 🛠️ Troubleshooting

### Common Issues

**API Key Issues:**
```bash
export DAYTONA_API_KEY="your_actual_api_key"
```

**SDK Installation:**
```bash
pip install --upgrade daytona-sdk
```

**Port Access:**
- Ensure services are running on ports 3000 and 8000
- Check firewall settings in sandbox

### Debug Commands
```python
# Check service status
response = sandbox.process.code_run("netstat -tlnp | grep -E '(3000|8000)'")
print(response.result)

# Check logs
backend_logs = sandbox.files.read("/workspace/backend.log")
frontend_logs = sandbox.files.read("/workspace/frontend.log")
```

## 💰 Pricing and Limits

- **Default**: 1 vCPU, 1GB RAM, 3GiB disk
- **Auto-stop**: 15 minutes (saves costs)
- **Scaling**: Pay for what you use
- **Regions**: Multiple options for global deployment

## 🎯 Next Steps After Deployment

1. **Access your sandbox** through the Daytona dashboard
2. **Open the application** at the provided URLs
3. **Configure LLM API keys** in the LLM Setup tab
4. **Load demo data** in the Data Setup tab
5. **Start querying** your sales pipeline data!

## 🔗 Resources

- **Daytona Dashboard**: https://www.daytona.io/
- **Documentation**: https://www.daytona.io/docs/
- **Python SDK**: https://pypi.org/project/daytona-sdk/
- **GitHub**: https://github.com/daytonaio/daytona

---

**Your IBM Sales Pipeline Analytics application is now ready for deployment to Daytona Sandboxes! 🎉**