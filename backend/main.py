#!/usr/bin/env python3
"""
FastAPI Backend for IBM Sales Pipeline Analytics
Natural Language to SQL with Multi-Agent Enhancement
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import tempfile
import shutil

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Import our existing modules
from data_dictionary import DataDictionary
from database_manager import DatabaseManager
from llm_connector import LLMConnector
from agents import process_with_agents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IBM Sales Pipeline Analytics API",
    description="Natural Language to SQL Analytics with Multi-Agent Enhancement",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
app_state = {
    "data_dict": None,
    "db_manager": None,
    "llm_connector": None,
    "data_loaded": False,
    "llm_connected": False
}

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class ExecuteQueryRequest(BaseModel):
    sql_query: str

class LLMConfig(BaseModel):
    provider: str
    apiKey: Optional[str] = None
    model: str

@app.on_event("startup")
async def startup_event():
    """Initialize the application state"""
    logger.info("Starting IBM Sales Pipeline Analytics API")
    
    # Initialize data dictionary with built-in knowledge
    app_state["data_dict"] = DataDictionary()
    logger.info("Data dictionary initialized")
    
    # Initialize database manager
    app_state["db_manager"] = DatabaseManager()
    logger.info("Database manager initialized")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "IBM Sales Pipeline Analytics API",
        "status": "running",
        "data_loaded": app_state["data_loaded"],
        "llm_connected": app_state["llm_connected"]
    }

@app.get("/api/data-status")
async def get_data_status():
    """Get the current data loading status"""
    db_manager = app_state["db_manager"]
    if not db_manager:
        return {"tables_loaded": 0, "total_rows": 0, "loaded": False}
    
    tables_count = len(db_manager.tables_loaded) if db_manager.tables_loaded else 0
    total_rows = sum(
        info.get("rows", 0) for info in db_manager.tables_loaded.values()
    ) if db_manager.tables_loaded else 0
    
    return {
        "tables_loaded": tables_count,
        "total_rows": total_rows,
        "loaded": tables_count > 0,
        "table_info": db_manager.tables_loaded if db_manager.tables_loaded else {}
    }

@app.post("/api/upload-data")
async def upload_data(files: List[UploadFile] = File(...)):
    """Upload and process MQT data files"""
    try:
        db_manager = app_state["db_manager"]
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database manager not initialized")
        
        # Create temporary directory for uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            uploaded_files = []
            
            # Save uploaded files
            for file in files:
                if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
                    continue
                    
                file_path = Path(temp_dir) / file.filename
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                uploaded_files.append(file_path)
            
            if not uploaded_files:
                raise HTTPException(status_code=400, detail="No valid files uploaded")
            
            # Process uploaded files
            db_manager.load_uploaded_files(uploaded_files)
            app_state["data_loaded"] = True
            
            return {
                "message": "Files uploaded successfully",
                "files_processed": len(uploaded_files),
                "tables_loaded": len(db_manager.tables_loaded)
            }
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/load-demo-data")
async def load_demo_data():
    """Load demo data for testing"""
    try:
        db_manager = app_state["db_manager"]
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database manager not initialized")
        
        db_manager.create_demo_data()
        app_state["data_loaded"] = True
        
        return {
            "message": "Demo data loaded successfully",
            "tables_created": len(db_manager.tables_loaded),
            "total_rows": sum(info.get("rows", 0) for info in db_manager.tables_loaded.values())
        }
        
    except Exception as e:
        logger.error(f"Demo data loading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm-status")
async def get_llm_status():
    """Get the current LLM connection status"""
    llm_connector = app_state["llm_connector"]
    if not llm_connector or not llm_connector.connected:
        return {"connected": False}
    
    return {
        "connected": True,
        "provider": llm_connector.provider,
        "model": llm_connector.model_name
    }

@app.post("/api/connect-llm")
async def connect_llm(config: LLMConfig):
    """Connect to LLM provider"""
    try:
        llm_connector = LLMConnector(
            provider=config.provider,
            model_name=config.model,
            api_key=config.apiKey or ""
        )
        
        if not llm_connector.connected:
            raise HTTPException(status_code=400, detail="Failed to connect to LLM")
        
        app_state["llm_connector"] = llm_connector
        app_state["llm_connected"] = True
        
        return {
            "message": f"Successfully connected to {config.provider}",
            "provider": config.provider,
            "model": config.model
        }
        
    except Exception as e:
        logger.error(f"LLM connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-llm")
async def test_llm():
    """Test LLM connection with a simple query"""
    try:
        llm_connector = app_state["llm_connector"]
        if not llm_connector:
            raise HTTPException(status_code=400, detail="No LLM connected")
        
        # Simple test query
        test_result = llm_connector.generate_sql(
            "Show total pipeline value",
            "Test schema",
            "Test data dictionary"
        )
        
        return {
            "message": "LLM test successful",
            "test_result": test_result
        }
        
    except Exception as e:
        logger.error(f"LLM test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-query")
async def generate_query(request: QueryRequest):
    """Generate SQL query from natural language question"""
    try:
        # Check if services are ready
        if not app_state["llm_connected"]:
            raise HTTPException(status_code=400, detail="LLM not connected")
        
        if not app_state["data_loaded"]:
            raise HTTPException(status_code=400, detail="No data loaded")
        
        llm_connector = app_state["llm_connector"]
        db_manager = app_state["db_manager"]
        data_dict = app_state["data_dict"]
        
        # Generate initial SQL query
        schema_info = db_manager.schema_info
        comprehensive_context = data_dict.get_comprehensive_context()
        
        result = llm_connector.generate_sql(
            request.question, 
            schema_info, 
            comprehensive_context
        )
        
        if not result.get('sql_query'):
            raise HTTPException(status_code=500, detail="Failed to generate SQL query")
        
        # Process with multi-agent system
        agent_result = process_with_agents(
            sql_query=result.get('sql_query', ''),
            question=request.question,
            db_manager=db_manager,
            data_dict=data_dict,
            db_type='SQLite',
            llm_connector=llm_connector
        )
        
        if agent_result['success']:
            result['original_query'] = result['sql_query']
            result['final_query'] = agent_result['final_query']
            result['processing_log'] = agent_result['processing_log']
            result['overall_confidence'] = agent_result['overall_confidence']
            result['improvements'] = agent_result['improvements']
        else:
            result['final_query'] = result['sql_query']
            result['processing_log'] = []
            result['improvements'] = {}
        
        return result
        
    except Exception as e:
        logger.error(f"Query generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-query")
async def execute_query(request: ExecuteQueryRequest):
    """Execute SQL query and return results"""
    try:
        if not app_state["data_loaded"]:
            raise HTTPException(status_code=400, detail="No data loaded")
        
        db_manager = app_state["db_manager"]
        
        # Execute the query
        df = db_manager.execute_query(request.sql_query)
        
        if df.empty:
            return {
                "results": [],
                "columns": [],
                "row_count": 0,
                "message": "Query returned no results"
            }
        
        # Convert DataFrame to JSON-serializable format
        results = df.to_dict('records')
        columns = list(df.columns)
        
        return {
            "results": results,
            "columns": columns,
            "row_count": len(df),
            "message": f"Query executed successfully. {len(df)} rows returned."
        }
        
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)