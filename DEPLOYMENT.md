# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### 1. Deploy the App
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `Yerdna1/Text_to_SQL`
4. Main file path: `create_interactive_app.py`
5. Click "Deploy!"

### 2. Set Environment Variables
After deployment, you need to configure the API keys:

1. Go to your app's settings (gear icon)
2. Click on "Secrets" in the left sidebar
3. Add the following secrets in TOML format:

```toml
[env]
GEMINI_API_KEY = "AIzaSyC3Ppu2KDF9-pSNzC2A5jvQH7wn7c9o3cE"
DEEPSEEK_API_KEY = "sk-0574945ee88a427f8dd55bb40ea804eb"
OPENROUTER_API_KEY = "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"
```

4. Click "Save"
5. Your app will automatically restart with the new environment variables

### 3. App Features
- **Multi-LLM Support**: Gemini, DeepSeek, OpenRouter, OpenAI, Anthropic
- **Natural Language to SQL**: Convert questions to SQL queries
- **Interactive Visualizations**: KPIs, charts, and formatted tables
- **Data Dictionary Integration**: Upload Excel files for column explanations
- **File Upload**: Support for CSV and Excel MQT data files

### 4. Usage
1. Upload your data dictionary (Excel file) in the sidebar
2. Load MQT tables (CSV/Excel files or directory path)
3. Choose your preferred LLM provider
4. Ask natural language questions about your data
5. View results with automatic visualizations and explanations

### 5. Local Development
For local development, copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
streamlit run create_interactive_app.py
```

### 6. Repository Structure
```
├── create_interactive_app.py    # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .streamlit/
│   ├── config.toml             # Streamlit configuration
│   └── secrets.toml            # Local secrets (not committed)
├── .env                        # Local environment variables (not committed)
├── .gitignore                  # Git ignore rules
└── DEPLOYMENT.md              # This deployment guide
```

### 7. Troubleshooting
- **Missing API Keys**: Ensure all required environment variables are set in Streamlit Cloud secrets
- **Module Errors**: Check that all dependencies are listed in `requirements.txt`
- **File Upload Issues**: Use the upload widgets or provide full file paths for local development

### 8. Security Notes
- API keys are stored securely in Streamlit Cloud secrets
- The `.env` file and `secrets.toml` are excluded from version control
- Environment variables are loaded automatically on app startup