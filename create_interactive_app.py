#!/usr/bin/env python3
"""
Interactive IBM Sales Pipeline Analytics Chat Application
with Natural Language to SQL conversion using local LLM
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import re
import webbrowser
import subprocess
import platform

# Optional tkinter import for file dialogs
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# Load environment variables from .env file or Streamlit secrets
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

# For Streamlit Cloud deployment, also try to load from st.secrets
try:
    if hasattr(st, 'secrets') and 'env' in st.secrets:
        for key, value in st.secrets.env.items():
            if key not in os.environ:
                os.environ[key] = value
except Exception:
    # Continue if secrets are not available
    pass

# For local LLM - we'll use Ollama with CodeLlama or similar
try:
    import requests
except ImportError:
    st.error("Please install requests: pip install requests")

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

try:
    # OpenRouter uses OpenAI-compatible API
    OPENROUTER_AVAILABLE = True  # Uses requests, always available
except ImportError:
    OPENROUTER_AVAILABLE = False

class DataDictionary:
    """Manages the complete data dictionary and knowledge base including all documentation"""
    
    def __init__(self, excel_path: str = None, data_exports_path: str = "/Volumes/DATA/Python/IBM_analyza/data_exports"):
        self.dictionary = {}
        self.business_questions = ""
        self.data_definitions = ""
        self.chatbot_queries = ""
        self.query_explanations = ""
        self.visual_context = ""
        
        # Load all knowledge base components
        if excel_path:
            self.load_dictionary(excel_path)
        self.load_additional_context(data_exports_path)
    
    def load_dictionary(self, excel_path: str):
        """Load the complete data dictionary from Excel"""
        try:
            # Load the main dictionary sheet
            df = pd.read_excel(excel_path, sheet_name='ALL Columns Dictionary')
            
            for _, row in df.iterrows():
                self.dictionary[row['Column']] = {
                    'category': row.get('Category', ''),
                    'description': row.get('Description', ''),
                    'slovak_description': row.get('Slovak_Description', ''),
                    'calculation': row.get('Calculation', ''),
                    'business_use': row.get('Business_Use', ''),
                    'example_values': row.get('Example_Values', ''),
                    'data_type': row.get('Data_Type', ''),
                    'table_source': row.get('Table_Source', '')
                }
            
            st.success(f"📊 Loaded data dictionary with {len(self.dictionary)} columns")
            
        except Exception as e:
            st.error(f"Error loading data dictionary: {e}")
    
    def load_additional_context(self, data_exports_path: str):
        """Load additional knowledge base files"""
        try:
            # Load business questions
            questions_path = os.path.join(data_exports_path, "questions.txt")
            if os.path.exists(questions_path):
                with open(questions_path, 'r', encoding='utf-8') as f:
                    self.business_questions = f.read()
            
            # Load data definitions 
            data_dict_path = os.path.join(data_exports_path, "Data Dictionaries.txt")
            if os.path.exists(data_dict_path):
                with open(data_dict_path, 'r', encoding='utf-8') as f:
                    self.data_definitions = f.read()
            
            # Load chatbot queries if available
            chatbot_path = "/Volumes/DATA/Python/IBM_analyza/chatbot_queries.md"
            if os.path.exists(chatbot_path):
                with open(chatbot_path, 'r', encoding='utf-8') as f:
                    self.chatbot_queries = f.read()
            
            # Load query explanations if available
            explanations_path = "/Volumes/DATA/Python/IBM_analyza/query_explanations.md"
            if os.path.exists(explanations_path):
                with open(explanations_path, 'r', encoding='utf-8') as f:
                    self.query_explanations = f.read()
            
            # Create visual context summary
            self.visual_context = """
            VISUAL CONTEXT FROM IBM SALES PIPELINE DASHBOARDS:
            
            From the dashboard screenshots, we can see:
            
            1. REVENUE TYPE FILTER: Shows Transactional vs Signings revenue types
            2. GEOGRAPHY FILTER: All, APAC, Americas, EMEA, Japan
            3. MARKET SEGMENTS: Various specialized markets like SRGI Market, UKI Market, US Federal Market, etc.
            4. SERVICE LINES (Lvl 15): Multiple categories including:
               - Intelligent Operations, Power HW, Power TPS, Public Cloud Platform, Storage HW, etc.
            5. PRODUCT LINES (Lvl 17): AI Tools & Runtimes Market, AI/ML Ops, Acoustic Analytics, etc.
            6. DETAILED PRODUCTS (Lvl 20): Specific offerings like ADVISE: Cloud Architecture, AI Assistants, AI Governance, etc.
            
            KEY METRICS VISIBLE:
            - Budget ($M): Financial targets by segment
            - YtY%: Year-over-year growth percentages
            - PPV Cov%: PERFORM Pipeline Value coverage percentage (444% for Total Lvl47)
            - Qualify+ ($M): Qualified pipeline amounts
            - WtW: Week-to-week changes
            - YtY%: Year-over-year comparisons
            - Multiplier for the Week: Pipeline coverage multipliers (ranging from 4.5 to 7.5)
            
            The dashboards show detailed breakdowns by:
            - AI Productivity ($11M budget, 15% YtY)
            - AI/ML Ops ($6M budget, 51% YtY)  
            - Data Fabric ($8M budget, 276% YtY)
            
            This indicates a focus on AI and data services with strong growth metrics.
            """
            
            st.success(f"✅ Loaded comprehensive knowledge base including business questions, data definitions, and visual context")
            
        except Exception as e:
            st.warning(f"Could not load some knowledge base components: {e}")
    
    def get_comprehensive_context(self) -> str:
        """Get complete knowledge base context for LLM"""
        context = ""
        
        # Add data dictionary summary
        if self.dictionary:
            context += "=== COMPLETE DATA DICTIONARY ===\n"
            for col, info in self.dictionary.items():
                context += f"{col}: {info.get('description', '')} | Business Use: {info.get('business_use', '')} | Slovak: {info.get('slovak_description', '')}\n"
            context += "\n"
        
        # Add business questions
        if self.business_questions:
            context += "=== BUSINESS QUESTIONS TO ANSWER ===\n"
            context += self.business_questions[:2000]  # Limit for token management
            context += "\n\n"
        
        # Add data definitions
        if self.data_definitions:
            context += "=== IBM SALES PIPELINE DATA DEFINITIONS ===\n"
            context += self.data_definitions[:3000]  # Limit for token management  
            context += "\n\n"
        
        # Add query examples
        if self.chatbot_queries:
            context += "=== EXAMPLE QUERY PATTERNS ===\n"
            context += self.chatbot_queries[:2000]  # Sample queries for patterns
            context += "\n\n"
        
        # Add query explanations
        if self.query_explanations:
            context += "=== QUERY RATIONALE AND TABLE SELECTION LOGIC ===\n"
            context += self.query_explanations[:2000]  # Key explanations
            context += "\n\n"
        
        # Add visual context
        context += self.visual_context
        
        return context
    
    def get_column_info(self, column: str) -> Dict:
        """Get complete information about a column"""
        return self.dictionary.get(column, {})
    
    def search_columns(self, keyword: str) -> List[str]:
        """Search for columns containing keyword"""
        keyword_lower = keyword.lower()
        matches = []
        
        for col, info in self.dictionary.items():
            if (keyword_lower in col.lower() or 
                keyword_lower in info.get('description', '').lower() or
                keyword_lower in info.get('business_use', '').lower()):
                matches.append(col)
        
        return matches
    
    def get_relevant_tables(self, keywords: List[str]) -> List[str]:
        """Get relevant tables based on keywords"""
        relevant_tables = set()
        
        for keyword in keywords:
            for col, info in self.dictionary.items():
                if keyword.lower() in col.lower() or keyword.lower() in info.get('description', '').lower():
                    table_source = info.get('table_source', '')
                    if table_source and table_source != 'MULTIPLE':
                        relevant_tables.add(table_source)
        
        return list(relevant_tables)

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
        
   
        
        prompt = f"""
You are an expert IBM DB2 SQL analyst for IBM Sales Pipeline Analytics. Generate a precise IBM DB2 SQL query based on the user's question.

SCHEMA INFORMATION:
{schema_info}

DATA DICTIONARY KNOWLEDGE BASE:
{data_dictionary}

USER QUESTION: {question}

