#!/usr/bin/env python3
"""
SQL Agent Orchestrator
Orchestrates multiple SQL agents to generate, validate, and enhance queries
"""

from typing import Dict, List, Any
from .base import QueryContext
from .db2_syntax_validator import DB2SyntaxValidatorAgent
from .where_clause_enhancer import WhereClauseEnhancerAgent
from .query_optimizer import QueryOptimizerAgent
from .column_validation import ColumnValidationAgent
from .sql_regeneration import SQLRegenerationAgent


class SQLAgentOrchestrator:
    """Orchestrates multiple SQL agents to generate, validate, and enhance queries"""
    
    def __init__(self, llm_connector=None):
        self.agents = {
            "validator": DB2SyntaxValidatorAgent(),
            "enhancer": WhereClauseEnhancerAgent(),
            "optimizer": QueryOptimizerAgent(),
            "column_validator": ColumnValidationAgent(),
            "regenerator": SQLRegenerationAgent(llm_connector)
        }
        self.llm_connector = llm_connector
        
    def process_query(self, 
                     initial_query: str,
                     question: str,
                     schema_info: str,
                     data_dictionary: str,
                     tables_available: List[str],
                     columns_available: Dict[str, List[str]],
                     db_type: str = "SQLite") -> Dict[str, Any]:
        """
        Process a query through the enhanced agent pipeline with column validation
        
        Returns:
            Dict containing the final query and processing details
        """
        
        # Create context
        context = QueryContext(
            question=question,
            schema_info=schema_info,
            data_dictionary=data_dictionary,
            tables_available=tables_available,
            columns_available=columns_available,
            db_type=db_type
        )
        
        # Track processing steps
        processing_log = []
        current_data = {"sql_query": initial_query}
        regeneration_attempted = False
        
        # Step 1: Validate and correct syntax
        validator_response = self.agents["validator"].process(current_data, context)
        processing_log.append({
            "agent": "DB2SyntaxValidator",
            "success": validator_response.success,
            "message": validator_response.message,
            "confidence": validator_response.confidence
        })
        
        if validator_response.success:
            current_data = validator_response.data
        else:
            # Don't return early - continue with other agents even if validation has issues
            # Use the best available query from validator
            current_data = {
                "sql_query": validator_response.data.get("validated_query", initial_query),
                "original_query": initial_query
            }
        
        # Step 2: Enhance WHERE clause
        enhancer_response = self.agents["enhancer"].process(current_data, context)
        processing_log.append({
            "agent": "WhereClauseEnhancer",
            "success": enhancer_response.success,
            "message": enhancer_response.message,
            "enhancements": enhancer_response.data.get("enhancements", [])
        })
        
        if enhancer_response.success:
            current_data = enhancer_response.data
            
        # Step 3: Optimize query
        optimizer_response = self.agents["optimizer"].process(current_data, context)
        processing_log.append({
            "agent": "QueryOptimizer",
            "success": optimizer_response.success,
            "message": optimizer_response.message,
            "optimizations": optimizer_response.data.get("optimizations", [])
        })
        
        if optimizer_response.success:
            current_data = optimizer_response.data
        
        # Step 4: NEW - Column validation
        column_validator_response = self.agents["column_validator"].process(current_data, context)
        processing_log.append({
            "agent": "ColumnValidation",
            "success": column_validator_response.success,
            "message": column_validator_response.message,
            "confidence": column_validator_response.confidence,
            "missing_columns": column_validator_response.data.get("missing_columns", []),
            "substitutions": column_validator_response.data.get("substitutions_made", [])
        })
        
        # Step 5: Handle regeneration if needed
        if not column_validator_response.success and column_validator_response.data.get("needs_regeneration"):
            regeneration_data = {
                "regeneration_prompt": column_validator_response.data.get("regeneration_prompt"),
                "original_query": column_validator_response.data.get("original_query")
            }
            
            regenerator_response = self.agents["regenerator"].process(regeneration_data, context)
            processing_log.append({
                "agent": "SQLRegeneration",
                "success": regenerator_response.success,
                "message": regenerator_response.message,
                "confidence": regenerator_response.confidence
            })
            
            if regenerator_response.success:
                # Use regenerated query and reprocess through the pipeline
                regenerated_query = regenerator_response.data.get("regenerated_query")
                regeneration_attempted = True
                
                # Reprocess the regenerated query through validation steps
                current_data = {"sql_query": regenerated_query}
                
                # Re-run column validation to ensure regenerated query is valid
                final_column_check = self.agents["column_validator"].process(current_data, context)
                processing_log.append({
                    "agent": "ColumnValidation-Recheck",
                    "success": final_column_check.success,
                    "message": f"Regenerated query validation: {final_column_check.message}",
                    "confidence": final_column_check.confidence
                })
                
                if final_column_check.success:
                    current_data = final_column_check.data
                else:
                    # If regeneration still fails, use substituted query
                    current_data = column_validator_response.data
            else:
                # Regeneration failed, use column substitution if available
                if column_validator_response.data.get("validated_query"):
                    current_data = column_validator_response.data
        else:
            # Column validation passed or substitutions were successful
            if column_validator_response.success:
                current_data = column_validator_response.data
        
        # Calculate overall confidence
        confidences = [log.get("confidence", 0.8) for log in processing_log if "confidence" in log]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.7
        
        # Determine final query
        final_query = current_data.get("validated_query", 
                     current_data.get("regenerated_query",
                     current_data.get("optimized_query", 
                     current_data.get("enhanced_query", initial_query))))
        
        # Determine overall success based on meaningful improvements made
        critical_failures = [step for step in processing_log if not step.get("success", False) and step.get("agent") in ["DB2SyntaxValidator"]]
        has_valid_query = final_query and final_query.strip()
        
        # Check if we made meaningful improvements (syntax conversion, etc.)
        syntax_improvements = len(validator_response.data.get("corrections", []))
        has_syntax_fixes = syntax_improvements > 0
        
        # Success if no critical failures AND (we improved the query OR high confidence)
        overall_success = (
            len(critical_failures) == 0 and 
            (has_syntax_fixes or has_valid_query or overall_confidence > 0.7)
        )
        
        return {
            "success": overall_success,
            "final_query": final_query,
            "original_query": initial_query,
            "processing_log": processing_log,
            "overall_confidence": overall_confidence,
            "regeneration_attempted": regeneration_attempted,
            "improvements": {
                "syntax_corrections": len(validator_response.data.get("issues", [])),
                "where_enhancements": len(enhancer_response.data.get("enhancements", [])),
                "optimizations": len(optimizer_response.data.get("optimizations", [])),
                "column_fixes": len(column_validator_response.data.get("substitutions_made", [])),
                "regeneration_needed": column_validator_response.data.get("needs_regeneration", False)
            }
        }
    
    def explain_processing(self, result: Dict[str, Any]) -> str:
        """Generate a human-readable explanation of the processing"""
        
        explanation = []
        
        if not result["success"]:
            explanation.append("❌ Query processing failed during validation.")
            if result.get("issues"):
                explanation.append("Issues found:")
                for issue in result["issues"]:
                    explanation.append(f"  • {issue}")
            return "\n".join(explanation)
        
        explanation.append("✅ Query successfully processed through multi-agent system:")
        explanation.append("")
        
        for step in result["processing_log"]:
            agent = step["agent"]
            if agent == "DB2SyntaxValidator":
                explanation.append(f"1️⃣ **{agent}**: {step['message']}")
                if step.get("confidence"):
                    explanation.append(f"   Confidence: {step['confidence']:.0%}")
                    
            elif agent == "WhereClauseEnhancer":
                explanation.append(f"2️⃣ **{agent}**: {step['message']}")
                if step.get("enhancements"):
                    explanation.append("   Enhancements:")
                    for enhancement in step["enhancements"]:
                        explanation.append(f"   • {enhancement}")
                        
            elif agent == "QueryOptimizer":
                explanation.append(f"3️⃣ **{agent}**: {step['message']}")
                if step.get("optimizations"):
                    explanation.append("   Optimizations:")
                    for opt in step["optimizations"]:
                        explanation.append(f"   • {opt}")
        
        explanation.append("")
        explanation.append(f"**Overall Confidence**: {result['overall_confidence']:.0%}")
        
        improvements = result.get("improvements", {})
        if any(improvements.values()):
            explanation.append("")
            explanation.append("**Summary of Improvements**:")
            if improvements.get("syntax_corrections", 0) > 0:
                explanation.append(f"• Fixed {improvements['syntax_corrections']} syntax issues")
            if improvements.get("where_enhancements", 0) > 0:
                explanation.append(f"• Added {improvements['where_enhancements']} WHERE clause enhancements")
            if improvements.get("optimizations", 0) > 0:
                explanation.append(f"• Applied {improvements['optimizations']} query optimizations")
            if improvements.get("column_fixes", 0) > 0:
                explanation.append(f"• Fixed {improvements['column_fixes']} column issues")
            if improvements.get("regeneration_needed"):
                explanation.append("• SQL regeneration was required due to column validation failures")
        
        return "\n".join(explanation)