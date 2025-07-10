# 🌟 Google Gemini API Setup Guide

## Why Gemini API?

Google Gemini provides **superior SQL generation quality** compared to local models:
- 🎯 **Better understanding** of natural language questions
- 📊 **More accurate** table and column selection
- 🔍 **Contextual awareness** of business logic
- ⚡ **Faster response times** than local models
- 🧠 **Advanced reasoning** for complex queries

## 🚀 Quick Setup

### 1. Get Your API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key (starts with `AIza...`)

### 2. Configure in Application

1. Open the app at http://localhost:8501
2. In the sidebar, select **"gemini"** as LLM Provider
3. Paste your API key in the **"Gemini API Key"** field
4. Choose model: **"gemini-1.5-pro"** (recommended)
5. Click **"🔗 Connect to Gemini API"**

### 3. Test the Connection

- Upload data dictionary and load MQT tables
- Ask: **"What's the forecasted revenue this month"**
- Click **"🚀 Generate Query"**
- You should see a much more sophisticated SQL query!

## 📊 Model Comparison

| Model | Speed | SQL Quality | Cost | Use Case |
|-------|-------|-------------|------|----------|
| **gemini-1.5-pro** | Medium | ⭐⭐⭐⭐⭐ | $$ | Complex queries, best results |
| **gemini-1.5-flash** | Fast | ⭐⭐⭐⭐ | $ | Quick queries, good quality |
| **gemini-pro** | Medium | ⭐⭐⭐ | $ | Basic queries |
| **Local Ollama** | Varies | ⭐⭐ | Free | Privacy-focused, offline |

## 🎯 Expected Improvements

With Gemini API, you should see:

### Better Question Understanding
- "What's our Q4 forecast" → Correctly identifies quarter filtering
- "Show pipeline by region" → Maps to GEOGRAPHY column
- "Which deals are at risk" → Identifies low probability deals

### Smarter Column Selection
- Uses PPV_AMT for forecasting (not OPPORTUNITY_VALUE)
- Selects appropriate date columns for time filtering
- Chooses relevant dimensions for grouping

### More Sophisticated Queries
```sql
-- Instead of basic queries, you'll get:
SELECT 
    GEOGRAPHY,
    strftime('%Y-%m', OPPORTUNITY_CREATE_DATE) as MONTH,
    SUM(PPV_AMT) / 1000000.0 as FORECASTED_REVENUE_M,
    COUNT(*) as OPPORTUNITY_COUNT
FROM PROD_MQT_CONSULTING_PIPELINE 
WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    AND strftime('%Y-%m', OPPORTUNITY_CREATE_DATE) = strftime('%Y-%m', 'now')
GROUP BY GEOGRAPHY, MONTH
ORDER BY FORECASTED_REVENUE_M DESC
```

## 💡 Best Practices

### For Better Results:
- Use specific business terminology (PPV, pipeline, geography)
- Ask for comparisons ("vs last quarter", "by region")
- Specify time periods ("this month", "Q4", "YTD")

### Example Questions That Work Great:
- "What's the forecasted revenue this month by geography?"
- "Show me the top 10 clients by pipeline value"
- "Compare win rates across different markets"
- "Which opportunities are likely to close this quarter?"
- "Show pipeline trends over the last 6 months"

## 🔒 Security & Privacy

- API calls are made directly from your machine
- No data is stored by Google beyond the API call
- All data processing happens in your local SQLite database
- Consider using demo data for testing if working with sensitive information

## 🛠️ Troubleshooting

### "Invalid API Key" Error
- Check the key starts with `AIza...`
- Ensure no extra spaces in the key
- Verify the key is active in Google AI Studio

### "Quota Exceeded" Error
- Check your API usage limits
- Consider using gemini-1.5-flash for faster/cheaper queries

### Poor Query Quality
- Ensure data dictionary is uploaded
- Try more specific questions
- Check that MQT tables are loaded correctly

---

**Ready to experience superior SQL generation with Google Gemini!** 🚀