CRITICAL SQL SYNTAX REQUIREMENTS (SQLite Compatible):
1. Generate SQLite compatible SQL syntax that simulates DB2 behavior
2. Use SQLite date functions: date('now'), strftime('%m', date('now')), strftime('%Y', date('now'))
3. For current month filtering use: strftime('%m', column_name) = strftime('%m', date('now'))
4. Use SQLite string functions: substr(), length(), upper()
5. Use ROUND() or CAST() for financial calculations instead of DECIMAL()
6. Use NULLIF() for division by zero protection
7. Use WITH clauses (CTEs) for complex queries
8. Date comparisons: date(column_name) = date('now')
9. Format financial values: ROUND(value, 2) or CAST(value AS DECIMAL(15,2))

BUSINESS CONTEXT:
- PPV_AMT = AI-based revenue forecast (use for forecasting)
- OPPORTUNITY_VALUE = Deal value (use for pipeline value)
- SALES_STAGE values: 'Qualify', 'Propose', 'Negotiate', 'Won', 'Lost'
- Exclude Won/Lost deals for active pipeline
- Use MQT table names (PROD_MQT_CONSULTING_PIPELINE, etc.)

EXAMPLE SQLITE PATTERNS:
- Current month: WHERE strftime('%m', OPPORTUNITY_CREATE_DATE) = strftime('%m', date('now')) AND strftime('%Y', OPPORTUNITY_CREATE_DATE) = strftime('%Y', date('now'))
- Financial format: ROUND(SUM(PPV_AMT) / 1000000.0, 2) AS FORECASTED_REVENUE_M
- Safe division: NULLIF(SUM(BUDGET_AMT), 0)

IMPORTANT: Return ONLY a valid JSON object with SQLite-compatible SQL:
{{
    "sql_query": "SELECT ROUND(SUM(PPV_AMT) / 1000000.0, 2) AS FORECASTED_REVENUE_M FROM PROD_MQT_CONSULTING_PIPELINE WHERE ...",
    "explanation": "Used PPV_AMT for AI-based revenue forecast with DB2 DECIMAL formatting...",
    "tables_used": ["PROD_MQT_CONSULTING_PIPELINE"],
    "columns_used": ["PPV_AMT", "OPPORTUNITY_CREATE_DATE", "SALES_STAGE"],
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
            
            # Extract JSON from Claude's response
            response_text = response.content[0].text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            st.error(f"Anthropic Error: {e}")
            return {"error": f"Anthropic Error: {e}"}
    
    def _generate_with_openai_compatible(self, prompt: str, question: str, schema_info: str, provider_name: str) -> Dict:
        """Generate SQL using OpenAI-compatible APIs (DeepSeek, Mistral)"""
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
    

  
def browse_for_directory(title="Select Directory"):
    """Open a directory browser dialog"""
    if not TKINTER_AVAILABLE:
        st.warning("⚠️ File browser not available. Please enter path manually.")
        return None
        
    try:
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        
        # Open directory dialog
        directory = filedialog.askdirectory(title=title)
        root.destroy()
        
        return directory if directory else None
    except Exception as e:
        st.error(f"Could not open directory browser: {e}")
        return None

def browse_for_file(title="Select File", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]):
    """Open a file browser dialog"""
    if not TKINTER_AVAILABLE:
        st.warning("⚠️ File browser not available. Please use the upload widget instead.")
        return None
        
    try:
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        
        # Open file dialog
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        root.destroy()
        
        return file_path if file_path else None
    except Exception as e:
        st.error(f"Could not open file browser: {e}")
        return None

def open_url_in_browser(url):
    """Open URL in default browser"""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        st.error(f"Could not open browser: {e}")
        return False

def open_file_explorer(path):
    """Open file explorer at specified path"""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", path])
        elif system == "Windows":
            subprocess.run(["explorer", path])
        elif system == "Linux":
            subprocess.run(["xdg-open", path])
        return True
    except Exception as e:
        st.error(f"Could not open file explorer: {e}")
        return False

class ParallelSQLGenerator:
    """Generates SQL queries with multiple LLMs in parallel and compares results"""
    
    def __init__(self, providers_config: List[Dict]):
        """
        providers_config: List of dicts with provider, model_name, api_key
        Example: [
            {"provider": "gemini", "model_name": "gemini-2.5-pro", "api_key": "key1"},
            {"provider": "deepseek", "model_name": "deepseek-reasoner", "api_key": "key2"},
            {"provider": "openai", "model_name": "gpt-4o", "api_key": "key3"}
        ]
        """
        self.providers_config = providers_config
        self.connectors = []
        
        # Initialize all connectors
        for config in providers_config:
            try:
                connector = LLMConnector(
                    provider=config["provider"],
                    model_name=config["model_name"],
                    api_key=config.get("api_key")
                )
                if connector.connected:
                    self.connectors.append(connector)
            except Exception as e:
                st.warning(f"Failed to initialize {config['provider']}: {e}")
    
    def generate_parallel(self, question: str, schema_info: str, data_dictionary: str) -> Dict:
        """Generate SQL with multiple models and compare results"""
        import concurrent.futures
        import threading
        import time
        
        results = []
        
        def generate_with_provider(connector):
            try:
                start_time = time.time()
                result = connector.generate_sql(question, schema_info, data_dictionary)
                end_time = time.time()
                
                result["provider"] = connector.provider
                result["model"] = connector.model_name
                result["generation_time"] = round(end_time - start_time, 2)
                return result
            except Exception as e:
                return {
                    "provider": connector.provider,
                    "model": connector.model_name,
                    "error": str(e),
                    "generation_time": 0
                }
        
        # Run parallel generation
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(generate_with_provider, connector) for connector in self.connectors[:3]]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        # Compare and analyze results
        comparison = self.compare_results(results, question)
        
        return {
            "results": results,
            "comparison": comparison,
            "best_result": self.select_best_result(results)
        }
    
    def compare_results(self, results: List[Dict], question: str) -> Dict:
        """Compare SQL queries from different providers"""
        sql_queries = []
        similarities = {}
        
        for result in results:
            if "sql_query" in result and not result.get("error"):
                sql_queries.append(result["sql_query"])
        
        if len(sql_queries) < 2:
            return {"status": "insufficient_results", "message": "Not enough valid queries to compare"}
        
        # Simple similarity check - normalize and compare key components
        normalized_queries = []
        for query in sql_queries:
            # Normalize query for comparison
            normalized = query.upper().replace("\n", " ").replace("  ", " ").strip()
            # Extract main components
            select_part = self.extract_select_part(normalized)
            from_part = self.extract_from_part(normalized)
            where_part = self.extract_where_part(normalized)
            
            normalized_queries.append({
                "full": normalized,
                "select": select_part,
                "from": from_part,
                "where": where_part
            })
        
        # Check for similarities
        select_match = len(set(q["select"] for q in normalized_queries)) == 1
        from_match = len(set(q["from"] for q in normalized_queries)) == 1
        where_similarity = self.check_where_similarity([q["where"] for q in normalized_queries])
        
        overall_similarity = select_match and from_match and where_similarity
        
        return {
            "status": "compared",
            "select_match": select_match,
            "from_match": from_match,
            "where_similarity": where_similarity,
            "overall_similarity": overall_similarity,
            "confidence_level": "HIGH" if overall_similarity else "MEDIUM" if (select_match or from_match) else "LOW"
        }
    
    def extract_select_part(self, query: str) -> str:
        """Extract SELECT part of query"""
        parts = query.split("FROM")
        if len(parts) > 1:
            select_part = parts[0].replace("SELECT", "").strip()
            return select_part
        return ""
    
    def extract_from_part(self, query: str) -> str:
        """Extract FROM part of query"""
        parts = query.split("FROM")
        if len(parts) > 1:
            from_part = parts[1].split("WHERE")[0].split("GROUP BY")[0].split("ORDER BY")[0].strip()
            return from_part
        return ""
    
    def extract_where_part(self, query: str) -> str:
        """Extract WHERE part of query"""
        if "WHERE" in query:
            where_part = query.split("WHERE")[1].split("GROUP BY")[0].split("ORDER BY")[0].strip()
            return where_part
        return ""
    
    def check_where_similarity(self, where_parts: List[str]) -> bool:
        """Check if WHERE clauses are similar (basic implementation)"""
        if not where_parts or all(not part for part in where_parts):
            return True
        
        # Simple keyword-based similarity
        keywords_sets = []
        for where in where_parts:
            if where:
                keywords = set(re.findall(r'\b[A-Z_]+\b', where))
                keywords_sets.append(keywords)
        
        if len(keywords_sets) < 2:
            return True
        
        # Check if there's significant overlap
        intersection = set.intersection(*keywords_sets)
        union = set.union(*keywords_sets)
        
        similarity_ratio = len(intersection) / len(union) if union else 1
        return similarity_ratio > 0.5
    
    def select_best_result(self, results: List[Dict]) -> Dict:
        """Select the best result based on confidence and completeness"""
        valid_results = [r for r in results if "sql_query" in r and not r.get("error")]
        
        if not valid_results:
            return results[0] if results else {}
        
        # Score results based on confidence, explanation quality, etc.
        for result in valid_results:
            score = 0
            score += result.get("confidence", 0) * 100
            score += len(result.get("explanation", "")) * 0.1
            score += len(result.get("tables_used", [])) * 5
            score += len(result.get("columns_used", [])) * 2
            result["quality_score"] = score
        
        # Return highest scoring result
        return max(valid_results, key=lambda x: x.get("quality_score", 0))

