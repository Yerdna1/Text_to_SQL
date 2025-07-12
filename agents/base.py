#!/usr/bin/env python3
"""
Base classes and data structures for SQL agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import streamlit as st


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
        """Log a message with agent name prefix"""
        print(f"[{self.name}] {message}")
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data structure"""
        return isinstance(input_data, dict) and 'sql_query' in input_data
        
    def create_response(self, success: bool, message: str, data: Dict[str, Any] = None, 
                       confidence: float = 0.0, suggestions: List[str] = None) -> AgentResponse:
        """Helper method to create standardized responses"""
        return AgentResponse(
            success=success,
            message=message,
            data=data or {},
            confidence=confidence,
            suggestions=suggestions or []
        )