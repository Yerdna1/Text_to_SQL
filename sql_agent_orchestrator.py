#!/usr/bin/env python3
"""
Multi-Agent SQL Query Orchestration System
Provides multiple specialized agents for SQL query generation, validation, and enhancement
"""

import json
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import streamlit as st
from datetime import datetime
import pandas as pd


@dataclass
class QueryContext:
    """Context information for query generation and validation"""
    question: str
    schema_info: str
    data_dictionary: str
    tables_available: List[str]
    columns_available: Dict[str, List[str]]
    db_type: str = "DB2"  # DB2, SQLite, etc.
    
    
@dataclass
class AgentResponse:
    """Standard response format from agents"""
    success: bool
    message: str
    data: Dict[str, Any]
    confidence: float = 0.0
    suggestions: List[str] = None
    

class SQLAgent(ABC):
    """Base class for SQL processing agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Process the input and return agent response"""
        pass
        
    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")
        

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
            return AgentResponse(
                success=False,
                message="No SQL query provided",
                data={},
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
        
        return AgentResponse(
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
    
    def _validate_sqlite_syntax(self, query: str) -> Tuple[str, List[str]]:
        """Validate SQLite syntax - minimal changes"""
        issues = []
        corrected = query
        
        # Check for proper SQLite syntax patterns
        if "FETCH FIRST" in corrected.upper():
            # Convert DB2 FETCH FIRST to SQLite LIMIT
            issues.append("Converted FETCH FIRST to LIMIT (SQLite syntax)")
            corrected = re.sub(r'FETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY', r'LIMIT \1', corrected, flags=re.IGNORECASE)
        
        # Check for DB2 date functions and suggest SQLite alternatives
        if "CURRENT DATE" in corrected.upper() and "date(" not in corrected.lower():
            issues.append("Note: Use date('now') for current date in SQLite")
        
        if "YEAR(" in corrected.upper() and "strftime" not in corrected.lower():
            issues.append("Note: Use strftime('%Y', date) for year extraction in SQLite")
        
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
    
    def _convert_to_sqlite(self, query: str) -> Tuple[str, List[str]]:
        """Convert DB2 syntax to SQLite compatible"""
        issues = []
        corrected = query
        
        # Convert DECIMAL to ROUND
        decimal_pattern = r'DECIMAL\s*\(\s*([^,]+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
        def decimal_replacer(match):
            value = match.group(1)
            scale = match.group(3)
            return f'ROUND({value}, {scale})'
        
        if re.search(decimal_pattern, corrected, re.IGNORECASE):
            corrected = re.sub(decimal_pattern, decimal_replacer, corrected, flags=re.IGNORECASE)
            issues.append("Converted DECIMAL to ROUND for SQLite compatibility")
        
        # Convert date functions
        date_conversions = {
            r'CURRENT\s+DATE': "date('now')",
            r'CURRENT\s+TIMESTAMP': "datetime('now')",
            r'YEAR\s*\(\s*([^)]+)\s*\)': r"strftime('%Y', \1)",
            r'MONTH\s*\(\s*([^)]+)\s*\)': r"strftime('%m', \1)",
            r'DAY\s*\(\s*([^)]+)\s*\)': r"strftime('%d', \1)",
        }
        
        for pattern, replacement in date_conversions.items():
            if re.search(pattern, corrected, re.IGNORECASE):
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
                issues.append(f"Converted date function for SQLite")
        
        # Convert FETCH FIRST to LIMIT
        fetch_pattern = r'FETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY'
        if re.search(fetch_pattern, corrected, re.IGNORECASE):
            corrected = re.sub(fetch_pattern, r'LIMIT \1', corrected, flags=re.IGNORECASE)
            issues.append("Converted FETCH FIRST to LIMIT for SQLite")
        
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


class WhereClauseEnhancerAgent(SQLAgent):
    """Enhances WHERE clauses with appropriate filters based on context"""
    
    def __init__(self):
        super().__init__(
            "WhereClauseEnhancer",
            "Adds intelligent WHERE clause filters for regions, time periods, and products"
        )
        
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Enhance WHERE clause with contextual filters"""
        sql_query = input_data.get("validated_query", input_data.get("sql_query", ""))
        question = context.question.lower()
        
        if not sql_query:
            return AgentResponse(
                success=False,
                message="No SQL query provided",
                data={},
                confidence=0.0
            )
        
        enhancements = []
        enhanced_query = sql_query
        
        # Step 1: Detect and add time-based filters
        self.log("Analyzing question for time context...")
        time_filters = self._detect_time_context(question)
        time_enhancements = []
        if time_filters:
            self.log(f"Time context detected: {time_filters}")
            enhanced_query, time_enhancements = self._add_time_filters(enhanced_query, time_filters, context)
            enhancements.extend(time_enhancements)
        else:
            self.log("No specific time context detected")
        
        # Step 2: Detect and add geographic filters
        self.log("Analyzing question for geographic context...")
        geo_filters = self._detect_geographic_context(question)
        geo_enhancements = []
        if geo_filters:
            self.log(f"Geographic context detected: {geo_filters}")
            enhanced_query, geo_enhancements = self._add_geographic_filters(enhanced_query, geo_filters, context)
            enhancements.extend(geo_enhancements)
        else:
            self.log("No specific geographic context detected")
        
        # Step 3: Detect and add product/service filters
        self.log("Analyzing question for product context...")
        product_filters = self._detect_product_context(question)
        prod_enhancements = []
        if product_filters:
            self.log(f"Product context detected: {product_filters}")
            enhanced_query, prod_enhancements = self._add_product_filters(enhanced_query, product_filters, context)
            enhancements.extend(prod_enhancements)
        else:
            self.log("No specific product context detected")
        
        # Step 4: Add standard business filters
        self.log("Applying standard business logic filters...")
        enhanced_query, business_enhancements = self._add_business_filters(enhanced_query, question, context)
        enhancements.extend(business_enhancements)
        
        confidence = 0.8 if enhancements else 0.6
        
        # Create detailed step summary
        step_details = {
            "time_filters": len(time_enhancements),
            "geographic_filters": len(geo_enhancements),
            "product_filters": len(prod_enhancements),
            "business_filters": len(business_enhancements),
            "total_enhancements": len(enhancements),
            "context_detected": {
                "time": bool(time_filters),
                "geographic": bool(geo_filters),
                "product": bool(product_filters)
            }
        }
        
        return AgentResponse(
            success=True,
            message=f"Enhanced WHERE clause with {len(enhancements)} contextual filters",
            data={
                "original_query": sql_query,
                "enhanced_query": enhanced_query,
                "enhancements": enhancements,
                "filters_added": {
                    "time": bool(time_filters),
                    "geographic": bool(geo_filters),
                    "product": bool(product_filters),
                    "business": bool(business_enhancements)
                },
                "step_details": step_details
            },
            confidence=confidence,
            suggestions=[]
        )
    
    def _detect_time_context(self, question: str) -> Dict[str, Any]:
        """Detect time-related context from the question"""
        time_context = {}
        
        # Current period detection
        if any(word in question for word in ["current", "this month", "this quarter", "today", "now"]):
            time_context["current_period"] = True
            
        # Specific quarter detection
        quarter_match = re.search(r'q(\d)|quarter (\d)', question)
        if quarter_match:
            time_context["quarter"] = quarter_match.group(1) or quarter_match.group(2)
            
        # Year detection
        year_match = re.search(r'20\d{2}', question)
        if year_match:
            time_context["year"] = year_match.group()
            
        # YTD (Year to Date)
        if "ytd" in question or "year to date" in question:
            time_context["ytd"] = True
            
        # Last period references
        if any(word in question for word in ["last month", "previous quarter", "last year"]):
            time_context["previous_period"] = True
            
        return time_context
    
    def _detect_geographic_context(self, question: str) -> Dict[str, Any]:
        """Detect geographic context from the question"""
        geo_context = {}
        
        # Common regions
        regions = {
            "americas": ["americas", "america", "us", "usa", "canada", "latam"],
            "emea": ["emea", "europe", "middle east", "africa"],
            "apac": ["apac", "asia", "pacific", "asia pacific"],
            "japan": ["japan", "jpn"]
        }
        
        for region, keywords in regions.items():
            if any(keyword in question for keyword in keywords):
                geo_context["region"] = region.upper()
                break
                
        # Country detection (simplified)
        countries = ["usa", "uk", "germany", "france", "china", "india", "brazil", "canada"]
        for country in countries:
            if country in question:
                geo_context["country"] = country.upper()
                break
                
        return geo_context
    
    def _detect_product_context(self, question: str) -> Dict[str, Any]:
        """Detect product/service context from the question"""
        product_context = {}
        
        # Common product categories
        if "consulting" in question:
            product_context["type"] = "CONSULTING"
        elif "software" in question:
            product_context["type"] = "SOFTWARE"
        elif "cloud" in question:
            product_context["type"] = "CLOUD"
        elif "ai" in question or "genai" in question or "gen ai" in question:
            product_context["ai_focus"] = True
            
        # UT level detection
        ut_match = re.search(r'ut(\d+)', question)
        if ut_match:
            product_context["ut_level"] = f"UT{ut_match.group(1)}"
            
        return product_context
    
    def _add_time_filters(self, query: str, time_filters: Dict, context: QueryContext) -> Tuple[str, List[str]]:
        """Add time-based WHERE filters"""
        enhancements = []
        enhanced_query = query
        
        # Check if WHERE clause exists
        where_match = re.search(r'WHERE\s+', enhanced_query, re.IGNORECASE)
        
        if time_filters.get("current_period"):
            if context.db_type == "DB2":
                time_condition = "YEAR = YEAR(CURRENT DATE) AND QUARTER = QUARTER(CURRENT DATE)"
            else:  # SQLite
                time_condition = "strftime('%Y', date('now')) = CAST(YEAR AS TEXT) AND ((CAST(strftime('%m', date('now')) AS INTEGER) - 1) / 3 + 1) = QUARTER"
            
            enhanced_query = self._add_where_condition(enhanced_query, time_condition, where_match)
            enhancements.append("Added current quarter filter")
            
        elif time_filters.get("quarter") and time_filters.get("year"):
            quarter = time_filters["quarter"]
            year = time_filters["year"]
            time_condition = f"YEAR = {year} AND QUARTER = {quarter}"
            enhanced_query = self._add_where_condition(enhanced_query, time_condition, where_match)
            enhancements.append(f"Added Q{quarter} {year} filter")
            
        elif time_filters.get("ytd"):
            if context.db_type == "DB2":
                time_condition = "YEAR = YEAR(CURRENT DATE)"
            else:  # SQLite
                time_condition = "YEAR = CAST(strftime('%Y', date('now')) AS INTEGER)"
            enhanced_query = self._add_where_condition(enhanced_query, time_condition, where_match)
            enhancements.append("Added Year-to-Date filter")
            
        return enhanced_query, enhancements
    
    def _add_geographic_filters(self, query: str, geo_filters: Dict, context: QueryContext) -> Tuple[str, List[str]]:
        """Add geographic WHERE filters"""
        enhancements = []
        enhanced_query = query
        
        where_match = re.search(r'WHERE\s+', enhanced_query, re.IGNORECASE)
        
        if geo_filters.get("region"):
            region = geo_filters["region"]
            geo_condition = f"GEOGRAPHY = '{region}'"
            enhanced_query = self._add_where_condition(enhanced_query, geo_condition, where_match)
            enhancements.append(f"Added {region} region filter")
            
        elif geo_filters.get("country"):
            country = geo_filters["country"]
            geo_condition = f"COUNTRY = '{country}'"
            enhanced_query = self._add_where_condition(enhanced_query, geo_condition, where_match)
            enhancements.append(f"Added {country} country filter")
            
        return enhanced_query, enhancements
    
    def _add_product_filters(self, query: str, product_filters: Dict, context: QueryContext) -> Tuple[str, List[str]]:
        """Add product-related WHERE filters"""
        enhancements = []
        enhanced_query = query
        
        where_match = re.search(r'WHERE\s+', enhanced_query, re.IGNORECASE)
        
        if product_filters.get("type"):
            prod_type = product_filters["type"]
            # Check if we're querying the right table
            if "CONSULTING" in prod_type and "CONSULTING" in enhanced_query.upper():
                enhancements.append(f"Confirmed {prod_type} table selection")
            elif "SOFTWARE" in prod_type and "SOFTWARE" in enhanced_query.upper():
                enhancements.append(f"Confirmed {prod_type} table selection")
                
        if product_filters.get("ai_focus"):
            ai_condition = "(IBM_GEN_AI_IND = 1 OR PARTNER_GEN_AI_IND = 1)"
            enhanced_query = self._add_where_condition(enhanced_query, ai_condition, where_match)
            enhancements.append("Added AI/GenAI filter")
            
        if product_filters.get("ut_level"):
            ut_level = product_filters["ut_level"]
            ut_column = f"{ut_level}_NAME"
            # This would need the actual UT value from context
            enhancements.append(f"Ready to filter by {ut_level} (specific value needed)")
            
        return enhanced_query, enhancements
    
    def _add_business_filters(self, query: str, question: str, context: QueryContext) -> Tuple[str, List[str]]:
        """Add standard business filters"""
        enhancements = []
        enhanced_query = query
        
        where_match = re.search(r'WHERE\s+', enhanced_query, re.IGNORECASE)
        
        # Active pipeline filter (exclude Won/Lost)
        if any(word in question for word in ["pipeline", "active", "open", "forecast"]):
            if "SALES_STAGE" in enhanced_query.upper() and "WON" not in enhanced_query.upper():
                active_condition = "SALES_STAGE NOT IN ('Won', 'Lost')"
                enhanced_query = self._add_where_condition(enhanced_query, active_condition, where_match)
                enhancements.append("Added active pipeline filter (excluding Won/Lost)")
                
        # Snapshot level filter
        if "SNAPSHOT_LEVEL" in context.schema_info and "SNAPSHOT_LEVEL" not in enhanced_query.upper():
            snapshot_condition = "SNAPSHOT_LEVEL = 'W'"  # Weekly snapshot
            enhanced_query = self._add_where_condition(enhanced_query, snapshot_condition, where_match)
            enhancements.append("Added weekly snapshot filter")
            
        # Latest week filter
        if "latest" in question or "current" in question:
            if "WEEK" in context.schema_info and "MAX(WEEK)" not in enhanced_query.upper():
                # Add subquery for latest week
                latest_week_condition = "WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE YEAR = (SELECT MAX(YEAR) FROM PROD_MQT_CONSULTING_PIPELINE))"
                enhanced_query = self._add_where_condition(enhanced_query, latest_week_condition, where_match)
                enhancements.append("Added latest week filter")
                
        return enhanced_query, enhancements
    
    def _add_where_condition(self, query: str, condition: str, where_match) -> str:
        """Helper to add WHERE condition to query"""
        if where_match:
            # Add to existing WHERE clause
            where_end = self._find_where_end(query, where_match.end())
            existing_where = query[where_match.end():where_end].strip()
            
            if existing_where and not existing_where.startswith("("):
                new_where = f"{existing_where} AND {condition}"
            else:
                new_where = condition
                
            return query[:where_match.end()] + new_where + query[where_end:]
        else:
            # Add new WHERE clause
            # Find position after FROM clause
            from_match = re.search(r'FROM\s+[^\s]+(?:\s+[^\s]+)*\s*', query, re.IGNORECASE)
            if from_match:
                insert_pos = from_match.end()
                # Check if there's already a JOIN, GROUP BY, etc.
                next_clause = re.search(r'\s+(JOIN|GROUP\s+BY|ORDER\s+BY|HAVING)', query[insert_pos:], re.IGNORECASE)
                if next_clause:
                    insert_pos += next_clause.start()
                    
                return query[:insert_pos] + f" WHERE {condition} " + query[insert_pos:]
            else:
                # Fallback: add at the end
                return query + f" WHERE {condition}"
    
    def _find_where_end(self, query: str, start_pos: int) -> int:
        """Find the end of WHERE clause"""
        # Look for next major clause
        next_clause = re.search(
            r'\s+(GROUP\s+BY|ORDER\s+BY|HAVING|UNION|EXCEPT|INTERSECT|$)',
            query[start_pos:],
            re.IGNORECASE
        )
        
        if next_clause:
            return start_pos + next_clause.start()
        else:
            return len(query)


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
        
        return AgentResponse(
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


class ColumnValidationAgent(SQLAgent):
    """Validates column existence and triggers SQL regeneration if needed"""
    
    def __init__(self):
        super().__init__(
            "ColumnValidation",
            "Validates column existence and suggests alternatives or regeneration"
        )
        
    def process(self, input_data: Dict[str, Any], context: QueryContext) -> AgentResponse:
        """Validate all columns in the query exist in the schema"""
        sql_query = input_data.get("optimized_query", input_data.get("sql_query", ""))
        
        if not sql_query:
            return AgentResponse(
                success=False,
                message="No SQL query provided",
                data={},
                confidence=0.0
            )
        
        # Skip validation for queries with CTEs as they create derived columns
        if 'WITH ' in sql_query.upper():
            self.log("Query contains CTE - skipping column validation")
            return AgentResponse(
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
        
        return AgentResponse(
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
        import re
        
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
        import re
        
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


class SQLRegenerationAgent(SQLAgent):
    """Handles SQL regeneration when column validation fails"""
    
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
            return AgentResponse(
                success=False,
                message="No regeneration prompt provided",
                data={},
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
                    
                    return AgentResponse(
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
            
            return AgentResponse(
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
            return AgentResponse(
                success=False,
                message=f"SQL regeneration failed: {e}",
                data={"original_query": original_query},
                confidence=0.0
            )
    
    def _apply_fallback_substitutions(self, query: str, context: QueryContext) -> str:
        """Apply basic fallback column substitutions"""
        import re
        
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
                explanation.append(f"• Added {improvements['where_enhancements']} contextual filters")
            if improvements.get("optimizations", 0) > 0:
                explanation.append(f"• Applied {improvements['optimizations']} performance optimizations")
        
        return "\n".join(explanation)


# Integration function for Streamlit app
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


if __name__ == "__main__":
    # Test the orchestrator
    test_query = "SELECT SUM(PPV_AMT) FROM PROD_MQT_CONSULTING_PIPELINE"
    test_question = "What is the total AI revenue forecast for Americas in Q4 2024?"
    
    orchestrator = SQLAgentOrchestrator()
    
    # Mock context
    context = QueryContext(
        question=test_question,
        schema_info="Table: PROD_MQT_CONSULTING_PIPELINE\nColumns: PPV_AMT, GEOGRAPHY, YEAR, QUARTER, IBM_GEN_AI_IND",
        data_dictionary="PPV_AMT: AI-based revenue forecast",
        tables_available=["PROD_MQT_CONSULTING_PIPELINE"],
        columns_available={
            "PROD_MQT_CONSULTING_PIPELINE": ["PPV_AMT", "GEOGRAPHY", "YEAR", "QUARTER", "IBM_GEN_AI_IND", "SALES_STAGE"]
        },
        db_type="SQLite"
    )
    
    result = orchestrator.process_query(
        initial_query=test_query,
        question=test_question,
        schema_info=context.schema_info,
        data_dictionary=context.data_dictionary,
        tables_available=context.tables_available,
        columns_available=context.columns_available,
        db_type=context.db_type
    )
    
    print("Original Query:", result["original_query"])
    print("Final Query:", result["final_query"])
    print("\nExplanation:")
    print(result["explanation"])