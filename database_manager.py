#!/usr/bin/env python3
"""
Database Manager for IBM Sales Pipeline Analytics
Manages database connections, schema, and demo data generation
"""

import sqlite3
import pandas as pd
import streamlit as st
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List

# DB2 connection support
try:
    import ibm_db
    import ibm_db_dbi
    DB2_AVAILABLE = True
except ImportError:
    DB2_AVAILABLE = False


class DatabaseManager:
    """Manages database connections and MQT table loading"""
    
    def __init__(self):
        self.conn = None
        self.db_type = "SQLite"  # Default fallback
        self.connection_string = ""
        self.tables_loaded = {}
        self.schema_info = ""
        self._init_default_connection()
    
    def _init_default_connection(self):
        """Initialize default SQLite connection"""
        try:
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.db_type = "SQLite"
        except Exception as e:
            st.error(f"Failed to initialize SQLite connection: {e}")
    
    def connect_to_db2(self, hostname: str, port: int, database: str, username: str, password: str, ssl: bool = True):
        """Connect to IBM DB2 database"""
        if not DB2_AVAILABLE:
            st.error("❌ IBM DB2 driver not installed. Please install: pip install ibm-db")
            return False
        
        try:
            # Build DB2 connection string
            protocol = "TCPIP"
            ssl_param = "Security=SSL;" if ssl else ""
            self.connection_string = f"DATABASE={database};HOSTNAME={hostname};PORT={port};PROTOCOL={protocol};UID={username};PWD={password};{ssl_param}"
            
            # Test connection
            conn_handle = ibm_db.connect(self.connection_string, "", "")
            if conn_handle:
                self.conn = ibm_db_dbi.Connection(conn_handle)
                self.db_type = "DB2"
                st.success(f"✅ Connected to IBM DB2: {hostname}:{port}/{database}")
                
                # Get schema information
                self._refresh_db2_schema()
                return True
            else:
                st.error("❌ Failed to connect to DB2 database")
                return False
                
        except Exception as e:
            st.error(f"❌ DB2 Connection Error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from current database"""
        try:
            if self.conn and self.db_type == "DB2":
                self.conn.close()
            elif self.conn and self.db_type == "SQLite":
                self.conn.close()
            self.conn = None
            st.info("🔌 Database disconnected")
        except Exception as e:
            st.warning(f"Disconnect warning: {e}")
    
    def _refresh_db2_schema(self):
        """Refresh schema information from DB2"""
        try:
            cursor = self.conn.cursor()
            
            # Get list of MQT tables
            cursor.execute("""
                SELECT TABSCHEMA, TABNAME, TYPE 
                FROM SYSCAT.TABLES 
                WHERE TABNAME LIKE '%MQT%' 
                   OR TABNAME LIKE 'PROD_MQT%'
                ORDER BY TABSCHEMA, TABNAME
            """)
            
            tables = cursor.fetchall()
            self.schema_info = f"Connected to DB2 - Found {len(tables)} MQT tables:\\n"
            
            for schema, table, table_type in tables:
                self.schema_info += f"- {schema}.{table} ({table_type})\\n"
                
                # Get column information for each table
                cursor.execute("""
                    SELECT COLNAME, TYPENAME, LENGTH, SCALE 
                    FROM SYSCAT.COLUMNS 
                    WHERE TABSCHEMA = ? AND TABNAME = ?
                    ORDER BY COLNO
                """, (schema, table))
                
                columns = cursor.fetchall()
                self.tables_loaded[f"{schema}.{table}"] = {
                    "columns": [col[0] for col in columns],
                    "rows": "Unknown",  # Would need COUNT query
                    "schema": schema,
                    "table": table
                }
            
            cursor.close()
            st.success(f"📊 Schema refreshed: {len(self.tables_loaded)} tables loaded")
            
        except Exception as e:
            st.error(f"Schema refresh error: {e}")
    
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
        
        self.schema_info = "\\n".join(schema_parts)
    
    def create_demo_data(self):
        """Create demo data for testing when actual files aren't available"""
        st.info("📁 Creating demo MQT data...")
        
        # Create demo PROD_MQT_CONSULTING_PIPELINE data
        demo_data_consulting = {
            'OPPORTUNITY_ID': [f'OPP_{i:05d}' for i in range(1, 101)],
            'CLIENT_NAME': [random.choice(['IBM Corp', 'Microsoft', 'Oracle', 'SAP', 'Salesforce', 'Adobe', 'Cisco', 'Dell', 'HP Inc', 'VMware']) for _ in range(100)],
            'ACCOUNT_NAME': [random.choice(['IBM Corp', 'Microsoft', 'Oracle', 'SAP', 'Salesforce', 'Adobe', 'Cisco', 'Dell', 'HP Inc', 'VMware']) for _ in range(100)],
            'GEOGRAPHY': [random.choice(['Americas', 'EMEA', 'APAC', 'Japan']) for _ in range(100)],
            'MARKET': [random.choice(['Financial Services', 'Healthcare', 'Retail', 'Technology']) for _ in range(100)],
            'SALES_STAGE': [random.choice(['Qualify', 'Propose', 'Negotiate', 'Won', 'Lost']) for _ in range(100)],
            'OPPORTUNITY_VALUE': [random.randint(50000, 5000000) for _ in range(100)],
            'OPEN_PIPELINE': [random.randint(50000, 5000000) for _ in range(100)],
            'OPEN_PIPELINE_AMT': [random.randint(50000, 5000000) for _ in range(100)],
            'PPV_AMT': [random.randint(40000, 4500000) for _ in range(100)],
            'OPPORTUNITY_CREATE_DATE': [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d') for _ in range(100)],
            'CLOSE_DATE': [(datetime.now() + timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d') for _ in range(100)]
        }
        
        df_consulting = pd.DataFrame(demo_data_consulting)
        df_consulting.to_sql('PROD_MQT_CONSULTING_PIPELINE', self.conn, if_exists='replace', index=False)
        
        # Create demo PROD_MQT_SW_SAAS_OPPORTUNITY data
        demo_data_saas = {
            'OPPORTUNITY_NUMBER': [f'SAAS_{i:05d}' for i in range(1, 81)],
            'ACCOUNT_NAME': [random.choice(['Amazon', 'Google', 'Netflix', 'Spotify', 'Slack', 'Zoom', 'Dropbox', 'Atlassian']) for _ in range(80)],
            'OPEN_PIPELINE': [random.randint(30000, 3000000) for _ in range(80)],
            'SALES_STAGE': [random.choice(['Qualify', 'Propose', 'Negotiate', 'Won', 'Lost']) for _ in range(80)],
            'OPPORTUNITY_VALUE': [random.randint(30000, 3000000) for _ in range(80)]
        }
        
        df_saas = pd.DataFrame(demo_data_saas)
        df_saas.to_sql('PROD_MQT_SW_SAAS_OPPORTUNITY', self.conn, if_exists='replace', index=False)
        
        # Create demo PROD_MQT_CONSULTING_OPPORTUNITY data (alias table)
        df_consulting_opp = df_consulting.copy()
        df_consulting_opp.to_sql('PROD_MQT_CONSULTING_OPPORTUNITY', self.conn, if_exists='replace', index=False)
        
        # Create demo PROD_MQT_CONSULTING_BUDGET data
        demo_data_budget = {
            'GEOGRAPHY': [random.choice(['Americas', 'EMEA', 'APAC', 'Japan']) for _ in range(50)],
            'MARKET': [random.choice(['Financial Services', 'Healthcare', 'Retail', 'Technology']) for _ in range(50)],
            'YEAR': [2024] * 50,
            'QUARTER': [random.randint(1, 4) for _ in range(50)],
            'MONTH': [random.randint(1, 12) for _ in range(50)],
            'REVENUE_BUDGET_AMT': [random.randint(1000000, 50000000) for _ in range(50)],
            'SIGNINGS_BUDGET_AMT': [random.randint(800000, 40000000) for _ in range(50)],
            'GROSS_PROFIT_BUDGET_AMT': [random.randint(200000, 15000000) for _ in range(50)]
        }
        
        df_budget = pd.DataFrame(demo_data_budget)
        df_budget.to_sql('PROD_MQT_CONSULTING_BUDGET', self.conn, if_exists='replace', index=False)
        
        # Create demo PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE data
        demo_data_sw_pipeline = {
            'GEOGRAPHY': [random.choice(['Americas', 'EMEA', 'APAC', 'Japan']) for _ in range(60)],
            'MARKET': [random.choice(['Financial Services', 'Healthcare', 'Retail', 'Technology']) for _ in range(60)],
            'PPV': [random.randint(500000, 15000000) for _ in range(60)],
            'PPV_AMT': [random.randint(500000, 15000000) for _ in range(60)],
            'OPPORTUNITY_VALUE': [random.randint(400000, 12000000) for _ in range(60)],
            'SALES_STAGE': [random.choice(['Qualify', 'Propose', 'Negotiate', 'Won', 'Lost']) for _ in range(60)]
        }
        
        df_sw_pipeline = pd.DataFrame(demo_data_sw_pipeline)
        df_sw_pipeline.to_sql('PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE', self.conn, if_exists='replace', index=False)
        
        # Create demo PROD_MQT_SOFTWARE_TRANSACTIONAL_BUDGET data
        demo_data_sw_budget = {
            'GEOGRAPHY': [random.choice(['Americas', 'EMEA', 'APAC', 'Japan']) for _ in range(40)],
            'MARKET': [random.choice(['Financial Services', 'Healthcare', 'Retail', 'Technology']) for _ in range(40)],
            'YEAR': [2024] * 40,
            'QUARTER': [random.randint(1, 4) for _ in range(40)],
            'MONTH': [random.randint(1, 12) for _ in range(40)],
            'REVENUE_BUDGET': [random.randint(2000000, 30000000) for _ in range(40)],
            'REVENUE_BUDGET_AMT': [random.randint(2000000, 30000000) for _ in range(40)]
        }
        
        df_sw_budget = pd.DataFrame(demo_data_sw_budget)
        df_sw_budget.to_sql('PROD_MQT_SOFTWARE_TRANSACTIONAL_BUDGET', self.conn, if_exists='replace', index=False)
        
        # Add missing columns to consulting pipeline for better compatibility
        cursor = self.conn.cursor()
        try:
            cursor.execute("ALTER TABLE PROD_MQT_CONSULTING_PIPELINE ADD COLUMN RELATIVE_QUARTER_MNEUMONIC TEXT DEFAULT 'CQ'")
            cursor.execute("ALTER TABLE PROD_MQT_CONSULTING_PIPELINE ADD COLUMN WEEK INTEGER DEFAULT 1")
            cursor.execute("ALTER TABLE PROD_MQT_CONSULTING_PIPELINE ADD COLUMN QUARTER INTEGER DEFAULT 1")
            cursor.execute("ALTER TABLE PROD_MQT_CONSULTING_PIPELINE ADD COLUMN YEAR INTEGER DEFAULT 2024")
            cursor.execute("ALTER TABLE PROD_MQT_CONSULTING_PIPELINE ADD COLUMN SNAPSHOT_LEVEL TEXT DEFAULT 'W'")
            self.conn.commit()
        except:
            pass  # Columns might already exist
        
        self.tables_loaded['PROD_MQT_CONSULTING_PIPELINE'] = {
            'rows': len(df_consulting),
            'columns': list(df_consulting.columns) + ['RELATIVE_QUARTER_MNEUMONIC', 'WEEK', 'QUARTER', 'YEAR', 'SNAPSHOT_LEVEL'],
            'file': 'demo_data'
        }
        
        self.tables_loaded['PROD_MQT_SW_SAAS_OPPORTUNITY'] = {
            'rows': len(df_saas),
            'columns': list(df_saas.columns),
            'file': 'demo_data'
        }
        
        self.tables_loaded['PROD_MQT_CONSULTING_OPPORTUNITY'] = {
            'rows': len(df_consulting_opp),
            'columns': list(df_consulting_opp.columns),
            'file': 'demo_data'
        }
        
        self.tables_loaded['PROD_MQT_CONSULTING_BUDGET'] = {
            'rows': len(df_budget),
            'columns': list(df_budget.columns),
            'file': 'demo_data'
        }
        
        self.tables_loaded['PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE'] = {
            'rows': len(df_sw_pipeline),
            'columns': list(df_sw_pipeline.columns),
            'file': 'demo_data'
        }
        
        self.tables_loaded['PROD_MQT_SOFTWARE_TRANSACTIONAL_BUDGET'] = {
            'rows': len(df_sw_budget),
            'columns': list(df_sw_budget.columns),
            'file': 'demo_data'
        }
        
        self.generate_schema_info()
        total_rows = len(df_consulting) + len(df_saas) + len(df_budget) + len(df_sw_pipeline) + len(df_sw_budget)
        st.success(f"✅ Created demo data with {total_rows} records across 6 tables (Pipeline, SaaS, Budget, Opportunity, SW Pipeline, SW Budget)")
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        try:
            # If using SQLite, convert DB2 syntax to SQLite
            if self.db_type == "SQLite":
                sql_query = self._convert_db2_to_sqlite(sql_query)
            
            return pd.read_sql_query(sql_query, self.conn)
        except Exception as e:
            st.error(f"SQL Error: {e}")
            return pd.DataFrame()
    
    def _convert_db2_to_sqlite(self, query: str) -> str:
        """Convert DB2 syntax to SQLite for testing"""
        import re
        
        # Convert FETCH FIRST n ROWS ONLY to LIMIT n
        query = re.sub(r'FETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY', r'LIMIT \1', query, flags=re.IGNORECASE)
        
        # Convert DECIMAL(value, precision, scale) to ROUND(value, scale)
        decimal_pattern = r'DECIMAL\s*\(\s*([^,]+)\s*,\s*\d+\s*,\s*(\d+)\s*\)'
        query = re.sub(decimal_pattern, r'ROUND(\1, \2)', query, flags=re.IGNORECASE)
        
        # Convert simple DECIMAL(expression) to ROUND(expression, 2)
        simple_decimal_pattern = r'DECIMAL\s*\(\s*([^)]+)\s*\)'
        query = re.sub(simple_decimal_pattern, r'ROUND(\1, 2)', query, flags=re.IGNORECASE)
        
        # Convert CURRENT DATE to date('now')
        query = re.sub(r'CURRENT\s+DATE', "date('now')", query, flags=re.IGNORECASE)
        
        # Convert YEAR(column) to strftime('%Y', column) - but handle YEAR = value case
        query = re.sub(r'YEAR\s*\(\s*([^)]+)\s*\)', r"strftime('%Y', \1)", query, flags=re.IGNORECASE)
        
        # Fix YEAR = value comparisons (like YEAR = 2024)
        query = re.sub(r'AND\s+YEAR\s*=\s*', "AND strftime('%Y', date('now')) = ", query, flags=re.IGNORECASE)
        query = re.sub(r'WHERE\s+YEAR\s*=\s*', "WHERE strftime('%Y', date('now')) = ", query, flags=re.IGNORECASE)
        
        # Convert MONTH(column) to strftime('%m', column)
        query = re.sub(r'MONTH\s*\(\s*([^)]+)\s*\)', r"strftime('%m', \1)", query, flags=re.IGNORECASE)
        
        # Convert QUARTER(column) to quarter calculation - be more careful with parentheses
        # First handle standalone QUARTER function calls
        quarter_pattern = r'QUARTER\s*\(\s*([^)]+)\s*\)'
        def quarter_replacement(match):
            column = match.group(1).strip()
            return f"((CAST(strftime('%m', {column}) AS INTEGER) - 1) / 3 + 1)"
        query = re.sub(quarter_pattern, quarter_replacement, query, flags=re.IGNORECASE)
        
        # Fix common malformed cases from the conversion
        query = re.sub(r'AS\s+INTEGER\)\s+AS\s+INTEGER', 'AS INTEGER', query, flags=re.IGNORECASE)
        
        # Convert CAST(x AS DOUBLE) to CAST(x AS REAL) - SQLite uses REAL for floating point
        query = re.sub(r'CAST\s*\(\s*([^)]+)\s+AS\s+DOUBLE\s*\)', r'CAST(\1 AS REAL)', query, flags=re.IGNORECASE)
        
        # Convert FULL OUTER JOIN to LEFT JOIN (SQLite doesn't support FULL OUTER JOIN)
        query = re.sub(r'FULL\s+OUTER\s+JOIN', 'LEFT JOIN', query, flags=re.IGNORECASE)
        
        # Fix ROUND function calls - SQLite ROUND only takes value and scale (2 parameters max)
        # Convert DECIMAL(value, precision, scale) to ROUND(value, scale) - already handled above
        # Fix any remaining ROUND calls with 3 parameters
        query = re.sub(r'ROUND\s*\(\s*([^,]+),\s*\d+,\s*(\d+)\s*\)', r'ROUND(\1, \2)', query, flags=re.IGNORECASE)
        
        # Fix malformed conversions where DECIMAL parameters become ROUND parameters incorrectly
        query = re.sub(r'COALESCE\([^,]+,\s*(\d+)\)', lambda m: m.group(0).replace(f', {m.group(1)}', ', 0'), query)
        
        # Remove NULLS LAST/FIRST from ORDER BY (not supported in SQLite)
        query = re.sub(r'\s+NULLS\s+(LAST|FIRST)', '', query, flags=re.IGNORECASE)
        
        # Convert NULLIF function (SQLite has this, so keep it)
        # No change needed for NULLIF
        
        # Remove DB2 comments that might cause issues
        query = re.sub(r'—[^\n]*', '', query)  # Remove em-dash comments
        
        return query