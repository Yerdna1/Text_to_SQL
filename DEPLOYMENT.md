# IBM Sales Pipeline Analytics - Deployment Guide

Modern deployment guide for the Next.js/FastAPI application to Daytona and other Docker environments.

## 🏗️ Architecture

The application consists of:
- **Frontend**: Next.js React application (Port 3000)
- **Backend**: FastAPI Python application (Port 8000)
- **Multi-Agent System**: AI-powered SQL enhancement
- **Database**: SQLite with dynamic MQT table loading

## 🚀 Quick Deployment to Daytona

### Prerequisites
- Docker and Docker Compose installed
- At least 2GB RAM available
- Ports 3000 and 8000 available

### 1. Quick Start

```bash
# Run the deployment script
./deploy.sh
```

### 2. Access the Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000

## 🎯 Daytona-Specific Deployment

### Using Daytona with API Key: `cd lovable-ui`

```bash
# Method 1: Frontend development
cd frontend
npm install
npm run dev

# Method 2: Full Docker deployment
docker-compose up -d
```

### Environment Variables for Daytona

Create a `.env` file:
```bash
# API Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Default API Keys (optional)
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

## 📊 Getting Started

### 1. Data Setup
**Option A: Demo Data**
- Go to "Data Setup" tab
- Click "Demo Data" 
- Click "Load Demo Data"

**Option B: Upload Your Data**
- Go to "Data Setup" tab
- Click "Upload Files"
- Upload your MQT CSV/Excel files

### 2. LLM Configuration
- Go to "LLM Setup" tab
- Choose your preferred provider:
  - **Gemini** (Recommended): Get API key from https://ai.google.dev/gemini-api
  - **DeepSeek** (Recommended): Get API key from https://platform.deepseek.com
  - **OpenAI**: Get API key from https://platform.openai.com/api-keys
- Enter your API key and connect

### 3. Start Querying
- Go to "Query Interface" tab
- Ask natural language questions like:
  - "What is the total pipeline value by geography?"
  - "Show me win rates by market segment"

## 🔧 Development Commands

```bash
# Frontend development
cd frontend
npm install
npm run dev

# Backend development  
cd backend
pip install -r requirements.txt
python main.py
```

## 🐳 Docker Deployment

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📁 Project Structure
```
├── frontend/                   # Next.js React frontend
│   ├── app/                   # App router pages
│   ├── components/            # React components
│   ├── package.json          # Frontend dependencies
│   └── Dockerfile            # Frontend container
├── backend/                   # FastAPI backend
│   ├── main.py               # API server
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile.backend    # Backend container
├── agents/                    # Multi-agent system
├── data_dictionary.py         # Data dictionary management
├── database_manager.py        # Database operations
├── llm_connector.py           # LLM integrations
├── docker-compose.yml         # Docker orchestration
├── deploy.sh                  # Deployment script
└── DEPLOYMENT.md              # This guide
```

## 🔍 Troubleshooting

**Backend fails to start:**
```bash
docker-compose logs backend
docker-compose restart backend
```

**Frontend build fails:**
```bash
docker-compose build --no-cache frontend
```

**Port conflicts:**
Edit `docker-compose.yml` to use different ports

## 📝 Features

- ✅ Natural Language to SQL conversion
- ✅ Multi-Agent SQL enhancement and validation
- ✅ Interactive web interface with React components
- ✅ File upload and demo data loading
- ✅ Multiple LLM provider support (Gemini, DeepSeek, OpenAI, etc.)
- ✅ Real-time query results with charts and tables
- ✅ Docker containerization for easy deployment
- ✅ Daytona deployment ready with API key support

## 🔒 Security Notes

- API keys are stored in memory only (not persisted)
- All database operations are isolated to SQLite
- No external network access required except for LLM API calls