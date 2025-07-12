#!/usr/bin/env python3
"""
Column Validation Agent
Validates column existence and triggers SQL regeneration if needed
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from .base import SQLAgent, AgentResponse, QueryContext


class ColumnValidationAgent(SQLAgent):
    """Validates column existence and suggests alternatives or regeneration"""
    
    def __init__(self):
        super().__init__(
            "ColumnValidation",
            "Validates column existence and suggests alternatives or regeneration"
        )
        
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Validate all columns in the query exist in the schema"""
        sql_query = input_data.get("optimized_query", input_data.get("sql_query", ""))
        
        if not sql_query:
            return self.create_response(
                success=False,
                message="No SQL query provided",
                confidence=0.0
            )
        
        # Skip validation for queries with CTEs as they create derived columns
        if 'WITH ' in sql_query.upper():
            self.log("Query contains CTE - skipping column validation")
            return self.create_response(
                success=True,
                message="Query contains CTE - column validation skipped",
                data={
                    "original_query": sql_query,
                    "validated_query": sql_query,
                    "missing_columns": [],
                    "column_mappings": {},
                    "substitutions_made": [],
                    "available_columns": [],
                    "needs_regeneration": False
                },
                confidence=0.9,
                suggestions=[]
            )
        
        missing_columns = []
        available_columns = []
        column_mappings = {}
        needs_regeneration = False
        
        # Step 1: Extract all column references from query
        self.log("Extracting column references from query...")
        referenced_columns = self._extract_column_references(sql_query)
        
        # Step 2: Check each column against available schema
        self.log("Validating columns against available schema...")
        for table, columns in referenced_columns.items():
            if table in context.columns_available:
                table_columns = context.columns_available[table]
                available_columns.extend(table_columns)
                
                for col in columns:
                    if col.upper() not in [tc.upper() for tc in table_columns]:
                        missing_columns.append({"table": table, "column": col})
                        self.log(f"Missing column detected: {col} in {table}")
                        
                        # Step 3: Try to find similar column
                        similar = self._find_similar_column(col, table_columns)
                        if similar:
                            column_mappings[col] = similar
                            self.log(f"Found similar column: {col} -> {similar}")
            else:
                # Table not in our schema - likely a CTE or external table
                self.log(f"Skipping column validation for unknown table: {table}")
                # Don't add missing columns for unknown tables
        
        # Step 4: Determine if regeneration is needed
        if missing_columns:
            # Check if we can map all missing columns
            unmappable_columns = [col for col in missing_columns if col["column"] not in column_mappings]
            
            if unmappable_columns:
                needs_regeneration = True
                self.log(f"Regeneration needed - {len(unmappable_columns)} unmappable columns")
            else:
                self.log(f"Column mapping possible - {len(column_mappings)} substitutions available")
        
        # Step 5: Apply column substitutions if possible
        corrected_query = sql_query
        substitutions_made = []
        
        if column_mappings and not needs_regeneration:
            corrected_query, substitutions_made = self._apply_column_substitutions(sql_query, column_mappings)
        
        confidence = 1.0 if not missing_columns else (0.7 if not needs_regeneration else 0.3)
        
        # Create detailed step summary
        step_details = {
            "columns_checked": sum(len(cols) for cols in referenced_columns.values()),
            "missing_columns": len(missing_columns),
            "column_mappings": len(column_mappings),
            "substitutions_made": len(substitutions_made),
            "needs_regeneration": needs_regeneration
        }
        
        return self.create_response(
            success=not needs_regeneration,
            message=f"Column validation complete - {len(missing_columns)} missing columns found" if missing_columns else "All columns validated successfully",
            data={
                "original_query": sql_query,
                "validated_query": corrected_query,
                "missing_columns": missing_columns,
                "column_mappings": column_mappings,
                "substitutions_made": substitutions_made,
                "available_columns": available_columns,
                "needs_regeneration": needs_regeneration,
                "step_details": step_details,
                "regeneration_prompt": self._build_regeneration_prompt(missing_columns, available_columns, context) if needs_regeneration else None
            },
            confidence=confidence,
            suggestions=self._build_suggestions(missing_columns, column_mappings, available_columns)
        )
    
    def _extract_column_references(self, query: str) -> Dict[str, List[str]]:
        """Extract all column references from SQL query"""
        # Remove comments and strings
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
        clean_query = re.sub(r"'[^']*'", "''", clean_query)
        clean_query = re.sub(r'"[^"]*"', '""', clean_query)
        
        # Find CTEs first (Common Table Expressions) - extract their SELECT columns too
        cte_names = set()
        cte_columns = {}  # Map CTE name to its output columns
        
        # Pattern to extract CTE with its SELECT clause
        cte_full_pattern = r'WITH\s+(\w+)\s+AS\s*\((.*?)\)(?=\s*(?:,|SELECT))'
        for match in re.finditer(cte_full_pattern, clean_query, re.IGNORECASE | re.DOTALL):
            cte_name = match.group(1).upper()
            cte_names.add(cte_name)
            
            # Extract columns from CTE SELECT clause
            cte_body = match.group(2)
            # Find column aliases in SELECT clause (e.g., COLUMN AS ALIAS)
            alias_pattern = r'(\w+)\s+AS\s+(\w+)'
            cte_cols = []
            for alias_match in re.finditer(alias_pattern, cte_body, re.IGNORECASE):
                cte_cols.append(alias_match.group(2).upper())
            cte_columns[cte_name] = cte_cols
        
        # Find table references
        table_aliases = {}
        primary_table = None
        table_pattern = r'FROM\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?|JOIN\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?'
        for match in re.finditer(table_pattern, clean_query, re.IGNORECASE):
            table = match.group(1) or match.group(3)
            alias = match.group(2) or match.group(4)
            
            # Skip CTEs - they're not real tables
            if table.upper() in cte_names:
                continue
                
            if not primary_table:  # First table found is primary
                primary_table = table.upper()
                
            if alias:
                table_aliases[alias.upper()] = table.upper()
        
        # Extract column references
        referenced_columns = {}
        
        # Pattern for qualified column references (table.column or alias.column)
        qualified_pattern = r'\b(\w+)\.(\w+)\b'
        for match in re.finditer(qualified_pattern, clean_query):
            table_ref = match.group(1).upper()
            column = match.group(2).upper()
            
            # Resolve alias to actual table name
            actual_table = table_aliases.get(table_ref, table_ref)
            
            if actual_table not in referenced_columns:
                referenced_columns[actual_table] = []
            if column not in referenced_columns[actual_table]:
                referenced_columns[actual_table].append(column)
        
        # For CTEs, we won't validate their internal columns since they're derived
        # We only validate columns from actual database tables
        
        # Extract columns from WHERE, GROUP BY, ORDER BY that reference real tables
        if primary_table and primary_table not in cte_names:
            all_columns = set()
            
            # Look for columns in WHERE clause that are compared to values
            where_pattern = r'(\w+)\s*(?:=|>|<|>=|<=|<>|!=)\s*(?:\'[^\']*\'|\d+)'
            for match in re.finditer(where_pattern, clean_query, re.IGNORECASE):
                col_name = match.group(1).upper()
                # Only add if it's not a SQL keyword or function
                if col_name not in ['AND', 'OR', 'NOT', 'EXISTS', 'NULL', 'TRUE', 'FALSE']:
                    all_columns.add(col_name)
            
            # GROUP BY clause columns
            group_match = re.search(r'GROUP\s+BY\s+([\w\s,]+?)(?:\s+ORDER\s+BY|\s+HAVING|\s*$)', clean_query, re.IGNORECASE)
            if group_match:
                group_clause = group_match.group(1)
                # Split by comma and extract column names
                for col in group_clause.split(','):
                    col = col.strip().upper()
                    if col and not col.isdigit():
                        all_columns.add(col)
            
            # Add extracted columns to primary table if any found
            if all_columns:
                if primary_table not in referenced_columns:
                    referenced_columns[primary_table] = []
                for col in all_columns:
                    if col not in referenced_columns[primary_table]:
                        referenced_columns[primary_table].append(col)
        
        # Remove any CTE names that were mistakenly added as columns
        for table in list(referenced_columns.keys()):
            if table in cte_names:
                del referenced_columns[table]
        
        return referenced_columns
    
    def _find_similar_column(self, missing_column: str, available_columns: List[str]) -> Optional[str]:
        """Find similar column name using fuzzy matching"""
        missing_upper = missing_column.upper()
        
        # Exact match (case insensitive)
        for col in available_columns:
            if col.upper() == missing_upper:
                return col
        
        # Common column mappings for IBM sales data
        column_mappings = {
            'OPPORTUNITY_ID': ['OPPTY_ID', 'OPP_ID', 'OPPORTUNITY_NUM', 'DEAL_ID'],
            'OPPORTUNITY_VALUE': ['OPPTY_VALUE', 'DEAL_VALUE', 'OPPORTUNITY_AMT', 'OPP_VALUE'],
            'CLIENT_NAME': ['CUSTOMER_NAME', 'ACCOUNT_NAME', 'CLIENT_ID', 'CUSTOMER_ID'],
            'SALES_STAGE': ['STAGE', 'OPPORTUNITY_STAGE', 'DEAL_STAGE'],
            'WON_AMT': ['WON_AMOUNT', 'WON_VALUE', 'CLOSED_WON_AMT'],
            'REVENUE_AMT': ['REVENUE', 'REVENUE_AMOUNT', 'ACTUAL_REVENUE'],
            'PIPELINE_AMT': ['PIPELINE_VALUE', 'PIPELINE_AMOUNT'],
            'BUDGET_AMT': ['BUDGET', 'BUDGET_AMOUNT', 'TARGET_REVENUE']
        }
        
        # Check if missing column has a known mapping
        if missing_upper in column_mappings:
            for potential in column_mappings[missing_upper]:
                for col in available_columns:
                    if col.upper() == potential:
                        return col
        
        # Reverse lookup - check if available column maps to missing column
        for standard, alternatives in column_mappings.items():
            if missing_upper in alternatives:
                for col in available_columns:
                    if col.upper() == standard:
                        return col
        
        # Substring matching
        for col in available_columns:
            col_upper = col.upper()
            if missing_upper in col_upper or col_upper in missing_upper:
                # Additional check for meaningful similarity
                if len(missing_upper) > 3 and len(col_upper) > 3:
                    return col
        
        return None
    
    def _apply_column_substitutions(self, query: str, mappings: Dict[str, str]) -> Tuple[str, List[str]]:
        """Apply column substitutions to the query"""
        corrected_query = query
        substitutions_made = []
        
        for old_col, new_col in mappings.items():
            # Replace qualified references (table.column)
            pattern1 = rf'\b(\w+\.){old_col}\b'
            if re.search(pattern1, corrected_query, re.IGNORECASE):
                corrected_query = re.sub(pattern1, rf'\1{new_col}', corrected_query, flags=re.IGNORECASE)
                substitutions_made.append(f"{old_col} -> {new_col}")
            
            # Replace unqualified references (more risky, so we're careful)
            # Only replace if it's clearly a column reference
            pattern2 = rf'\b{old_col}\b(?=\s*[,\s]|\s+AS\s|\s*\)|\s*$)'
            if re.search(pattern2, corrected_query, re.IGNORECASE):
                corrected_query = re.sub(pattern2, new_col, corrected_query, flags=re.IGNORECASE)
                if f"{old_col} -> {new_col}" not in substitutions_made:
                    substitutions_made.append(f"{old_col} -> {new_col}")
        
        return corrected_query, substitutions_made
    
    def _build_regeneration_prompt(self, missing_columns: List[Dict], available_columns: List[str], context: QueryContext) -> str:
        """Build prompt for SQL regeneration"""
        missing_list = [f"{col['column']} (from {col['table']})" for col in missing_columns]
        
        prompt = f"""
The generated SQL query contains columns that don't exist in the database schema.

MISSING COLUMNS:
{', '.join(missing_list)}

AVAILABLE COLUMNS:
{', '.join(available_columns[:20])}{'...' if len(available_columns) > 20 else ''}

Please regenerate the SQL query using only the available columns. 
Consider these alternatives:
- For OPPORTUNITY_ID: Use OPPTY_ID, OPP_ID, or similar
- For OPPORTUNITY_VALUE: Use OPPTY_VALUE, DEAL_VALUE, or PPV_AMT
- For CLIENT_NAME: Use CUSTOMER_NAME or ACCOUNT_NAME
- For missing date columns: Use available date/time columns

Original question: {context.question}
Database type: {context.db_type}
"""
        return prompt
    
    def _build_suggestions(self, missing_columns: List[Dict], column_mappings: Dict[str, str], available_columns: List[str]) -> List[str]:
        """Build suggestions for fixing column issues"""
        suggestions = []
        
        if missing_columns:
            suggestions.append(f"Found {len(missing_columns)} missing columns")
            
            if column_mappings:
                suggestions.append("Some columns can be automatically substituted:")
                for old, new in column_mappings.items():
                    suggestions.append(f"  {old} → {new}")
            
            unmappable = [col for col in missing_columns if col["column"] not in column_mappings]
            if unmappable:
                suggestions.append("Columns requiring regeneration:")
                for col in unmappable:
                    suggestions.append(f"  {col['column']} (from {col['table']})")
                
                suggestions.append("Consider these alternatives from available columns:")
                # Show relevant available columns
                relevant = [col for col in available_columns if any(keyword in col.upper() for keyword in ['ID', 'NAME', 'AMT', 'VALUE', 'STAGE'])]
                for col in relevant[:5]:
                    suggestions.append(f"  {col}")
        
        return suggestions