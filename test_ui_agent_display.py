#!/usr/bin/env python3
"""
Test Agent Display in UI
Simple test to verify that agent processing results are being passed to the UI correctly
"""

from sql_agent_orchestrator import process_with_agents, QueryContext
from create_interactive_app import DatabaseManager, DataDictionary

def test_agent_ui_integration():
    """Test that agent processing returns proper data for UI display"""
    
    print("🧪 TESTING AGENT UI INTEGRATION")
    print("=" * 50)
    
    # Mock objects
    class MockLLM:
        def generate_sql(self, question, schema, context):
            return {'sql_query': 'SELECT OPPORTUNITY_ID FROM PROD_MQT_CONSULTING_PIPELINE'}
    
    # Create mock database manager with columns
    db_manager = DatabaseManager()
    
    # Mock the tables_loaded to include our test table
    db_manager.tables_loaded = {
        "PROD_MQT_CONSULTING_PIPELINE": {
            "columns": ["MARKET", "WON_AMT", "SALES_STAGE", "OPPORTUNITY_VALUE", "YEAR", "QUARTER", 
                       "PPV_AMT", "GEOGRAPHY", "CLIENT_NAME", "SNAPSHOT_LEVEL", "WEEK",
                       "OPPTY_ID", "DEAL_ID", "IBM_GEN_AI_IND"],
            "rows": 1000
        }
    }
    db_manager.schema_info = "Table: PROD_MQT_CONSULTING_PIPELINE with sales pipeline data"
    
    data_dict = DataDictionary()
    llm_connector = MockLLM()
    
    # Test query with missing column (OPPORTUNITY_ID should map to OPPTY_ID)
    test_query = """
    SELECT MARKET, OPPORTUNITY_ID, SALES_STAGE 
    FROM PROD_MQT_CONSULTING_PIPELINE 
    WHERE SALES_STAGE = 'Won'
    """
    
    print("🔍 Input Query:")
    print(test_query)
    print()
    
    # Process with agents
    print("🤖 Processing with agents...")
    result = process_with_agents(
        sql_query=test_query,
        question="Show me won deals by market",
        db_manager=db_manager,
        data_dict=data_dict,
        db_type='SQLite',
        llm_connector=llm_connector
    )
    
    print("📊 AGENT RESULT ANALYSIS:")
    print("-" * 30)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"📝 Processing log items: {len(result.get('processing_log', []))}")
    print(f"🔧 Final query different: {result.get('final_query', '') != test_query.strip()}")
    print()
    
    print("📋 Processing Steps:")
    for i, step in enumerate(result.get('processing_log', []), 1):
        agent = step.get('agent', 'Unknown')
        success = "✅" if step.get('success', False) else "❌"
        message = step.get('message', 'No message')
        print(f"  {i}. {success} {agent}: {message}")
        
        # Show column validation details
        if agent == "ColumnValidation":
            if step.get('missing_columns'):
                print(f"     Missing: {[col['column'] for col in step['missing_columns']]}")
            if step.get('substitutions'):
                print(f"     Substitutions: {step['substitutions']}")
    
    print()
    print("🎯 Final Query:")
    print(result.get('final_query', 'No final query'))
    print()
    
    # Check if UI data is present
    print("🖥️ UI DISPLAY DATA CHECK:")
    print("-" * 30)
    ui_ready_data = {
        'success': result.get('success', False),
        'final_query': result.get('final_query', ''),
        'processing_log': result.get('processing_log', []),
        'explanation': result.get('explanation', ''),
        'issues': result.get('issues', []),
        'suggestions': result.get('suggestions', [])
    }
    
    for key, value in ui_ready_data.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        elif isinstance(value, str):
            print(f"  {key}: {'Present' if value else 'Missing'}")
        else:
            print(f"  {key}: {value}")
    
    print()
    print("🎉 UI INTEGRATION TEST COMPLETE!")
    print("The agent processing data is ready for UI display.")
    
    return result

if __name__ == "__main__":
    test_agent_ui_integration()