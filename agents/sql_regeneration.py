#!/usr/bin/env python3
"""
SQL Regeneration Agent
Handles SQL regeneration when column validation fails
"""

import re
from typing import Dict, Any
from .base import SQLAgent, AgentResponse, QueryContext


class SQLRegenerationAgent(SQLAgent):
    """Regenerates SQL queries with valid columns when validation fails"""
    
    def __init__(self, llm_connector=None):
        super().__init__(
            "SQLRegeneration",
            "Regenerates SQL queries with valid columns when validation fails"
        )
        self.llm_connector = llm_connector
        
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Regenerate SQL with valid columns"""
        regeneration_prompt = input_data.get("regeneration_prompt", "")
        original_query = input_data.get("original_query", "")
        
        if not regeneration_prompt:
            return self.create_response(
                success=False,
                message="No regeneration prompt provided",
                confidence=0.0
            )
        
        self.log("Attempting SQL regeneration with valid columns...")
        
        try:
            if self.llm_connector:
                # Use the same LLM that generated the original query
                regenerated_result = self.llm_connector.generate_sql(
                    context.question,
                    context.schema_info,
                    context.data_dictionary + "\n\n" + regeneration_prompt
                )
                
                if regenerated_result and "sql_query" in regenerated_result:
                    new_query = regenerated_result["sql_query"]
                    
                    return self.create_response(
                        success=True,
                        message="SQL successfully regenerated with valid columns",
                        data={
                            "original_query": original_query,
                            "regenerated_query": new_query,
                            "regeneration_explanation": regenerated_result.get("explanation", ""),
                            "regeneration_confidence": regenerated_result.get("confidence", 0.8)
                        },
                        confidence=regenerated_result.get("confidence", 0.8)
                    )
            
            # Fallback: Basic column substitution
            self.log("LLM regeneration not available, using fallback substitution...")
            fallback_query = self._apply_fallback_substitutions(original_query, context)
            
            return self.create_response(
                success=True,
                message="Applied fallback column substitutions",
                data={
                    "original_query": original_query,
                    "regenerated_query": fallback_query,
                    "regeneration_explanation": "Applied basic column name substitutions",
                    "regeneration_confidence": 0.6
                },
                confidence=0.6
            )
            
        except Exception as e:
            self.log(f"Regeneration failed: {e}")
            return self.create_response(
                success=False,
                message=f"SQL regeneration failed: {e}",
                data={"original_query": original_query},
                confidence=0.0
            )
    
    def _apply_fallback_substitutions(self, query: str, context: QueryContext) -> str:
        """Apply basic fallback column substitutions"""
        fallback_query = query
        
        # Common substitutions for IBM sales pipeline data
        substitutions = {
            r'\bOPPORTUNITY_ID\b': 'OPPTY_ID',
            r'\bOPPORTUNITY_VALUE\b': 'PPV_AMT',
            r'\bCLIENT_NAME\b': 'CUSTOMER_NAME',
            r'\bREVENUE_AMT\b': 'ACTUAL_REVENUE',
            r'\bPIPELINE_AMT\b': 'PIPELINE_VALUE'
        }
        
        for pattern, replacement in substitutions.items():
            fallback_query = re.sub(pattern, replacement, fallback_query, flags=re.IGNORECASE)
        
        return fallback_query