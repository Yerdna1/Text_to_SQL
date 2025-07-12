# Alternative Deployment Options

Since the original Daytona service has been sunset, here are several excellent alternatives to deploy your IBM Sales Pipeline Analytics application:

## 🚀 Quick Local Deployment (Recommended)

### Option 1: Docker Compose (Fastest)

```bash
# Simple one-command deployment
./deploy.sh

# Or manually:
docker-compose up -d
```

**Access**: http://localhost:3000

### Option 2: Development Mode

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend  
cd frontend
npm install
npm run dev
```

**Access**: http://localhost:3000

## ☁️ Cloud Deployment Options

### 1. **Railway** (Recommended - Easy)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Git-based deployments
- ✅ Environment variables support

### 2. **Vercel** (Frontend) + **Railway** (Backend)

Frontend on Vercel:
```bash
cd frontend
npx vercel --prod
```

Backend on Railway:
```bash
cd backend
railway up
```

### 3. **Render** (Full-Stack)

1. Create account at render.com
2. Connect your GitHub repository
3. Deploy as Docker service
4. Automatic builds and deployments

### 4. **DigitalOcean App Platform**

```bash
# Create doctl app spec
cat > app.yaml << EOF
name: ibm-analytics
services:
- name: web
  source_dir: /
  dockerfile_path: Dockerfile
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 3000
  routes:
  - path: /
EOF

doctl apps create --spec app.yaml
```

### 5. **Google Cloud Run**

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/ibm-analytics
gcloud run deploy --image gcr.io/PROJECT-ID/ibm-analytics --platform managed
```

## 🏠 Self-Hosted Options

### 1. **Portainer** (Docker UI)

```bash
docker volume create portainer_data
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ee:latest
```

### 2. **Coolify** (Self-hosted PaaS)

Install Coolify on your server and deploy via Git repository.

### 3. **Dokku** (Mini-Heroku)

```bash
# On your server
dokku apps:create ibm-analytics
git remote add dokku dokku@your-server:ibm-analytics
git push dokku main
```

## 🎯 Recommended Path

**For immediate testing**:
```bash
./deploy.sh
# Access at http://localhost:3000
```

**For production deployment**:
1. **Railway** - Easiest cloud option
2. **Render** - Great for full-stack apps  
3. **Vercel + Railway** - Best performance (split frontend/backend)

## 🔧 Environment Setup

For any cloud deployment, add these environment variables:

```
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## 📱 Mobile/Tablet Access

All deployment options provide responsive web interfaces that work perfectly on:
- 📱 Mobile devices
- 📱 Tablets  
- 💻 Desktops
- 🖥️ Large screens

## 🆘 Need Help?

1. **Local Issues**: Run `python test_deployment.py` to diagnose
2. **Cloud Issues**: Check the deployment platform's logs
3. **API Issues**: Verify your LLM API keys are correctly set

Would you like me to help you deploy to any of these alternatives?