class DatabaseManager:
    """Manages database connections and MQT table loading"""
    
    def __init__(self):
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.tables_loaded = {}
        self.schema_info = ""
    
    def load_mqt_tables(self, data_path: str):
        """Load all MQT tables from Excel/CSV files in directory"""
        
        st.info("📁 Loading MQT tables from directory...")
        progress_bar = st.progress(0)
        
        # Find all MQT files
        mqt_files = [f for f in os.listdir(data_path) if 'MQT' in f and f.endswith('.csv')]
        
        for idx, file in enumerate(mqt_files):
            try:
                df = pd.read_csv(os.path.join(data_path, file))
                table_name = file.replace('.csv', '')
                
                # Clean column names
                df.columns = [col.upper().replace(' ', '_') for col in df.columns]
                
                # Load to database
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                
                self.tables_loaded[table_name] = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'file': file
                }
                
                progress_bar.progress((idx + 1) / len(mqt_files))
                
            except Exception as e:
                st.warning(f"⚠️ Could not load {file}: {e}")
        
        self.generate_schema_info()
        st.success(f"✅ Loaded {len(self.tables_loaded)} MQT tables")
    
    def load_uploaded_files(self, uploaded_files):
        """Load MQT tables from uploaded files"""
        
        st.info("📤 Loading uploaded MQT files...")
        progress_bar = st.progress(0)
        
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                # Determine file type and read accordingly
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                else:
                    st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
                    continue
                
                # Create table name from file name
                table_name = uploaded_file.name.replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
                
                # Clean column names
                df.columns = [col.upper().replace(' ', '_') for col in df.columns]
                
                # Load to database
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                
                self.tables_loaded[table_name] = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'file': uploaded_file.name
                }
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
            except Exception as e:
                st.warning(f"⚠️ Could not load {uploaded_file.name}: {e}")
        
        self.generate_schema_info()
        st.success(f"✅ Loaded {len(self.tables_loaded)} tables from uploaded files")
    
    def generate_schema_info(self):
        """Generate schema information for LLM"""
        schema_parts = []
        
        for table_name, info in self.tables_loaded.items():
            schema_parts.append(f"Table: {table_name}")
            schema_parts.append(f"Columns: {', '.join(info['columns'][:10])}...")  # First 10 columns
            schema_parts.append(f"Rows: {info['rows']}")
            schema_parts.append("")
        
        self.schema_info = "\n".join(schema_parts)
    
    def create_demo_data(self):
        """Create demo data for testing when actual files aren't available"""
        st.info("📁 Creating demo MQT data...")
        
        import random
        from datetime import datetime, timedelta
        
        # Create demo PROD_MQT_CONSULTING_PIPELINE data
        demo_data = {
            'OPPORTUNITY_ID': [f'OPP_{i:05d}' for i in range(1, 101)],
            'CLIENT_NAME': [random.choice(['IBM Corp', 'Microsoft', 'Oracle', 'SAP', 'Salesforce', 'Adobe', 'Cisco', 'Dell', 'HP Inc', 'VMware']) for _ in range(100)],
            'GEOGRAPHY': [random.choice(['Americas', 'EMEA', 'APAC', 'Japan']) for _ in range(100)],
            'SALES_STAGE': [random.choice(['Qualify', 'Propose', 'Negotiate', 'Won', 'Lost']) for _ in range(100)],
            'OPPORTUNITY_VALUE': [random.randint(50000, 5000000) for _ in range(100)],
            'PPV_AMT': [random.randint(40000, 4500000) for _ in range(100)],
            'OPPORTUNITY_CREATE_DATE': [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d') for _ in range(100)]
        }
        
        df = pd.DataFrame(demo_data)
        df.to_sql('PROD_MQT_CONSULTING_PIPELINE', self.conn, if_exists='replace', index=False)
        
        self.tables_loaded['PROD_MQT_CONSULTING_PIPELINE'] = {
            'rows': len(df),
            'columns': list(df.columns),
            'file': 'demo_data'
        }
        
        self.generate_schema_info()
        st.success(f"✅ Created demo data with {len(df)} sample opportunities")
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        try:
            return pd.read_sql_query(sql_query, self.conn)
        except Exception as e:
            st.error(f"SQL Error: {e}")
            return pd.DataFrame()

def create_hover_tooltip(column: str, data_dict: DataDictionary) -> str:
    """Create hover tooltip for column explanations"""
    info = data_dict.get_column_info(column)
    
    # If we have dictionary info, use it
    if info and info.get('description') and info.get('description') != 'N/A':
        tooltip = f"""
**{column}**

📊 **Category:** {info.get('category', 'N/A')}

📝 **Description:** {info.get('description', 'No description available')}

🇸🇰 **Slovak:** {info.get('slovak_description', 'N/A')}

🔢 **Calculation:** {info.get('calculation', 'N/A')}

💼 **Business Use:** {info.get('business_use', 'N/A')}

📈 **Data Type:** {info.get('data_type', 'N/A')}

💡 **Examples:** {info.get('example_values', 'N/A')}
"""
        return tooltip
    
    # Generate intelligent explanation for computed/derived columns
    column_lower = column.lower()
    column_clean = column.replace('_', ' ').title()
    
    # Smart explanations based on column patterns
    if 'number_of_countries' in column_lower or 'country_count' in column_lower:
        description = "Count of distinct countries present in the dataset"
        category = "Geographic Metrics"
        business_use = "Used to understand geographic distribution and market reach"
        
    elif 'win_rate' in column_lower:
        description = "Percentage of opportunities that resulted in won deals"
        category = "Sales Performance"
        business_use = "Key metric for measuring sales effectiveness and team performance"
        
    elif 'total_revenue' in column_lower or 'revenue_total' in column_lower:
        description = "Sum of all revenue amounts"
        category = "Financial Metrics"
        business_use = "Primary indicator of business performance and growth"
        
    elif 'forecast' in column_lower and ('revenue' in column_lower or 'amt' in column_lower):
        description = "AI-based predicted revenue using PPV_AMT calculations"
        category = "Forecasting"
        business_use = "Strategic planning and pipeline management"
        
    elif 'pipeline' in column_lower and 'value' in column_lower:
        description = "Total value of active opportunities in the sales pipeline"
        category = "Pipeline Metrics"
        business_use = "Monitor potential future revenue and sales capacity"
        
    elif 'deal_count' in column_lower or 'opportunity_count' in column_lower:
        description = "Number of sales opportunities or deals"
        category = "Volume Metrics"
        business_use = "Track sales activity and opportunity generation"
        
    elif 'average' in column_lower or 'avg' in column_lower:
        description = f"Average value calculated from the underlying data"
        category = "Statistical Metrics"
        business_use = "Understand typical performance levels and benchmarks"
        
    elif column_lower.endswith('_m') or 'million' in column_lower:
        description = f"Financial amount expressed in millions of dollars"
        category = "Financial Metrics"
        business_use = "High-level financial reporting and executive dashboards"
        
    elif 'rate' in column_lower or 'percentage' in column_lower:
        description = f"Percentage calculation showing ratio or performance rate"
        category = "Performance Metrics"
        business_use = "Measure efficiency and success rates"
        
    elif 'geography' in column_lower or 'region' in column_lower:
        description = "Geographic region or territory classification"
        category = "Geographic Dimensions"
        business_use = "Regional analysis and territory management"
        
    elif 'sales_stage' in column_lower or 'stage' in column_lower:
        description = "Current stage in the sales process (e.g., Prospect, Qualified, Won, Lost)"
        category = "Sales Process"
        business_use = "Track deal progression and identify bottlenecks"
        
    elif 'client' in column_lower or 'customer' in column_lower:
        description = "Client or customer name/identifier"
        category = "Customer Dimensions"
        business_use = "Customer analysis and relationship management"
        
    else:
        # Generic explanation for unknown columns
        description = f"Data column containing {column_clean.lower()} information"
        category = "Data Field"
        business_use = "Analysis and reporting purposes"
    
    # Format the tooltip
    tooltip = f"""
**{column_clean}**

📊 **Category:** {category}

📝 **Description:** {description}

💼 **Business Use:** {business_use}

🔢 **Type:** {"Numeric" if any(word in column_lower for word in ['count', 'rate', 'total', 'avg', 'sum', 'amount', 'value']) else "Text/Category"}

💡 **Note:** This is a computed column from your SQL query
"""
    
    return tooltip

def create_visualization(df: pd.DataFrame, viz_type: str, columns_used: List[str]) -> None:
    """Create appropriate visualization based on data and type"""
    
    if df.empty:
        st.warning("No data to visualize")
        return
    
    try:
        st.subheader("📊 Data Visualization")
        
        # Check if viz_type is valid and we have enough columns
        if viz_type == "bar_chart" and len(df.columns) >= 2:
            # Find the best columns for visualization
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                
                fig = px.bar(df, x=x_col, y=y_col, 
                            title=f"{y_col} by {x_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Bar chart requires both categorical and numeric columns. Showing table instead.")
                st.dataframe(df, use_container_width=True)
            
        elif viz_type == "line_chart" and len(df.columns) >= 2:
            # Find numeric columns for line chart
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
                
                fig = px.line(df, x=x_col, y=y_col,
                             title=f"{y_col} trend over {x_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            elif len(numeric_cols) >= 1:
                # Use index as x-axis if only one numeric column
                y_col = numeric_cols[0]
                fig = px.line(df, y=y_col, title=f"{y_col} trend")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Line chart requires numeric columns. Showing table instead.")
                st.dataframe(df, use_container_width=True)
            
        elif viz_type == "pie_chart" and len(df.columns) >= 2:
            # Find appropriate columns for pie chart
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                names_col = categorical_cols[0]
                values_col = numeric_cols[0]
                
                # Aggregate data if needed
                pie_data = df.groupby(names_col)[values_col].sum().reset_index()
                
                fig = px.pie(pie_data, names=names_col, values=values_col,
                            title=f"Distribution of {values_col} by {names_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pie chart requires both categorical and numeric columns. Showing table instead.")
                st.dataframe(df, use_container_width=True)
                
        elif viz_type == "kpi" or viz_type == "metric":
            # Create KPI/Metric dashboard with large numbers and visual indicators
            st.subheader("📊 Key Performance Indicators")
            
            # Find numeric columns for KPIs
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            
            if len(numeric_cols) > 0:
                # If we have multiple rows, try to create a chart as well
                if len(df) > 1:
                    # Try to create a chart visualization
                    categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
                    
                    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                        st.write("**Visual Chart:**")
                        
                        # Automatically choose best chart type
                        if len(df) <= 10:  # Small dataset - use bar chart
                            x_col = categorical_cols[0] if categorical_cols else df.index
                            y_col = numeric_cols[0]
                            
                            fig = px.bar(df, x=x_col, y=y_col, 
                                        title=f"{y_col} by {x_col}")
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                            
                        else:  # Larger dataset - use line chart
                            y_col = numeric_cols[0]
                            fig = px.line(df, y=y_col, title=f"{y_col} Trend")
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                
                # Show KPI metrics
                st.write("**Key Metrics:**")
                
                # Calculate number of columns for layout
                num_kpis = min(len(numeric_cols), 4)  # Max 4 KPIs per row
                cols = st.columns(num_kpis)
                
                for idx, col in enumerate(numeric_cols[:4]):  # Show first 4 KPIs
                    with cols[idx % num_kpis]:
                        value = df[col].iloc[0] if len(df) == 1 else df[col].sum()
                        
                        # Format value based on column name
                        if col.upper().endswith('_M') or 'MILLION' in col.upper():
                            formatted_value = f"${value:.2f}M"
                        elif 'RATE' in col.upper() or 'PERCENT' in col.upper():
                            formatted_value = f"{value:.1f}%"
                        elif 'AMT' in col.upper() or 'VALUE' in col.upper():
                            formatted_value = f"${value:,.0f}"
                        elif 'COUNT' in col.upper() or col.upper().endswith('_COUNT'):
                            formatted_value = f"{value:,.0f}"
                        else:
                            formatted_value = f"{value:,.2f}"
                        
                        # Display as metric
                        st.metric(
                            label=col.replace('_', ' ').title(),
                            value=formatted_value
                        )
                
                # If more than 4 KPIs, show additional ones in a second row
                if len(numeric_cols) > 4:
                    st.write("")  # Add space
                    remaining_kpis = numeric_cols[4:8]  # Next 4 KPIs
                    cols2 = st.columns(len(remaining_kpis))
                    
                    for idx, col in enumerate(remaining_kpis):
                        with cols2[idx]:
                            value = df[col].iloc[0] if len(df) == 1 else df[col].sum()
                            
                            # Format value
                            if col.upper().endswith('_M') or 'MILLION' in col.upper():
                                formatted_value = f"${value:.2f}M"
                            elif 'RATE' in col.upper() or 'PERCENT' in col.upper():
                                formatted_value = f"{value:.1f}%"
                            elif 'AMT' in col.upper() or 'VALUE' in col.upper():
                                formatted_value = f"${value:,.0f}"
                            elif 'COUNT' in col.upper() or col.upper().endswith('_COUNT'):
                                formatted_value = f"{value:,.0f}"
                            else:
                                formatted_value = f"{value:,.2f}"
                            
                            st.metric(
                                label=col.replace('_', ' ').title(),
                                value=formatted_value
                            )
                
                # Show data table below KPIs
                if len(df) > 1:  # Only show table if there's more than one row
                    st.write("")
                    st.write("**Detailed Data:**")
                    st.dataframe(df, use_container_width=True)
                
            else:
                st.info("No numeric data available for KPI display. Showing table instead.")
                st.dataframe(df, use_container_width=True)
            
        else:
            # Auto-detect best visualization for unknown types or fallback
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            # Try to create an appropriate chart automatically
            if len(df) > 1 and len(numeric_cols) >= 1:
                if len(categorical_cols) >= 1:
                    # We have both categorical and numeric data
                    if len(df) <= 20:  # Small dataset - bar chart works well
                        st.write("**Auto-generated Bar Chart:**")
                        x_col = categorical_cols[0]
                        y_col = numeric_cols[0]
                        
                        fig = px.bar(df, x=x_col, y=y_col, 
                                    title=f"{y_col} by {x_col}")
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:  # Larger dataset - try grouping for better visualization
                        st.write("**Auto-generated Summary Chart:**")
                        x_col = categorical_cols[0]
                        y_col = numeric_cols[0]
                        
                        # Group and sum the data
                        grouped_df = df.groupby(x_col)[y_col].sum().reset_index()
                        
                        if len(grouped_df) <= 10:
                            fig = px.bar(grouped_df, x=x_col, y=y_col, 
                                        title=f"Total {y_col} by {x_col}")
                        else:
                            fig = px.line(grouped_df, x=x_col, y=y_col, 
                                         title=f"Total {y_col} by {x_col}")
                        
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                elif len(numeric_cols) >= 2:
                    # Multiple numeric columns - scatter or line plot
                    st.write("**Auto-generated Trend Chart:**")
                    x_col = numeric_cols[0]
                    y_col = numeric_cols[1]
                    
                    fig = px.scatter(df, x=x_col, y=y_col, 
                                    title=f"{y_col} vs {x_col}")
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    # Single numeric column - histogram or line trend
                    st.write("**Auto-generated Distribution:**")
                    y_col = numeric_cols[0]
                    
                    if len(df) > 10:
                        fig = px.histogram(df, x=y_col, title=f"Distribution of {y_col}")
                    else:
                        fig = px.line(df, y=y_col, title=f"{y_col} Values")
                    
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback message for unsupported visualization
                st.info(f"Chart visualization not available for this data type (visualization type: {viz_type}). Showing formatted table instead.")
            
            # Always show formatted table as well
            st.write("**Data Table:**")
            
            # Format numeric columns for better display
            formatted_df = df.copy()
            
            for col in numeric_cols:
                if col.upper().endswith('_M') or 'MILLION' in col.upper():
                    # Format as millions
                    formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:.2f}M" if pd.notnull(x) else "")
                elif 'RATE' in col.upper() or 'PERCENT' in col.upper():
                    # Format as percentage
                    formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
                elif 'AMT' in col.upper() or 'VALUE' in col.upper():
                    # Format as currency
                    formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
            
            st.dataframe(formatted_df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.write("Error details:", str(e))
        # Fallback to simple table
        st.dataframe(df, use_container_width=True)

def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="IBM Sales Pipeline Analytics Chat",
        page_icon="📊",
        layout="wide"
    )
    
    # Header with GitHub link
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🤖 IBM Sales Pipeline Analytics Chat")
        st.markdown("*Natural Language to SQL with Local LLM*")
    with col2:
        st.write("")  # Add space
        if st.button("📂 View on GitHub", key="github_repo"):
            if open_url_in_browser("https://github.com/Yerdna1/Text_to_SQL"):
                st.success("✅ Repository opened")
    
    # Initialize session state
    if 'data_dict' not in st.session_state:
        st.session_state.data_dict = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = None
    if 'llm_connector' not in st.session_state:
        st.session_state.llm_connector = None
    
    # Sidebar for setup
    with st.sidebar:
        st.header("⚙️ Setup")
        
        # Data Dictionary Upload
        st.subheader("📚 Data Dictionary")
        
        # Default dictionary path (can be overridden by environment variable)
        DEFAULT_DICT_PATH = os.environ.get(
            "DEFAULT_DICT_PATH", 
            "/Volumes/DATA/Python/IBM_analyza/IBM_COMPLETE_ALL_COLUMNS_Dictionary_20250710.xlsx"
        )
        
        # Checkbox to use default file
        use_default = st.checkbox(
            "Use default data dictionary",
            value=os.path.exists(DEFAULT_DICT_PATH),
            help=f"Use the default file: {os.path.basename(DEFAULT_DICT_PATH)}"
        )
        
        if use_default and os.path.exists(DEFAULT_DICT_PATH):
            st.session_state.selected_dict_path = DEFAULT_DICT_PATH
            st.success(f"✅ Using default dictionary: {os.path.basename(DEFAULT_DICT_PATH)}")
            dict_file = None  # No need for upload
        else:
            if TKINTER_AVAILABLE:
                col1, col2 = st.columns([3, 1])
                with col1:
                    dict_file = st.file_uploader(
                        "Upload IBM_COMPLETE_ALL_COLUMNS_Dictionary.xlsx",
                        type=['xlsx'],
                        help="Upload the complete data dictionary Excel file"
                    )
                with col2:
                    st.write("")  # Add some space
                    if st.button("📂 Browse", key="browse_dict"):
                        selected_file = browse_for_file(
                            title="Select Data Dictionary Excel File",
                            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
                        )
                        if selected_file:
                            st.session_state.selected_dict_path = selected_file
                            st.success(f"Selected: {os.path.basename(selected_file)}")
            else:
                dict_file = st.file_uploader(
                    "Upload IBM_COMPLETE_ALL_COLUMNS_Dictionary.xlsx",
                    type=['xlsx'],
                    help="Upload the complete data dictionary Excel file"
                )
                st.info("💡 **Alternative**: You can also specify a file path below:")
                manual_dict_path = st.text_input(
                    "Or enter full path to Excel file",
                    placeholder="/path/to/your/dictionary.xlsx",
                    help="Enter the complete file path to your data dictionary Excel file"
                )
                if manual_dict_path and os.path.exists(manual_dict_path) and manual_dict_path.endswith('.xlsx'):
                    st.session_state.selected_dict_path = manual_dict_path
                    st.success(f"✅ Valid Excel file: {os.path.basename(manual_dict_path)}")
                elif manual_dict_path:
                    st.error("❌ File not found or not an Excel file")
        
        # Display selected file path if browsed
        if hasattr(st.session_state, 'selected_dict_path'):
            st.info(f"📁 Selected file: {st.session_state.selected_dict_path}")
            if st.button("🗑️ Clear Selection", key="clear_dict"):
                del st.session_state.selected_dict_path
        
        # Auto-load knowledge base if not already loaded
        if st.session_state.data_dict is None:
            with st.spinner("Loading comprehensive knowledge base..."):
                excel_path = None
                
                if dict_file:
                    # Save uploaded file temporarily
                    temp_path = f"/tmp/{dict_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(dict_file.getbuffer())
                    excel_path = temp_path
                elif hasattr(st.session_state, 'selected_dict_path'):
                    # Use browsed file
                    excel_path = st.session_state.selected_dict_path
                
                if excel_path:
                    st.session_state.data_dict = DataDictionary(excel_path)
                else:
                    # Load knowledge base without Excel file
                    st.session_state.data_dict = DataDictionary()
        
        # Data Path
        st.subheader("📁 MQT Tables")
        
        # Add tabs for different data loading methods
        tab1, tab2 = st.tabs(["📁 Directory Path", "📤 Upload Files"])
        
        with tab1:
            st.write("**Load from directory containing CSV files:**")
            
            # Default MQT data path (can be overridden by environment variable)
            DEFAULT_MQT_PATH = os.environ.get(
                "DEFAULT_MQT_PATH",
                "/Volumes/DATA/Python/IBM_analyza/data_exports/20250709_215809/tables/"
            )
            
            # Checkbox to use default path
            use_default_mqt = st.checkbox(
                "Use default MQT data path",
                value=os.path.exists(DEFAULT_MQT_PATH),
                help=f"Use the default path: {DEFAULT_MQT_PATH}"
            )
            
            if use_default_mqt and os.path.exists(DEFAULT_MQT_PATH):
                data_path = DEFAULT_MQT_PATH
                st.success(f"✅ Using default MQT path: {data_path}")
            elif TKINTER_AVAILABLE:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    data_path = st.text_input(
                        "Path to MQT CSV files",
                        value=DEFAULT_MQT_PATH if not use_default_mqt else "",
                        help="Directory containing MQT CSV files"
                    )
                with col2:
                    st.write("")  # Add space
                    if st.button("📂 Browse", key="browse_data"):
                        selected_dir = browse_for_directory("Select MQT CSV Files Directory")
                        if selected_dir:
                            st.session_state.selected_data_path = selected_dir
                            st.success("✅ Selected")
                with col3:
                    st.write("")  # Add space  
                    if st.button("🌐 Open", key="open_data") and data_path:
                        if open_file_explorer(data_path):
                            st.success("✅ Opened")
            else:
                col1, col2 = st.columns([4, 1])
                with col1:
                    data_path = st.text_input(
                        "Path to MQT CSV files",
                        value=DEFAULT_MQT_PATH if not use_default_mqt else "",
                        help="Directory containing MQT CSV files"
                    )
                with col2:
                    st.write("")  # Add space  
                    if st.button("🌐 Open", key="open_data") and data_path:
                        if open_file_explorer(data_path):
                            st.success("✅ Opened")
        
        with tab2:
            st.write("**Upload MQT files directly:**")
            st.info("💡 Upload your MQT data files here. Supports both CSV and Excel formats.")
            
            uploaded_files = st.file_uploader(
                "Upload MQT CSV or Excel files",
                type=['csv', 'xlsx', 'xls'],
                accept_multiple_files=True,
                help="Upload one or more CSV or Excel files containing MQT data. File names should contain 'MQT' for best results."
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
                with st.expander("📁 Uploaded Files", expanded=True):
                    for file in uploaded_files:
                        file_type = "Excel" if file.name.endswith(('.xlsx', '.xls')) else "CSV"
                        file_size = f"{file.size / (1024*1024):.1f} MB" if file.size > 1024*1024 else f"{file.size / 1024:.1f} KB"
                        st.write(f"• **{file.name}** ({file_type}, {file_size})")
                
                # Store uploaded files in session state
                st.session_state.uploaded_mqt_files = uploaded_files
                
                st.warning("⚠️ **Next step**: Click '📤 Load Uploaded Files' button below to process these files.")
        
        # Display selected directory if browsed
        if hasattr(st.session_state, 'selected_data_path'):
            st.info(f"📁 Selected directory: {st.session_state.selected_data_path}")
            if st.button("🔄 Use Selected Path", key="use_selected_data"):
                # Update the text input by rerunning with new session state
                st.session_state.current_data_path = st.session_state.selected_data_path
                st.rerun()
        
        # Use selected path if available
        if hasattr(st.session_state, 'current_data_path'):
            data_path = st.session_state.current_data_path
        
        # Show available MQT files
        if os.path.exists(data_path):
            mqt_files = [f for f in os.listdir(data_path) if 'MQT' in f and f.endswith('.csv')]
            st.success(f"✅ Found {len(mqt_files)} MQT files")
            with st.expander("📁 Available MQT Files", expanded=False):
                for file in mqt_files[:5]:  # Show first 5
                    st.write(f"• {file}")
                if len(mqt_files) > 5:
                    st.write(f"... and {len(mqt_files) - 5} more files")
        else:
            st.error("❌ Path does not exist")
        
        # Load buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Load from directory (only show if path exists or uploaded files available)
            load_dir_available = hasattr(st.session_state, 'current_data_path') or os.path.exists(data_path)
            load_upload_available = hasattr(st.session_state, 'uploaded_mqt_files') and st.session_state.uploaded_mqt_files
            
            if st.button("🔄 Load from Directory", disabled=not load_dir_available):
                if load_dir_available:
                    with st.spinner("Loading tables from directory..."):
                        st.session_state.db_manager = DatabaseManager()
                        st.session_state.db_manager.load_mqt_tables(data_path)
        
        with col2:
            if st.button("📤 Load Uploaded Files", disabled=not load_upload_available):
                if load_upload_available:
                    with st.spinner("Loading uploaded files..."):
                        st.session_state.db_manager = DatabaseManager()
                        st.session_state.db_manager.load_uploaded_files(st.session_state.uploaded_mqt_files)
        
        with col3:
            if st.button("🎯 Load Demo Data"):
                with st.spinner("Creating demo data..."):
                    st.session_state.db_manager = DatabaseManager()
                    st.session_state.db_manager.create_demo_data()
        
        # LLM Setup
        st.subheader("🧠 LLM Provider")
        
        provider_choice = st.selectbox(
            "Choose LLM Provider",
            ["gemini", "deepseek", "openai", "anthropic", "mistral", "openrouter", "ollama"],
            help="🌟 Latest models: Gemini 2.5, DeepSeek R1, GPT-4o, Claude 3.5 Sonnet, OpenRouter"
        )
        
        # Parallel generation option
        parallel_mode = st.checkbox(
            "🔄 Generate with 3 LLMs in parallel (comparison mode)",
            help="Generate SQL with multiple models and compare results for accuracy validation"
        )
        
        # Parallel mode configuration
        if parallel_mode:
            st.info("🔧 **Parallel Mode Configuration**: Choose 3 models for comparison")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Model 1:**")
                provider1 = st.selectbox(
                    "Provider 1",
                    ["gemini", "deepseek", "openai", "anthropic", "mistral", "openrouter"],
                    key="provider1"
                )
                if provider1 == "gemini":
                    model1 = st.selectbox("Model 1", ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"], key="model1")
                elif provider1 == "deepseek":
                    model1 = st.selectbox("Model 1", ["deepseek-reasoner", "deepseek-chat"], key="model1")
                elif provider1 == "openai":
                    model1 = st.selectbox("Model 1", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], key="model1")
                elif provider1 == "anthropic":
                    model1 = st.selectbox("Model 1", ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"], key="model1")
                elif provider1 == "mistral":
                    model1 = st.selectbox("Model 1", ["mistral-medium-3", "pixtral-large", "mistral-large-2411"], key="model1")
                elif provider1 == "openrouter":
                    model1 = st.selectbox("Model 1", [
                        "anthropic/claude-3.5-sonnet:beta", 
                        "openai/gpt-4o-2024-11-20", 
                        "deepseek/deepseek-r1",
                        "meta-llama/llama-3.3-70b-instruct:free",
                        "mistralai/mistral-small-3.2-24b-instruct:free",
                        "moonshotai/kimi-dev-72b:free"
                    ], key="model1")
            
            with col2:
                st.write("**Model 2:**")
                provider2 = st.selectbox(
                    "Provider 2", 
                    ["deepseek", "gemini", "openai", "anthropic", "mistral", "openrouter"],
                    key="provider2"
                )
                if provider2 == "gemini":
                    model2 = st.selectbox("Model 2", ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"], key="model2")
                elif provider2 == "deepseek":
                    model2 = st.selectbox("Model 2", ["deepseek-reasoner", "deepseek-chat"], key="model2")
                elif provider2 == "openai":
                    model2 = st.selectbox("Model 2", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], key="model2")
                elif provider2 == "anthropic":
                    model2 = st.selectbox("Model 2", ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"], key="model2")
                elif provider2 == "mistral":
                    model2 = st.selectbox("Model 2", ["mistral-medium-3", "pixtral-large", "mistral-large-2411"], key="model2")
                elif provider2 == "openrouter":
                    model2 = st.selectbox("Model 2", [
                        "anthropic/claude-3.5-sonnet:beta", 
                        "openai/gpt-4o-2024-11-20", 
                        "deepseek/deepseek-r1",
                        "meta-llama/llama-3.3-70b-instruct:free",
                        "mistralai/mistral-small-3.2-24b-instruct:free",
                        "moonshotai/kimi-dev-72b:free"
                    ], key="model2")
            
            with col3:
                st.write("**Model 3:**")
                provider3 = st.selectbox(
                    "Provider 3",
                    ["openai", "gemini", "deepseek", "anthropic", "mistral", "openrouter"],
                    key="provider3"
                )
                if provider3 == "gemini":
                    model3 = st.selectbox("Model 3", ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"], key="model3")
                elif provider3 == "deepseek":
                    model3 = st.selectbox("Model 3", ["deepseek-reasoner", "deepseek-chat"], key="model3")
                elif provider3 == "openai":
                    model3 = st.selectbox("Model 3", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], key="model3")
                elif provider3 == "anthropic":
                    model3 = st.selectbox("Model 3", ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"], key="model3")
                elif provider3 == "mistral":
                    model3 = st.selectbox("Model 3", ["mistral-medium-3", "pixtral-large", "mistral-large-2411"], key="model3")
                elif provider3 == "openrouter":
                    model3 = st.selectbox("Model 3", [
                        "anthropic/claude-3.5-sonnet:beta", 
                        "openai/gpt-4o-2024-11-20", 
                        "deepseek/deepseek-r1",
                        "meta-llama/llama-3.3-70b-instruct:free",
                        "mistralai/mistral-small-3.2-24b-instruct:free",
                        "moonshotai/kimi-dev-72b:free"
                    ], key="model3")
            
            # Store parallel configurations in session state
            st.session_state.parallel_config = [
                {"provider": provider1, "model_name": model1},
                {"provider": provider2, "model_name": model2}, 
                {"provider": provider3, "model_name": model3}
            ]
        
        if provider_choice == "gemini":
            st.info("🌟 Google Gemini - Latest AI models with superior reasoning!")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                api_key = st.text_input(
                    "Gemini API Key",
                    value=os.environ.get("GEMINI_API_KEY", ""),
                    type="password",
                    help="Get your API key from: https://ai.google.dev/gemini-api"
                )
            with col2:
                st.write("")  # Add space
                if st.button("🌐 Get API Key", key="gemini_api"):
                    if open_url_in_browser("https://ai.google.dev/gemini-api"):
                        st.success("✅ Opened in browser")
            model_choice = st.selectbox(
                "Gemini Model",
                ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
                help="🚀 gemini-2.5-pro (March 2025) - Latest with enhanced reasoning"
            )
            
            if st.button("🔗 Connect to Gemini API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="gemini", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.gemini_key = api_key
                else:
                    st.error("Please enter your Gemini API key")
        
        elif provider_choice == "deepseek":
            st.info("🚀 DeepSeek - Ultra-efficient reasoning models at 90% lower cost!")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                api_key = st.text_input(
                    "DeepSeek API Key",
                    value=os.environ.get("DEEPSEEK_API_KEY", ""),
                    type="password",
                    help="Get your API key from: https://platform.deepseek.com"
                )
            with col2:
                st.write("")  # Add space
                if st.button("🌐 Get API Key", key="deepseek_api"):
                    if open_url_in_browser("https://platform.deepseek.com"):
                        st.success("✅ Opened in browser")
            model_choice = st.selectbox(
                "DeepSeek Model",
                ["deepseek-reasoner", "deepseek-chat"],
                help="🧠 deepseek-reasoner (R1-0528) - Best for complex reasoning tasks"
            )
            
            if st.button("🔗 Connect to DeepSeek API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="deepseek", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.deepseek_key = api_key
                else:
                    st.error("Please enter your DeepSeek API key")
        
        elif provider_choice == "openai":
            st.info("🤖 OpenAI - Industry-leading GPT models with latest reasoning capabilities!")
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Get your API key from: https://platform.openai.com/api-keys"
            )
            model_choice = st.selectbox(
                "OpenAI Model",
                ["o3", "o3-pro", "o4-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"],
                help="🎯 o3 (2025) - Latest reasoning model for complex queries"
            )
            
            if st.button("🔗 Connect to OpenAI API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="openai", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.openai_key = api_key
                else:
                    st.error("Please enter your OpenAI API key")
        
        elif provider_choice == "anthropic":
            st.info("🧠 Anthropic Claude - Advanced reasoning with superior code understanding!")
            api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                help="Get your API key from: https://console.anthropic.com"
            )
            model_choice = st.selectbox(
                "Claude Model",
                ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
                help="💡 claude-3-5-sonnet - Best for complex SQL generation"
            )
            
            if st.button("🔗 Connect to Claude API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="anthropic", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.anthropic_key = api_key
                else:
                    st.error("Please enter your Anthropic API key")
        
        elif provider_choice == "mistral":
            st.info("⚡ Mistral AI - High-performance models with multimodal capabilities!")
            api_key = st.text_input(
                "Mistral API Key",
                type="password",
                help="Get your API key from: https://console.mistral.ai"
            )
            model_choice = st.selectbox(
                "Mistral Model",
                ["mistral-medium-3", "pixtral-large", "mistral-large-2411", "codestral-2501"],
                help="🔥 mistral-medium-3 (May 2025) - 8x cheaper with excellent performance"
            )
            
            if st.button("🔗 Connect to Mistral API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="mistral", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.mistral_key = api_key
                else:
                    st.error("Please enter your Mistral API key")
        
        elif provider_choice == "openrouter":
            st.info("🌐 OpenRouter - Access to 200+ models including latest GPT, Claude, and open source!")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                api_key = st.text_input(
                    "OpenRouter API Key",
                    value=os.environ.get("OPENROUTER_API_KEY", ""),
                    type="password",
                    help="Get your API key from: https://openrouter.ai/keys"
                )
            with col2:
                st.write("")  # Add space
                if st.button("🌐 Get API Key", key="openrouter_api"):
                    if open_url_in_browser("https://openrouter.ai/keys"):
                        st.success("✅ Opened in browser")
            model_choice = st.selectbox(
                "OpenRouter Model",
                [
                    "anthropic/claude-3.5-sonnet:beta",
                    "openai/gpt-4o-2024-11-20",
                    "deepseek/deepseek-r1",
                    "google/gemini-2.0-flash-exp",
                    "meta-llama/llama-3.3-70b-instruct",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "mistralai/mistral-small-3.2-24b-instruct:free",
                    "moonshotai/kimi-dev-72b:free",
                    "qwen/qwq-32b-preview",
                    "nvidia/llama-3.1-nemotron-70b-instruct"
                ],
                help="🚀 Choose from the latest and most powerful models (including FREE options!)"
            )
            
            if st.button("🔗 Connect to OpenRouter API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="openrouter", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.openrouter_key = api_key
                else:
                    st.error("Please enter your OpenRouter API key")
        
        elif provider_choice == "ollama":  # ollama
            st.warning("⚠️ Local models may have limited SQL generation quality")
            model_choice = st.selectbox(
                "Ollama Model",
                ["llama3.2:latest", "codellama:7b-instruct", "qwen2.5-coder:7b", "deepseek-coder:6.7b"],
                help="Make sure Ollama is running: ollama serve"
            )
            
            if st.button("🔗 Connect to Ollama"):
                st.session_state.llm_connector = LLMConnector(
                    provider="ollama", model_name=model_choice
                )
        
        # Status
        st.subheader("📊 Status")
        if st.session_state.data_dict:
            st.success("✅ Data Dictionary Loaded")
        if st.session_state.db_manager:
            st.success(f"✅ {len(st.session_state.db_manager.tables_loaded)} Tables Loaded")
        if st.session_state.llm_connector:
            st.success("✅ LLM Connected")
        
        # Browser capabilities status
        if TKINTER_AVAILABLE:
            st.success("✅ File Browser Available")
        else:
            st.warning("⚠️ File Browser Unavailable (tkinter missing)")
    
    # Main chat interface
    if all([st.session_state.data_dict, st.session_state.db_manager, st.session_state.llm_connector]):
        
        st.header("💬 Ask Questions About Your Sales Pipeline")
        
        # Example questions
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - "What is the total pipeline value by geography?"
            - "Show me win rates by market segment"
            - "Which clients have the largest opportunities?"
            - "What's the PPV coverage vs budget?"
            - "Show pipeline by sales stage"
            - "Compare this quarter vs last quarter performance"
            """)
        
        # Chat input
        question = st.text_input(
            "Ask your question:",
            placeholder="e.g., What is the total pipeline value by geography?",
            key="question_input"
        )
        
        if st.button("🚀 Generate Query") and question:
            
            # Prepare comprehensive context for LLM
            schema_info = st.session_state.db_manager.schema_info
            comprehensive_context = st.session_state.data_dict.get_comprehensive_context()
            
            if parallel_mode:
                # Parallel generation with 3 LLMs
                with st.spinner("🧠 Generating SQL with 3 LLMs in parallel..."):
                    
                    # Use user-selected provider configurations for parallel generation
                    def get_api_key(provider):
                        """Get API key from session state or environment variables"""
                        if provider == "gemini":
                            return st.session_state.get("gemini_key", os.environ.get("GEMINI_API_KEY", ""))
                        elif provider == "deepseek":
                            return st.session_state.get("deepseek_key", os.environ.get("DEEPSEEK_API_KEY", ""))
                        elif provider == "openai":
                            return st.session_state.get("openai_key", os.environ.get("OPENAI_API_KEY", ""))
                        elif provider == "anthropic":
                            return st.session_state.get("anthropic_key", os.environ.get("ANTHROPIC_API_KEY", ""))
                        elif provider == "mistral":
                            return st.session_state.get("mistral_key", os.environ.get("MISTRAL_API_KEY", ""))
                        elif provider == "openrouter":
                            return st.session_state.get("openrouter_key", os.environ.get("OPENROUTER_API_KEY", ""))
                        return ""
                    
                    # Get parallel configurations from session state or use defaults
                    if hasattr(st.session_state, 'parallel_config'):
                        parallel_providers = []
                        for config in st.session_state.parallel_config:
                            provider_config = {
                                "provider": config["provider"],
                                "model_name": config["model_name"],
                                "api_key": get_api_key(config["provider"])
                            }
                            parallel_providers.append(provider_config)
                    else:
                        # Default configuration if no user selection
                        parallel_providers = [
                            {"provider": "gemini", "model_name": "gemini-2.5-pro", "api_key": os.environ.get("GEMINI_API_KEY", "")},
                            {"provider": "deepseek", "model_name": "deepseek-reasoner", "api_key": os.environ.get("DEEPSEEK_API_KEY", "")},
                            {"provider": "openai", "model_name": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY", "")}
                        ]
                    
                    parallel_generator = ParallelSQLGenerator(parallel_providers)
                    parallel_result = parallel_generator.generate_parallel(
                        question, schema_info, comprehensive_context
                    )
                    
                    # Store parallel results
                    st.session_state.query_result = parallel_result
                    st.session_state.current_question = question
                    st.session_state.parallel_mode = True
            else:
                # Single LLM generation
                with st.spinner("🧠 Generating SQL query..."):
                    result = st.session_state.llm_connector.generate_sql(
                        question, schema_info, comprehensive_context
                    )
                    
                    # Store result in session state
                    st.session_state.query_result = result
                    st.session_state.current_question = question
                    st.session_state.parallel_mode = False
        
        # Display results if we have them
        if hasattr(st.session_state, 'query_result') and st.session_state.query_result:
            result = st.session_state.query_result
            
            if st.session_state.get('parallel_mode', False):
                # Display parallel results with comparison
                st.subheader("🔄 Parallel Generation Results")
                
                # Display comparison summary
                comparison = result.get('comparison', {})
                if comparison.get('overall_similarity'):
                    st.success("✅ **HIGH CONFIDENCE**: All 3 LLMs generated similar SQL queries!")
                elif comparison.get('confidence_level') == 'MEDIUM':
                    st.warning("⚠️ **MEDIUM CONFIDENCE**: Some similarities between queries")
                else:
                    st.error("❌ **LOW CONFIDENCE**: LLMs generated different queries")
                
                # Show detailed comparison
                with st.expander("📊 Detailed Comparison Analysis"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("SELECT Match", "✅" if comparison.get('select_match') else "❌")
                    with col2:
                        st.metric("FROM Match", "✅" if comparison.get('from_match') else "❌")  
                    with col3:
                        st.metric("WHERE Similarity", "✅" if comparison.get('where_similarity') else "❌")
                
                # Display individual results
                st.subheader("🤖 Individual LLM Results")
                
                individual_results = result.get('results', [])
                for i, llm_result in enumerate(individual_results):
                    with st.expander(f"🧠 {llm_result.get('provider', 'Unknown').title()} - {llm_result.get('model', 'Unknown')} ({llm_result.get('generation_time', 0)}s)"):
                        if llm_result.get('error'):
                            st.error(f"❌ Error: {llm_result['error']}")
                        else:
                            st.code(llm_result.get('sql_query', ''), language='sql')
                            st.write("**Explanation:**", llm_result.get('explanation', 'No explanation'))
                
                # Use best result for execution
                best_result = result.get('best_result', {})
                if best_result:
                    st.subheader("🏆 Best Result (Selected for Execution)")
                    st.info(f"**Selected:** {best_result.get('provider', 'Unknown').title()} - {best_result.get('model', 'Unknown')}")
                    st.code(best_result.get('sql_query', ''), language='sql')
                    
                    # Execute best query button
                    if st.button("▶️ Execute Best Query", key="execute_parallel_btn"):
                        if not st.session_state.db_manager.tables_loaded:
                            st.error("❌ No tables loaded! Please load MQT tables first in the sidebar.")
                        else:
                            with st.spinner("Executing best query..."):
                                try:
                                    df = st.session_state.db_manager.execute_query(best_result.get('sql_query', ''))
                                    
                                    if not df.empty:
                                        st.subheader("📊 Results")
                                        st.success(f"✅ Query executed successfully! Found {len(df)} rows.")
                                        
                                        # Show results first
                                        st.dataframe(df, use_container_width=True)
                                        
                                        # Add hover explanations for columns
                                        columns_info = {}
                                        for col in df.columns:
                                            columns_info[col] = create_hover_tooltip(col, st.session_state.data_dict)
                                        
                                        # Display with tooltips
                                        with st.expander("ℹ️ Column Explanations", expanded=False):
                                            for col, tooltip in columns_info.items():
                                                st.markdown(tooltip)
                                        
                                        # Create visualization
                                        try:
                                            create_visualization(
                                                df, 
                                                best_result.get('visualization_type', 'table'),
                                                best_result.get('columns_used', [])
                                            )
                                        except Exception as viz_error:
                                            st.warning(f"Visualization failed: {viz_error}")
                                    else:
                                        st.warning("⚠️ Query returned no results")
                                        
                                except Exception as e:
                                    st.error(f"❌ Query execution failed: {e}")
                                    st.code(best_result.get('sql_query', ''), language='sql')
                
            else:
                # Display single LLM results  
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("🔍 Generated Query")
                    st.code(result.get('sql_query', ''), language='sql')
                    
                    st.subheader("💡 Explanation")
                    st.write(result.get('explanation', 'No explanation available'))
                    
                    # Execute query button (now independent)
                    if st.button("▶️ Execute Query", key="execute_btn"):
                        if not st.session_state.db_manager.tables_loaded:
                            st.error("❌ No tables loaded! Please load MQT tables first in the sidebar.")
                        else:
                            with st.spinner("Executing query..."):
                                try:
                                    df = st.session_state.db_manager.execute_query(result.get('sql_query', ''))
                                    
                                    if not df.empty:
                                        st.subheader("📊 Results")
                                        st.success(f"✅ Query executed successfully! Found {len(df)} rows.")
                                        
                                        # Show results first
                                        st.dataframe(df, use_container_width=True)
                                        
                                        # Add hover explanations for columns
                                        columns_info = {}
                                        for col in df.columns:
                                            columns_info[col] = create_hover_tooltip(col, st.session_state.data_dict)
                                        
                                        # Display with tooltips
                                        with st.expander("ℹ️ Column Explanations", expanded=False):
                                            for col, tooltip in columns_info.items():
                                                st.markdown(tooltip)
                                        
                                        # Create visualization
                                        try:
                                            create_visualization(
                                                df, 
                                                result.get('visualization_type', 'table'),
                                                result.get('columns_used', [])
                                            )
                                        except Exception as viz_error:
                                            st.warning(f"Visualization error: {viz_error}")
                                    else:
                                        st.warning("⚠️ Query returned no results. Try a different question or check your data.")
                                        
                                except Exception as e:
                                    st.error(f"❌ Query execution failed: {e}")
                                    st.info("💡 This might be because:")
                                    st.write("- Column names don't match your actual data")
                                    st.write("- Tables aren't loaded properly")
                                    st.write("- SQL syntax needs adjustment for SQLite")
                
                with col2:
                    st.subheader("📋 Query Details")
                
                    st.write("**Tables Used:**")
                    for table in result.get('tables_used', []):
                        st.write(f"• {table}")
                    
                    st.write("**Columns Used:**")
                    for col in result.get('columns_used', []):
                        with st.expander(f"📊 {col}", expanded=False):
                            info = st.session_state.data_dict.get_column_info(col)
                            if info:
                                st.write(f"**Description:** {info.get('description', 'N/A')}")
                                st.write(f"**Slovak:** {info.get('slovak_description', 'N/A')}")
                                st.write(f"**Business Use:** {info.get('business_use', 'N/A')}")
                    
                    confidence = result.get('confidence', 0)
                    st.metric("Confidence", f"{confidence:.1%}")
                    
                    # Add clear query button
                    if st.button("🗑️ Clear Query", key="clear_btn"):
                        if 'query_result' in st.session_state:
                            del st.session_state.query_result
                        if 'current_question' in st.session_state:
                            del st.session_state.current_question
                        st.rerun()
    
    else:
        st.info("👆 Please complete the setup in the sidebar to start asking questions!")
        
        st.markdown("""
        ### 🚀 Setup Instructions:
        
        1. **Upload Data Dictionary**: Upload the IBM_COMPLETE_ALL_COLUMNS_Dictionary.xlsx file
        2. **Load MQT Tables**: Point to the directory with your MQT CSV files
        3. **Connect LLM**: Make sure Ollama is running locally
        
        ### 📋 Prerequisites:
        
        ```bash
        # Install Ollama
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Download a model
        ollama pull codellama
        
        # Start Ollama service
        ollama serve
        ```
        
        ### 🎯 Features:
        
        - 🤖 **Natural Language to SQL** using local LLM
        - 📚 **Smart Knowledge Base** from complete data dictionary
        - 🖱️ **Hover Explanations** for all columns
        - 📊 **Auto Visualizations** based on query results
        - 🔒 **Privacy Focused** - everything runs locally
        """)

if __name__ == "__main__":
    main()