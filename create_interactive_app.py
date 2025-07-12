#!/usr/bin/env python3
"""
Interactive IBM Sales Pipeline Analytics Chat Application
with Natural Language to SQL conversion using local LLM
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple
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

# Import modular components
from data_dictionary import DataDictionary
from database_manager import DatabaseManager
from llm_connector import LLMConnector
from visualization_utils import create_hover_tooltip, create_visualization

# Import the agent orchestrator and receptionist
try:
    from agents import process_with_agents, SQLAgentOrchestrator
    from receptionist_agent import ReceptionistAgent, create_step_visualization
    AGENTS_AVAILABLE = True
    RECEPTIONIST_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    RECEPTIONIST_AVAILABLE = False
    print("Warning: SQL Agent Orchestrator and Receptionist not available")


# Utility functions
def browse_for_directory(title="Select Directory"):
    """Open a directory browser dialog"""
    if not TKINTER_AVAILABLE:
        st.warning("⚠️ File browser not available. Please enter path manually.")
        return None
        
    try:
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Open directory dialog
        directory = filedialog.askdirectory(title=title)
        root.destroy()
        
        return directory if directory else None
        
    except Exception as e:
        st.error(f"Browser error: {e}")
        return None


def browse_for_file(title="Select File", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]):
    """Open a file browser dialog"""
    if not TKINTER_AVAILABLE:
        st.warning("⚠️ File browser not available. Please enter path manually.")
        return None
        
    try:
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Open file dialog
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        root.destroy()
        
        return file_path if file_path else None
        
    except Exception as e:
        st.error(f"Browser error: {e}")
        return None


def open_url_in_browser(url):
    """Open URL in web browser"""
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def open_file_explorer(path):
    """Open file explorer/finder for the given path"""
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        elif platform.system() == "Windows":  # Windows
            subprocess.run(["explorer", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
        return True
    except Exception:
        return False


class ParallelSQLGenerator:
    """Generate SQL with multiple LLMs in parallel for comparison"""
    
    def __init__(self, providers_config: List[Dict]):
        """
        providers_config: List of dicts with keys: provider, model_name, api_key
        """
        self.providers_config = providers_config
        self.llm_connectors = []
        
        # Initialize LLM connectors
        for config in providers_config:
            try:
                connector = LLMConnector(
                    provider=config["provider"],
                    model_name=config["model_name"],
                    api_key=config.get("api_key", "")
                )
                if connector.connected:
                    self.llm_connectors.append({
                        "connector": connector,
                        "provider": config["provider"],
                        "model": config["model_name"]
                    })
            except Exception as e:
                st.warning(f"Failed to initialize {config['provider']}: {e}")
    
    def generate_parallel(self, question: str, schema_info: str, data_dictionary: str) -> Dict:
        """Generate SQL with all available LLMs in parallel"""
        import concurrent.futures
        import time
        
        if not self.llm_connectors:
            return {"error": "No LLM connectors available"}
        
        def generate_with_llm(llm_info):
            """Generate SQL with a single LLM"""
            start_time = time.time()
            try:
                result = llm_info["connector"].generate_sql(question, schema_info, data_dictionary)
                result["provider"] = llm_info["provider"]
                result["model"] = llm_info["model"]
                result["generation_time"] = round(time.time() - start_time, 2)
                return result
            except Exception as e:
                return {
                    "error": str(e),
                    "provider": llm_info["provider"],
                    "model": llm_info["model"],
                    "generation_time": round(time.time() - start_time, 2)
                }
        
        # Execute in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.llm_connectors)) as executor:
            future_to_llm = {executor.submit(generate_with_llm, llm_info): llm_info for llm_info in self.llm_connectors}
            
            for future in concurrent.futures.as_completed(future_to_llm):
                result = future.result()
                results.append(result)
        
        # Analyze and compare results
        comparison = self._compare_results(results)
        best_result = self._select_best_result(results)
        
        return {
            "results": results,
            "comparison": comparison,
            "best_result": best_result,
            "total_llms": len(results),
            "successful_generations": len([r for r in results if not r.get("error")])
        }
    
    def _compare_results(self, results: List[Dict]) -> Dict:
        """Compare SQL results for similarity"""
        valid_results = [r for r in results if not r.get("error") and r.get("sql_query")]
        
        if len(valid_results) < 2:
            return {"confidence_level": "LOW", "reason": "Insufficient valid results for comparison"}
        
        # Extract key components from SQL queries
        queries = [r["sql_query"].upper() for r in valid_results]
        
        # Compare SELECT clauses
        select_clauses = []
        for query in queries:
            if "SELECT" in query and "FROM" in query:
                select_part = query[query.find("SELECT"):query.find("FROM")].strip()
                select_clauses.append(select_part)
        
        select_match = len(set(select_clauses)) == 1 if select_clauses else False
        
        # Compare FROM clauses
        from_clauses = []
        for query in queries:
            if "FROM" in query:
                from_part = query[query.find("FROM"):].split("WHERE")[0].split("GROUP")[0].split("ORDER")[0].strip()
                from_clauses.append(from_part)
        
        from_match = len(set(from_clauses)) == 1 if from_clauses else False
        
        # Overall similarity assessment
        if select_match and from_match:
            confidence = "HIGH"
            overall_similarity = True
        elif select_match or from_match:
            confidence = "MEDIUM"
            overall_similarity = False
        else:
            confidence = "LOW"
            overall_similarity = False
        
        return {
            "confidence_level": confidence,
            "overall_similarity": overall_similarity,
            "select_match": select_match,
            "from_match": from_match,
            "where_similarity": True,  # Simplified for now
            "total_compared": len(valid_results)
        }
    
    def _select_best_result(self, results: List[Dict]) -> Dict:
        """Select the best result based on various criteria"""
        valid_results = [r for r in results if not r.get("error") and r.get("sql_query")]
        
        if not valid_results:
            return results[0] if results else {}
        
        # Simple scoring based on explanation length and confidence
        best_result = None
        best_score = 0
        
        for result in valid_results:
            score = 0
            
            # Prefer results with higher confidence
            score += result.get("confidence", 0) * 100
            
            # Prefer results with better explanations
            explanation_length = len(result.get("explanation", ""))
            score += min(explanation_length / 10, 20)  # Cap at 20 points
            
            # Prefer faster generation (slight bonus)
            generation_time = result.get("generation_time", 10)
            score += max(0, 10 - generation_time)  # Bonus for faster generation
            
            # Provider preferences (Gemini, DeepSeek, OpenAI get slight bonus)
            preferred_providers = ["gemini", "deepseek", "openai"]
            if result.get("provider") in preferred_providers:
                score += 5
            
            if score > best_score:
                best_score = score
                best_result = result
        
        return best_result or valid_results[0]


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
            help="Generate SQL with multiple models and compare results for accuracy validation. Multi-agent enhancement will be applied to the best result."
        )
        
        # LLM provider configuration (simplified)
        if provider_choice == "gemini":
            st.info("🌟 Google Gemini - Latest AI models with superior reasoning!")
            api_key = st.text_input(
                "Gemini API Key",
                value=os.environ.get("GEMINI_API_KEY", ""),
                type="password",
                help="Get your API key from: https://ai.google.dev/gemini-api"
            )
            model_choice = st.selectbox(
                "Gemini Model",
                ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
                help="🚀 gemini-2.5-pro - Latest with enhanced reasoning"
            )
            
            if st.button("🔗 Connect to Gemini API"):
                if api_key:
                    st.session_state.llm_connector = LLMConnector(
                        provider="gemini", model_name=model_choice, api_key=api_key
                    )
                    st.session_state.gemini_key = api_key
                else:
                    st.error("Please enter your Gemini API key")
        
        # Add other provider configurations here (abbreviated for space)
        # ... similar blocks for deepseek, openai, anthropic, mistral, openrouter, ollama
        
        # Status
        st.subheader("📊 Status")
        if st.session_state.data_dict:
            st.success("✅ Data Dictionary Loaded")
        if st.session_state.db_manager:
            st.success(f"✅ {len(st.session_state.db_manager.tables_loaded)} Tables Loaded")
        if st.session_state.llm_connector:
            st.success("✅ LLM Connected")
        
        # Multi-Agent Configuration
        st.subheader("🤖 Multi-Agent System")
        enable_agents = st.checkbox(
            "Enable Multi-Agent SQL Enhancement",
            value=True,
            help="Use AI agents to validate DB2 syntax, enhance WHERE clauses, and optimize queries"
        )
        st.session_state.enable_agents = enable_agents
        
        if enable_agents and AGENTS_AVAILABLE:
            st.success("✅ Multi-Agent System: Active")
        elif enable_agents and not AGENTS_AVAILABLE:
            st.error("❌ Multi-Agent System: Import Error")
        else:
            st.info("ℹ️ Multi-Agent System: Disabled")
    
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
            
            # Single LLM generation
            with st.spinner("🧠 Generating SQL query..."):
                result = st.session_state.llm_connector.generate_sql(
                    question, schema_info, comprehensive_context
                )
                
                # Process with agent orchestration if available and enabled
                if AGENTS_AVAILABLE and st.session_state.get('enable_agents', True) and result.get('sql_query'):
                    with st.spinner("🤖 Processing with multi-agent system..."):
                        agent_result = process_with_agents(
                            sql_query=result.get('sql_query', ''),
                            question=question,
                            db_manager=st.session_state.db_manager,
                            data_dict=st.session_state.data_dict,
                            db_type=st.session_state.get('db_type', 'DB2'),
                            llm_connector=st.session_state.llm_connector
                        )
                        
                        if agent_result['success']:
                            # Update the result with enhanced query
                            result['original_query'] = result['sql_query']
                            result['sql_query'] = agent_result['final_query']
                            result['agent_processing'] = agent_result
                
                # Store result in session state
                st.session_state.query_result = result
                st.session_state.current_question = question
        
        # Display results if we have them
        if hasattr(st.session_state, 'query_result') and st.session_state.query_result:
            result = st.session_state.query_result
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🔍 Generated Query")
                st.code(result.get('sql_query', ''), language='sql')
                
                # Show agent processing details if available
                if result.get('agent_processing'):
                    with st.expander("🤖 Multi-Agent Processing Details", expanded=False):
                        if result.get('agent_processing', {}).get('processing_log'):
                            create_step_visualization(result['agent_processing']['processing_log'])
                
                st.subheader("💡 Explanation")
                st.write(result.get('explanation', 'No explanation available'))
                
                # Execute query button
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
                                    
                                    # Show results
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # Add hover explanations for columns
                                    with st.expander("ℹ️ Column Explanations", expanded=False):
                                        for col in df.columns:
                                            tooltip = create_hover_tooltip(col, st.session_state.data_dict)
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
                                    st.warning("⚠️ Query returned no results.")
                                    
                            except Exception as e:
                                st.error(f"❌ Query execution failed: {e}")
                                st.code(result.get('sql_query', ''), language='sql')
            
            with col2:
                st.subheader("📋 Query Details")
            
                st.write("**Tables Used:**")
                for table in result.get('tables_used', []):
                    st.write(f"• {table}")
                
                st.write("**Columns Used:**")
                for col in result.get('columns_used', []):
                    info = st.session_state.data_dict.get_column_info(col)
                    if info:
                        st.write(f"• **{col}**")
                        st.write(f"  - {info.get('description', 'No description available')}")
                    else:
                        st.write(f"• {col}")
                
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
        3. **Connect LLM**: Choose your preferred LLM provider
        
        ### 🎯 Features:
        
        - 🤖 **Natural Language to SQL** using local/cloud LLM
        - 📚 **Smart Knowledge Base** from complete data dictionary
        - 🖱️ **Hover Explanations** for all columns
        - 📊 **Auto Visualizations** based on query results
        - 🤖 **Multi-Agent Enhancement** for better SQL quality
        """)


if __name__ == "__main__":
    main()