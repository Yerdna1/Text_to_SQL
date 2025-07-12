# Multi-stage Docker build for IBM Sales Pipeline Analytics

# Stage 1: Build frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code
COPY *.py ./
COPY agents/ ./agents/
COPY backend/main.py ./

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package.json ./frontend/

# Expose ports
EXPOSE 3000 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting IBM Sales Pipeline Analytics..."\n\
echo "Starting FastAPI backend on port 8000..."\n\
python main.py &\n\
echo "Starting Next.js frontend on port 3000..."\n\
cd frontend && npm start &\n\
wait' > start.sh && chmod +x start.sh

CMD ["./start.sh"]