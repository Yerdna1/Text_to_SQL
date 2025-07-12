#!/usr/bin/env python3
"""
SQL Agent System
Multi-agent orchestration for SQL query enhancement and validation
"""

from typing import Dict, Any
from .orchestrator import SQLAgentOrchestrator


def process_with_agents(sql_query: str, 
                       question: str,
                       db_manager,
                       data_dict,
                       db_type: str = "SQLite",
                       llm_connector=None) -> Dict[str, Any]:
    """
    Process SQL query with enhanced multi-agent system including column validation
    
    This function integrates with the existing create_interactive_app.py
    """
    
    # Extract schema information from db_manager
    tables_available = list(db_manager.tables_loaded.keys()) if db_manager and hasattr(db_manager, 'tables_loaded') else []
    
    # If no tables loaded, use a default schema for IBM sales pipeline
    if not tables_available:
        print("[Agent Warning] No tables loaded in db_manager, using default IBM schema")
        tables_available = ["PROD_MQT_CONSULTING_PIPELINE", "PROD_MQT_CONSULTING_BUDGET", "PROD_MQT_CONSULTING_REVENUE_ACTUALS"]
        columns_available = {
            "PROD_MQT_CONSULTING_PIPELINE": [
                "MARKET", "WON_AMT", "SALES_STAGE", "OPPORTUNITY_VALUE", "YEAR", "QUARTER", 
                "PPV_AMT", "GEOGRAPHY", "CLIENT_NAME", "SNAPSHOT_LEVEL", "WEEK",
                "OPPTY_ID", "DEAL_ID", "IBM_GEN_AI_IND", "PARTNER_GEN_AI_IND",
                "CALL_AMT", "UPSIDE_AMT", "QUALIFY_PLUS_AMT", "PROPOSE_PLUS_AMT",
                "NEGOTIATE_PLUS_AMT", "OPEN_PIPELINE_AMT", "UT15_NAME", "UT17_NAME",
                "UT20_NAME", "UT30_NAME", "SECTOR", "INDUSTRY", "RELATIVE_QUARTER_MNEUMONIC"
            ],
            "PROD_MQT_CONSULTING_BUDGET": [
                "REVENUE_BUDGET_AMT", "SIGNINGS_BUDGET_AMT", "GROSS_PROFIT_BUDGET_AMT",
                "YEAR", "QUARTER", "MONTH", "GEOGRAPHY", "MARKET", "SECTOR", "INDUSTRY",
                "CLIENT_NAME", "UT15_NAME", "UT17_NAME", "UT20_NAME", "UT30_NAME"
            ],
            "PROD_MQT_CONSULTING_REVENUE_ACTUALS": [
                "REVENUE_AMT", "GROSS_PROFIT_AMT", "REVENUE_AMT_PY", "GROSS_PROFIT_AMT_PY",
                "YEAR", "QUARTER", "MONTH", "GEOGRAPHY", "MARKET", "SECTOR", "INDUSTRY"
            ]
        }
    else:
        columns_available = {
            table: info["columns"] 
            for table, info in db_manager.tables_loaded.items()
        }
    
    # Get data dictionary context
    data_dictionary = data_dict.get_comprehensive_context() if data_dict else ""
    schema_info = db_manager.schema_info if db_manager else ""
    
    # Create orchestrator with LLM connector for regeneration
    orchestrator = SQLAgentOrchestrator(llm_connector=llm_connector)
    
    result = orchestrator.process_query(
        initial_query=sql_query,
        question=question,
        schema_info=schema_info,
        data_dictionary=data_dictionary,
        tables_available=tables_available,
        columns_available=columns_available,
        db_type=db_type
    )
    
    # Add explanation
    result["explanation"] = orchestrator.explain_processing(result)
    
    return result


# Import all agent classes for convenient access
from .base import SQLAgent, AgentResponse, QueryContext
from .db2_syntax_validator import DB2SyntaxValidatorAgent
from .where_clause_enhancer import WhereClauseEnhancerAgent
from .query_optimizer import QueryOptimizerAgent
from .column_validation import ColumnValidationAgent
from .sql_regeneration import SQLRegenerationAgent
from .orchestrator import SQLAgentOrchestrator

__all__ = [
    'process_with_agents',
    'SQLAgent',
    'AgentResponse', 
    'QueryContext',
    'DB2SyntaxValidatorAgent',
    'WhereClauseEnhancerAgent',
    'QueryOptimizerAgent',
    'ColumnValidationAgent',
    'SQLRegenerationAgent',
    'SQLAgentOrchestrator'
]