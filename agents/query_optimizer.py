#!/usr/bin/env python3
"""
Query Optimizer Agent
Optimizes SQL queries for performance
"""

from typing import Dict, Any
from .base import SQLAgent, AgentResponse, QueryContext


class QueryOptimizerAgent(SQLAgent):
    """Optimizes SQL queries for performance"""
    
    def __init__(self):
        super().__init__(
            "QueryOptimizer", 
            "Optimizes SQL queries for better performance"
        )
        
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Optimize the SQL query"""
        sql_query = input_data.get("enhanced_query", input_data.get("sql_query", ""))
        
        optimizations = []
        optimized_query = sql_query
        
        # Step 1: Check for MQT table usage
        self.log("Analyzing table usage for MQT optimization...")
        if "PROD_MQT" in optimized_query:
            optimizations.append("Using MQT (Materialized Query Tables) for optimal performance")
            self.log("MQT tables detected - optimal for performance")
        
        # Step 2: Check SELECT clause efficiency
        self.log("Analyzing SELECT clause efficiency...")
        if "SELECT *" in optimized_query.upper():
            optimizations.append("Consider selecting specific columns instead of SELECT *")
            self.log("SELECT * detected - recommend specific columns for better performance")
        
        # Step 3: Check for result set limits
        self.log("Checking for result set limitations...")
        if "FETCH FIRST" not in optimized_query.upper() and "LIMIT" not in optimized_query.upper():
            has_aggregation = any(agg in optimized_query.upper() for agg in ["SUM(", "COUNT(", "AVG(", "MAX(", "MIN("])
            
            if not has_aggregation:
                if context.db_type == "DB2":
                    optimized_query += " FETCH FIRST 1000 ROWS ONLY"
                    self.log("Added DB2 FETCH FIRST clause for result limiting")
                else:
                    optimized_query += " LIMIT 1000"
                    self.log("Added LIMIT clause for result limiting")
                optimizations.append("Added row limit to prevent large result sets")
            else:
                self.log("Aggregation detected - no row limit needed")
        else:
            self.log("Result limiting already present")
        
        # Step 4: Check for index opportunities
        self.log("Analyzing indexing opportunities...")
        if "WHERE" in optimized_query.upper():
            optimizations.append("WHERE clause present - ensure indexes on filter columns")
            
        # Step 5: Check for join optimization
        self.log("Checking for join optimizations...")
        if " JOIN " in optimized_query.upper():
            optimizations.append("JOINs detected - verify proper join conditions and indexes")
        
        confidence = 0.9 if optimizations else 0.7
        
        # Create detailed step summary
        step_details = {
            "mqt_optimization": "PROD_MQT" in optimized_query,
            "select_optimization": "SELECT *" not in optimized_query.upper(),
            "limit_added": "FETCH FIRST" in optimized_query.upper() or "LIMIT" in optimized_query.upper(),
            "where_present": "WHERE" in optimized_query.upper(),
            "joins_present": " JOIN " in optimized_query.upper(),
            "total_optimizations": len(optimizations)
        }
        
        return self.create_response(
            success=True,
            message=f"Query optimization complete - {len(optimizations)} improvements applied",
            data={
                "original_query": sql_query,
                "optimized_query": optimized_query,
                "optimizations": optimizations,
                "step_details": step_details
            },
            confidence=confidence
        )