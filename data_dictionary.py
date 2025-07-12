#!/usr/bin/env python3
"""
Data Dictionary Manager for IBM Sales Pipeline Analytics
Manages complete data dictionary and knowledge base
"""

import pandas as pd
import streamlit as st
import os
from typing import Dict, List


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