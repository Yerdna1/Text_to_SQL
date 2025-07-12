# 🤖 Multi-Agent SQL Query Orchestration System

## Overview

The Multi-Agent SQL Query Orchestration System enhances the IBM Sales Pipeline Analytics application with intelligent SQL query validation, enhancement, and optimization using specialized AI agents.

## 🎯 Key Features

### 1. **DB2 Syntax Validator Agent** 🔍
- **Purpose**: Validates and corrects SQL syntax for IBM DB2 compatibility
- **Capabilities**:
  - Converts between DB2 and SQLite syntax automatically
  - Fixes DECIMAL function usage: `DECIMAL(value, precision, scale)` → `ROUND(value, scale)`
  - Handles date functions: `CURRENT DATE` ↔ `date('now')`
  - Validates FETCH FIRST vs LIMIT syntax
  - Checks table and column names against available schema

### 2. **WHERE Clause Enhancer Agent** 🎯
- **Purpose**: Intelligently adds contextual filters based on natural language questions
- **Capabilities**:
  - **Time Filters**: Current quarter, specific quarters, YTD, date ranges
  - **Geographic Filters**: Americas, EMEA, APAC, specific countries
  - **Product Filters**: AI/GenAI focus, consulting vs software, UT hierarchy
  - **Business Filters**: Exclude Won/Lost deals, latest snapshots, active pipeline

### 3. **Query Optimizer Agent** 🚀
- **Purpose**: Applies performance optimizations for better query execution
- **Capabilities**:
  - Adds row limits to prevent excessive result sets
  - Suggests MQT-specific optimizations
  - Implements best practices for large datasets
  - Provides performance hints

## 🔧 Configuration

### In Streamlit App Sidebar:

1. **Enable Multi-Agent System**
   ```
   ☑️ Enable Multi-Agent SQL Enhancement
   ```

2. **Database Type Selection**
   - **SQLite**: For local testing and development
   - **DB2**: For actual IBM DB2 database connections

3. **Agent Configuration Panel**
   - View active agents and their capabilities
   - Check system status and availability

## 📝 Usage Examples

### Example 1: Time and Geographic Context

**Question**: *"What is the total AI revenue forecast for Americas in Q4 2024?"*

**Original Query**:
```sql
SELECT SUM(PPV_AMT) FROM PROD_MQT_CONSULTING_PIPELINE
```

**Enhanced Query**:
```sql
SELECT ROUND(SUM(PPV_AMT) / 1000000.0, 2) AS FORECASTED_REVENUE_M 
FROM PROD_MQT_CONSULTING_PIPELINE 
WHERE YEAR = 2024 
  AND QUARTER = 4 
  AND GEOGRAPHY = 'AMERICAS' 
  AND (IBM_GEN_AI_IND = 1 OR PARTNER_GEN_AI_IND = 1)
  AND SALES_STAGE NOT IN ('Won', 'Lost')
  AND SNAPSHOT_LEVEL = 'W'
  AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE YEAR = 2024 AND QUARTER = 4)
LIMIT 1000
```

**Enhancements Applied**:
- ✅ Added Q4 2024 time filter
- ✅ Added Americas geographic filter  
- ✅ Added AI/GenAI product filter
- ✅ Added active pipeline filter (exclude Won/Lost)
- ✅ Added latest weekly snapshot filter
- ✅ Added result limit for performance

### Example 2: Current Period Analysis

**Question**: *"Show me current month pipeline for EMEA consulting"*

**Enhancements Applied**:
- Current month time filter
- EMEA geographic filter
- Consulting product type filter
- Active pipeline filter

### Example 3: YTD Performance

**Question**: *"What's our YTD win rate by market?"*

**Enhancements Applied**:
- Year-to-date time filter
- Win rate calculation optimization
- Market dimension grouping

## 🔄 Processing Pipeline

```
1. Initial SQL Generation (LLM)
         ↓
2. DB2 Syntax Validation & Correction
         ↓  
3. WHERE Clause Enhancement (Context Detection)
         ↓
4. Query Optimization & Performance Tuning
         ↓
5. Final Enhanced Query
```

## 📊 Integration Modes

### Single LLM Mode
- Processes query after initial LLM generation
- Shows before/after comparison
- Displays detailed enhancement explanations

### Parallel Mode (3 LLMs)
- Generates queries with 3 different LLMs
- Selects best result automatically
- Applies agent enhancement to the winning query
- Shows confidence comparison across models

## 🎛️ Technical Integration

### Function Call
```python
from sql_agent_orchestrator import process_with_agents

result = process_with_agents(
    sql_query="SELECT SUM(PPV_AMT) FROM PROD_MQT_CONSULTING_PIPELINE",
    question="What is the total AI revenue forecast for Americas?",
    db_manager=db_manager,
    data_dict=data_dictionary,
    db_type="SQLite"  # or "DB2"
)
```

### Response Format
```python
{
    "success": True,
    "final_query": "enhanced SQL query",
    "original_query": "original SQL query", 
    "processing_log": [...],
    "overall_confidence": 0.95,
    "explanation": "Human-readable processing summary",
    "improvements": {
        "syntax_corrections": 2,
        "where_enhancements": 4, 
        "optimizations": 1
    }
}
```

## 🧪 Testing

Run the test suite:
```bash
python test_agents.py
```

This will validate:
- Agent initialization
- Query processing pipeline
- Enhancement detection
- Confidence scoring

## 🔧 Troubleshooting

### Agent System Not Available
- Check that `sql_agent_orchestrator.py` is in the same directory
- Verify all imports are working correctly

### No Enhancements Applied
- Check that the question contains recognizable context keywords
- Verify table and column names are available in schema
- Enable debug mode for detailed processing logs

### Syntax Errors
- Ensure database type is set correctly (SQLite vs DB2)
- Check that column names match the actual database schema
- Verify the original query is valid before enhancement

## 📈 Performance Impact

- **Minimal Latency**: Agent processing adds ~0.5-1 second
- **High Value**: Significantly improves query accuracy and completeness
- **Intelligent Caching**: Reuses schema validations for similar queries
- **Parallel Friendly**: Works seamlessly with multi-LLM generation

## 🎯 Benefits

1. **Higher Query Accuracy**: Contextual filters ensure relevant results
2. **Better Performance**: Automatic optimizations and limits
3. **DB2 Compatibility**: Ensures queries work on actual IBM systems
4. **User Experience**: More intuitive natural language understanding
5. **Transparency**: Clear explanations of all enhancements made

---

*This multi-agent system transforms simple SQL queries into sophisticated, context-aware analytics queries automatically, making IBM Sales Pipeline Analytics more powerful and user-friendly.*