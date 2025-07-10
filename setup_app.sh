#!/bin/bash

echo "🚀 Setting up IBM Sales Pipeline Analytics Chat Application"
echo "============================================================"

# Install Python requirements
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

# Install Ollama (if not already installed)
echo "🧠 Setting up Local LLM (Ollama)..."
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Download recommended models
echo "⬇️ Downloading LLM models..."
echo "This may take a few minutes..."

# CodeLlama for SQL generation
ollama pull codellama:7b-instruct

# SQLCoder specialized for SQL
ollama pull sqlcoder:7b

# Mistral as alternative
ollama pull mistral:7b-instruct

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application:"
echo "1. Start Ollama service: ollama serve"
echo "2. Run the app: streamlit run create_interactive_app.py"
echo ""
echo "📋 Make sure you have:"
echo "- IBM_COMPLETE_ALL_COLUMNS_Dictionary.xlsx file"
echo "- MQT CSV files in a directory"
echo ""
echo "🌐 The app will open at: http://localhost:8501"