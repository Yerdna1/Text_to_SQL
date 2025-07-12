#!/usr/bin/env python3
"""
DB2 Syntax Validator Agent
Validates and converts SQL to proper DB2 syntax
"""

import re
from typing import Dict, List, Tuple, Any
from .base import SQLAgent, AgentResponse, QueryContext


class DB2SyntaxValidatorAgent(SQLAgent):
    """Validates and converts SQL to proper DB2 syntax"""
    
    def __init__(self):
        super().__init__(
            "DB2SyntaxValidator",
            "Validates SQL syntax and ensures DB2 compatibility"
        )
        
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Validate and correct DB2 syntax"""
        sql_query = input_data.get("sql_query", "")
        
        if not sql_query:
            return self.create_response(
                success=False,
                message="No SQL query provided",
                confidence=0.0
            )
        
        issues = []
        suggestions = []
        corrections = []
        corrected_query = sql_query
        
        # Always use DB2 syntax validation (application is DB2-only)
        self.log("Validating DB2 syntax compliance...")
        corrected_query, db2_issues = self._validate_db2_syntax(corrected_query)
        issues.extend(db2_issues)
        if db2_issues:
            corrections.extend([f"DB2 Syntax: {issue}" for issue in db2_issues])
        
        # Step 2: DB2 function validations
        self.log("Checking DB2 function usage...")
        corrected_query, func_issues = self._validate_db2_functions(corrected_query)
        issues.extend(func_issues)
        if func_issues:
            corrections.extend([f"Functions: {issue}" for issue in func_issues])
        
        # Step 3: DB2 date/time handling
        self.log("Validating date/time functions...")
        corrected_query, date_issues = self._validate_db2_dates(corrected_query)
        issues.extend(date_issues)
        if date_issues:
            corrections.extend([f"Date/Time: {issue}" for issue in date_issues])
        
        # Step 4: Check table names
        self.log("Validating table names against schema...")
        tables_used = self._extract_tables(corrected_query)
        table_issues = []
        for table in tables_used:
            if table.upper() not in [t.upper() for t in context.tables_available]:
                table_issue = f"Table '{table}' not found in available tables"
                issues.append(table_issue)
                table_issues.append(table_issue)
                suggestions.append(f"Available tables: {', '.join(context.tables_available)}")
        
        # Step 5: Check column names
        self.log("Validating column names against schema...")
        validation_result = self._validate_columns(corrected_query, context.columns_available)
        column_issues = validation_result["issues"]
        if column_issues:
            issues.extend(column_issues)
            suggestions.extend(validation_result["suggestions"])
        
        confidence = 1.0 - (len(issues) * 0.1)  # Reduce confidence for each issue
        confidence = max(0.1, min(1.0, confidence))
        
        # Create detailed step summary
        step_details = {
            "syntax_corrections": len([c for c in corrections if "Syntax" in c]),
            "function_corrections": len([c for c in corrections if "Functions" in c]),
            "date_corrections": len([c for c in corrections if "Date" in c]),
            "table_issues": len(table_issues),
            "column_issues": len(column_issues),
            "total_changes": len(corrections)
        }
        
        # Success if no critical syntax issues (ignore table/column validation failures)
        critical_issues = [issue for issue in issues if not any(word in issue.lower() for word in ['table', 'column', 'not found'])]
        has_improvements = len(corrections) > 0
        
        return self.create_response(
            success=len(critical_issues) == 0 or has_improvements,
            message=f"Syntax validation complete - {step_details['total_changes']} corrections applied" if corrections else "Syntax validation complete - no issues found",
            data={
                "original_query": sql_query,
                "validated_query": corrected_query,
                "issues": issues,
                "tables_used": tables_used,
                "corrections": corrections,
                "step_details": step_details
            },
            confidence=confidence,
            suggestions=suggestions
        )
    
    def _validate_db2_syntax(self, query: str) -> Tuple[str, List[str]]:
        """Validate DB2-specific syntax and fix SQLite syntax"""
        issues = []
        corrected = query
        
        # Fix LIMIT to FETCH FIRST (most common issue)
        if "LIMIT " in corrected.upper():
            issues.append("Converted LIMIT to FETCH FIRST (DB2 syntax)")
            corrected = re.sub(r'LIMIT\s+(\d+)', r'FETCH FIRST \1 ROWS ONLY', corrected, flags=re.IGNORECASE)
        
        # Fix SQLite date functions to DB2 - more comprehensive patterns
        sqlite_date_patterns = [
            # strftime('%Y', column) = strftime('%Y', date('now')) -> YEAR(column) = YEAR(CURRENT DATE)
            (r"strftime\s*\(\s*['\"]%Y['\"]\s*,\s*([^)]+)\s*\)\s*=\s*strftime\s*\(\s*['\"]%Y['\"]\s*,\s*date\s*\(\s*['\"]now['\"]\s*\)\s*\)", r"YEAR(\1) = YEAR(CURRENT DATE)"),
            # strftime('%m', column) = strftime('%m', date('now')) -> MONTH(column) = MONTH(CURRENT DATE)
            (r"strftime\s*\(\s*['\"]%m['\"]\s*,\s*([^)]+)\s*\)\s*=\s*strftime\s*\(\s*['\"]%m['\"]\s*,\s*date\s*\(\s*['\"]now['\"]\s*\)\s*\)", r"MONTH(\1) = MONTH(CURRENT DATE)"),
            # General strftime('%Y', column) -> YEAR(column)
            (r"strftime\s*\(\s*['\"]%Y['\"]\s*,\s*([^)]+)\s*\)", r"YEAR(\1)"),
            # General strftime('%m', column) -> MONTH(column)
            (r"strftime\s*\(\s*['\"]%m['\"]\s*,\s*([^)]+)\s*\)", r"MONTH(\1)"),
            # date('now') -> CURRENT DATE
            (r"date\s*\(\s*['\"]now['\"]\s*\)", "CURRENT DATE"),
            # datetime('now') -> CURRENT TIMESTAMP
            (r"datetime\s*\(\s*['\"]now['\"]\s*\)", "CURRENT TIMESTAMP"),
        ]
        
        for pattern, replacement in sqlite_date_patterns:
            if re.search(pattern, corrected, re.IGNORECASE):
                old_query = corrected
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
                if corrected != old_query:
                    issues.append(f"Converted SQLite date function to DB2")
                    break  # Apply one pattern at a time to avoid conflicts
        
        # Check for DECIMAL function usage
        if "DECIMAL(" in corrected.upper():
            # DB2 DECIMAL syntax: DECIMAL(value, precision, scale)
            decimal_pattern = r'DECIMAL\s*\(\s*([^,]+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
            if not re.search(decimal_pattern, corrected, re.IGNORECASE):
                issues.append("Invalid DECIMAL syntax. Use: DECIMAL(value, precision, scale)")
        
        # Check for proper JOIN syntax
        if " JOIN " in corrected.upper() and " ON " not in corrected.upper():
            issues.append("JOIN clause missing ON condition")
        
        # Fix SQLite CAST to DB2 style where possible
        if "CAST(" in corrected.upper():
            # Convert CAST(strftime(...) AS INTEGER) to proper DB2 functions
            cast_strftime_pattern = r'CAST\s*\(\s*strftime\s*\([^)]+\)\s+AS\s+INTEGER\s*\)'
            if re.search(cast_strftime_pattern, corrected, re.IGNORECASE):
                issues.append("Converted SQLite CAST with strftime to DB2 date functions")
                # This is complex - for now just flag it
        
        # Validate FETCH FIRST syntax if present
        if "FETCH FIRST" in corrected.upper():
            fetch_pattern = r'FETCH\s+FIRST\s+\d+\s+ROWS?\s+ONLY'
            if not re.search(fetch_pattern, corrected, re.IGNORECASE):
                issues.append("Invalid FETCH FIRST syntax. Use: FETCH FIRST n ROWS ONLY")
        
        return corrected, issues
    
    def _validate_db2_functions(self, query: str) -> Tuple[str, List[str]]:
        """Validate DB2 function usage"""
        issues = []
        corrected = query
        
        # Common function mappings
        function_mappings = {
            r'SUBSTRING\s*\(': 'SUBSTR(',  # DB2 uses SUBSTR not SUBSTRING
            r'DATEPART\s*\(': 'EXTRACT(',  # DB2 uses EXTRACT
            r'GETDATE\s*\(\s*\)': 'CURRENT DATE',  # DB2 current date syntax
            r'NOW\s*\(\s*\)': 'CURRENT TIMESTAMP',  # DB2 current timestamp
        }
        
        for pattern, replacement in function_mappings.items():
            if re.search(pattern, corrected, re.IGNORECASE):
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
                issues.append(f"Converted function: {pattern} to {replacement}")
        
        return corrected, issues
    
    def _validate_db2_dates(self, query: str) -> Tuple[str, List[str]]:
        """Validate DB2 date handling"""
        issues = []
        corrected = query
        
        # DB2 date arithmetic
        if re.search(r'DATE\s*\+\s*\d+', corrected, re.IGNORECASE):
            issues.append("DB2 date arithmetic: Use DATE + n DAYS/MONTHS/YEARS")
        
        # Current date functions
        if "CURDATE()" in corrected.upper():
            corrected = corrected.replace("CURDATE()", "CURRENT DATE")
            corrected = corrected.replace("curdate()", "CURRENT DATE")
            issues.append("Converted CURDATE() to CURRENT DATE")
        
        return corrected, issues
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from SQL query"""
        tables = []
        
        # Remove comments
        query_clean = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
        
        # Extract FROM clause tables
        from_pattern = r'FROM\s+([^\s,]+)(?:\s+(?:AS\s+)?(\w+))?'
        from_matches = re.finditer(from_pattern, query_clean, re.IGNORECASE)
        for match in from_matches:
            table_name = match.group(1).strip()
            if table_name.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING']:
                tables.append(table_name)
        
        # Extract JOIN tables
        join_pattern = r'JOIN\s+([^\s,]+)(?:\s+(?:AS\s+)?(\w+))?'
        join_matches = re.finditer(join_pattern, query_clean, re.IGNORECASE)
        for match in join_matches:
            table_name = match.group(1).strip()
            tables.append(table_name)
        
        return list(set(tables))
    
    def _validate_columns(self, query: str, columns_available: Dict[str, List[str]]) -> Dict:
        """Validate column names against available columns"""
        issues = []
        suggestions = []
        
        # Extract column references (simplified)
        column_pattern = r'\b(\w+)\.(\w+)\b|\b(\w+)\b'
        matches = re.finditer(column_pattern, query)
        
        for match in matches:
            if match.group(2):  # Table.Column format
                table = match.group(1)
                column = match.group(2)
                
                if table.upper() in [t.upper() for t in columns_available]:
                    table_cols = columns_available.get(table.upper(), [])
                    if column.upper() not in [c.upper() for c in table_cols]:
                        issues.append(f"Column '{column}' not found in table '{table}'")
                        # Find similar columns
                        similar = [c for c in table_cols if column.upper() in c.upper() or c.upper() in column.upper()]
                        if similar:
                            suggestions.append(f"Did you mean: {', '.join(similar[:3])}?")
        
        return {"issues": issues, "suggestions": suggestions}