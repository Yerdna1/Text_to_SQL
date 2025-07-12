#!/usr/bin/env python3
"""
LLM Connector for IBM Sales Pipeline Analytics
Manages connections to various LLM providers for SQL generation
"""

import json
import streamlit as st
import requests
from typing import Dict

# Optional LLM provider imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMConnector:
    """Connects to various LLM providers for SQL generation"""
    
    def __init__(self, provider: str = "ollama", model_name: str = "codellama", api_key: str = None, base_url: str = None):
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url or "http://localhost:11434"  # Default Ollama URL
        self.connected = False
        self.client = None
        self.check_connection()
    
    def check_connection(self):
        """Check if the selected LLM provider is available"""
        if self.provider == "ollama":
            try:
                response = requests.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    st.success("✅ Connected to Ollama (Local LLM)")
                    self.connected = True
                    return True
            except:
                st.warning("⚠️ Ollama not available. Using fallback approach.")
                return False
        
        elif self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                st.error("❌ Gemini package not installed. Run: pip install google-generativeai")
                return False
            
            if not self.api_key:
                st.warning("⚠️ Gemini API key required. Using fallback approach.")
                return False
            
            try:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                st.success("✅ Connected to Google Gemini API")
                self.connected = True
                return True
            except Exception as e:
                st.error(f"❌ Gemini connection failed: {e}")
                return False
        
        elif self.provider == "openai":
            if not OPENAI_AVAILABLE:
                st.error("❌ OpenAI package not installed. Run: pip install openai")
                return False
            
            if not self.api_key:
                st.warning("⚠️ OpenAI API key required. Using fallback approach.")
                return False
            
            try:
                self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url if self.base_url != "http://localhost:11434" else None)
                # Test connection with a simple request
                st.success("✅ Connected to OpenAI API")
                self.connected = True
                return True
            except Exception as e:
                st.error(f"❌ OpenAI connection failed: {e}")
                return False
        
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                st.error("❌ Anthropic package not installed. Run: pip install anthropic")
                return False
            
            if not self.api_key:
                st.warning("⚠️ Anthropic API key required. Using fallback approach.")
                return False
            
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                st.success("✅ Connected to Anthropic Claude API")
                self.connected = True
                return True
            except Exception as e:
                st.error(f"❌ Anthropic connection failed: {e}")
                return False
        
        elif self.provider == "deepseek":
            if not OPENAI_AVAILABLE:
                st.error("❌ OpenAI package required for DeepSeek. Run: pip install openai")
                return False
            
            if not self.api_key:
                st.warning("⚠️ DeepSeek API key required. Using fallback approach.")
                return False
            
            try:
                self.client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                st.success("✅ Connected to DeepSeek API")
                self.connected = True
                return True
            except Exception as e:
                st.error(f"❌ DeepSeek connection failed: {e}")
                return False
        
        elif self.provider == "mistral":
            if not OPENAI_AVAILABLE:
                st.error("❌ OpenAI package required for Mistral. Run: pip install openai")
                return False
            
            if not self.api_key:
                st.warning("⚠️ Mistral API key required. Using fallback approach.")
                return False
            
            try:
                self.client = openai.OpenAI(api_key=self.api_key, base_url="https://api.mistral.ai/v1")
                st.success("✅ Connected to Mistral AI API")
                self.connected = True
                return True
            except Exception as e:
                st.error(f"❌ Mistral connection failed: {e}")
                return False
        
        elif self.provider == "openrouter":
            if not self.api_key:
                st.warning("⚠️ OpenRouter API key required. Using fallback approach.")
                return False
            
            try:
                # OpenRouter uses OpenAI-compatible API
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                st.success("✅ Connected to OpenRouter API")
                self.connected = True
                return True
            except Exception as e:
                st.error(f"❌ OpenRouter connection failed: {e}")
                return False
        
        return False
    
    def generate_sql(self, question: str, schema_info: str, data_dictionary: str) -> Dict:
        """Generate SQL query from natural language question"""
        
        # Always use DB2 syntax
        syntax_requirements = """
CRITICAL IBM DB2 SQL SYNTAX REQUIREMENTS:
1. Generate PURE IBM DB2 SQL syntax ONLY
2. Use DB2 date functions: CURRENT DATE, CURRENT TIMESTAMP, YEAR(date), MONTH(date), DAY(date)
3. For current date filtering use: YEAR(column_name) = YEAR(CURRENT DATE)
4. Use DB2 string functions: SUBSTR(), LENGTH(), UPPER()
5. Use DECIMAL(value, precision, scale) for financial calculations
6. Use NULLIF() for division by zero protection
7. Use WITH clauses (CTEs) for complex queries
8. Use FETCH FIRST n ROWS ONLY instead of LIMIT
9. Format financial values: DECIMAL(SUM(value), 18, 2) or similar"""
        
        examples = """
EXAMPLE IBM DB2 PATTERNS:
- Current year: WHERE YEAR(column_name) = YEAR(CURRENT DATE)
- Current quarter: WHERE QUARTER(column_name) = QUARTER(CURRENT DATE)
- Financial format: DECIMAL(SUM(PPV_AMT) / 1000000, 18, 2) AS FORECASTED_REVENUE_M
- Safe division: DECIMAL(value / NULLIF(divisor, 0), 18, 2)
- Row limiting: FETCH FIRST 100 ROWS ONLY"""
        
        prompt = f"""
You are an expert SQL analyst for IBM Sales Pipeline Analytics. Generate a precise SQL query based on the user's question.

SCHEMA INFORMATION:
{schema_info}

DATA DICTIONARY KNOWLEDGE BASE:
{data_dictionary}

USER QUESTION: {question}

{syntax_requirements}

BUSINESS CONTEXT:
- PPV_AMT = AI-based revenue forecast (use for forecasting)
- OPPORTUNITY_VALUE = Deal value (use for pipeline value)
- SALES_STAGE values: 'Qualify', 'Propose', 'Negotiate', 'Won', 'Lost'
- Exclude Won/Lost deals for active pipeline
- Use MQT table names (PROD_MQT_CONSULTING_PIPELINE, etc.)

{examples}

IMPORTANT: Return ONLY a valid JSON object with proper SQL:
{{
    "sql_query": "SELECT ... FROM ... WHERE ...",
    "explanation": "Explanation of the query approach...",
    "tables_used": ["table_names"],
    "columns_used": ["column_names"],
    "visualization_type": "table",
    "confidence": 0.9
}}
"""
        
        try:
            if self.provider == "gemini":
                return self._generate_with_gemini(prompt, question, schema_info)
            elif self.provider == "ollama":
                return self._generate_with_ollama(prompt, question, schema_info)
            elif self.provider == "openai":
                return self._generate_with_openai(prompt, question, schema_info)
            elif self.provider == "anthropic":
                return self._generate_with_anthropic(prompt, question, schema_info)
            elif self.provider == "deepseek":
                return self._generate_with_openai_compatible(prompt, question, schema_info, "DeepSeek")
            elif self.provider == "mistral":
                return self._generate_with_openai_compatible(prompt, question, schema_info, "Mistral")
            elif self.provider == "openrouter":
                return self._generate_with_openai_compatible(prompt, question, schema_info, "OpenRouter")
            else:
                return {"error": "Unsupported provider"}
                
        except Exception as e:
            st.error(f"LLM Error: {e}")
            return {"error": str(e)}
    
    def _generate_with_gemini(self, prompt: str, question: str, schema_info: str) -> Dict:
        """Generate SQL using Google Gemini API"""
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            return {"error": f"Gemini API Error: {e}"}
    
    def _generate_with_ollama(self, prompt: str, question: str, schema_info: str) -> Dict:
        """Generate SQL using Ollama local LLM"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get('response', '{}'))
            else:
                return {"error": f"Ollama HTTP error: {response.status_code}"}
                
        except Exception as e:
            st.error(f"Ollama Error: {e}")
            return {"error": f"Ollama Error: {e}"}
    
    def _generate_with_openai(self, prompt: str, question: str, schema_info: str) -> Dict:
        """Generate SQL using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"OpenAI Error: {e}")
            return {"error": f"OpenAI Error: {e}"}
    
    def _generate_with_anthropic(self, prompt: str, question: str, schema_info: str) -> Dict:
        """Generate SQL using Anthropic Claude API"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            st.error(f"Anthropic Error: {e}")
            return {"error": f"Anthropic Error: {e}"}
    
    def _generate_with_openai_compatible(self, prompt: str, question: str, schema_info: str, provider_name: str) -> Dict:
        """Generate SQL using OpenAI-compatible API (DeepSeek, Mistral, OpenRouter)"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            st.error(f"{provider_name} Error: {e}")
            return {"error": f"{provider_name} Error: {e}"}