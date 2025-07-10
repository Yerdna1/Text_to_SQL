# IBM Sales Pipeline Analytics Chat Application

## 🎯 Overview

This interactive application provides natural language querying of IBM sales pipeline data using a local LLM model. It features:

- 🤖 **Natural Language to SQL** conversion
- 📚 **Complete Data Dictionary** as knowledge base  
- 🖱️ **Hover explanations** for all columns
- 📊 **Auto-generated visualizations**
- 🔒 **Privacy-focused** (runs entirely locally)

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
chmod +x setup_app.sh
./setup_app.sh
```

### 2. Start the Application
```bash
# Terminal 1: Start Ollama service
ollama serve

# Terminal 2: Run the Streamlit app
streamlit run create_interactive_app.py
```

### 3. Open Application
Navigate to: `http://localhost:8501`

## 📋 Manual Setup (if script fails)

### Install Python Packages
```bash
pip3 install streamlit pandas plotly openpyxl requests
```

### Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
ollama serve
```

### Download LLM Models
```bash
# Best for SQL generation
ollama pull codellama:7b-instruct

# Specialized SQL model
ollama pull sqlcoder:7b

# Alternative general model
ollama pull mistral:7b-instruct
```

## 🎮 How to Use

### 1. **Setup Phase** (Sidebar)
- 📚 **Upload Data Dictionary**: `IBM_COMPLETE_ALL_COLUMNS_Dictionary.xlsx`
- 📁 **Set MQT Tables Path**: Point to your CSV files directory
- 🧠 **Connect LLM**: Choose model (codellama recommended)

### 2. **Query Phase** (Main Interface)
- 💬 **Ask Questions**: Use natural language
- 🔍 **Review Generated SQL**: Check the query logic
- ▶️ **Execute Query**: Run and see results
- 📊 **View Visualizations**: Auto-generated charts

### 3. **Analysis Phase**
- 🖱️ **Hover over columns** for detailed explanations
- 📋 **Check query details** for table/column usage
- 💡 **Review explanations** for why specific columns were chosen

## 💡 Example Questions

### Pipeline Analysis
- "What is the total pipeline value by geography?"
- "Show me opportunities by sales stage"
- "Which clients have the largest pipeline?"

### Performance Metrics
- "What's our win rate by market?"
- "Compare PPV vs budget coverage"
- "Show quarterly performance trends"

### Detailed Analysis
- "Which deals are at risk of being lost?"
- "What's the average deal size by industry?"
- "Show pipeline velocity by region"

## 🔧 Advanced Features

### **Smart Column Detection**
- The app automatically finds relevant columns based on your question
- Uses the complete data dictionary as knowledge base
- Provides intelligent table selection

### **Hover Explanations**
When you hover over column names, you'll see:
- 📊 Category and description
- 🇸🇰 Slovak translation
- 🔢 Calculation method
- 💼 Business use case
- 📈 Data type and examples

### **Auto Visualizations**
Based on your query results:
- 📊 **Bar charts** for categorical comparisons
- 📈 **Line charts** for time series data
- 🥧 **Pie charts** for distribution analysis
- 📋 **Tables** for detailed data

### **Query Confidence**
Each generated query includes a confidence score showing how well the LLM understood your question.

## 🛠️ Technical Architecture

### **Components**
1. **DataDictionary**: Manages 216+ column definitions
2. **LocalLLMConnector**: Interfaces with Ollama models
3. **DatabaseManager**: Loads and manages MQT tables
4. **Streamlit UI**: Interactive web interface

### **Local LLM Models**

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| **codellama:7b-instruct** | 3.8GB | SQL generation | Fast |
| **sqlcoder:7b** | 3.8GB | SQL-specific | Medium |
| **mistral:7b-instruct** | 4.1GB | General queries | Fast |

### **Data Flow**
1. User enters natural language question
2. App searches data dictionary for relevant columns/tables
3. LLM generates SQL query with context
4. Query executes against loaded MQT tables
5. Results displayed with auto-generated visualizations

## 🔍 Troubleshooting

### **Ollama Connection Issues**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### **Model Download Issues**
```bash
# Check available models
ollama list

# Re-download model
ollama pull codellama:7b-instruct
```

### **Streamlit Issues**
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with debug mode
streamlit run create_interactive_app.py --logger.level=debug
```

### **Data Loading Issues**
- Ensure MQT CSV files are in the specified directory
- Check file permissions
- Verify data dictionary Excel file format

## 📊 Performance Tips

### **For Better Query Generation**
- Be specific in your questions
- Use domain terminology (pipeline, PPV, budget, etc.)
- Mention specific dimensions (geography, market, stage)

### **For Faster Response**
- Use codellama:7b-instruct (fastest SQL model)
- Limit result sets with date ranges
- Use "LIMIT" in complex queries

### **For Better Visualizations**
- Ask for data that naturally groups (by geography, stage, etc.)
- Request time-series data for trend analysis
- Specify what you want to compare

## 🎯 Business Value

### **For Sales Leaders**
- Quick pipeline health checks
- Performance comparisons across territories
- Risk identification and opportunity assessment

### **For Sales Teams**
- Easy access to deal-specific insights
- Understanding of pipeline composition
- Action-oriented analytics

### **For Executives**
- Strategic overview of sales performance
- Predictive insights for planning
- Real-time business intelligence

## 🔒 Privacy & Security

- **100% Local Processing**: No data leaves your machine
- **No Cloud Dependencies**: All models run locally
- **Secure Data Handling**: In-memory database processing
- **No API Keys Required**: No external service dependencies

---

*Ready to explore your IBM Sales Pipeline data with AI-powered natural language queries!* 🚀