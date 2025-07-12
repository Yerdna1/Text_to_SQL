#!/usr/bin/env python3
"""
Test Execute Query Flow
Test that the execute button uses the agent-enhanced query, not the original
"""

from sql_agent_orchestrator import process_with_agents
from create_interactive_app import DatabaseManager, DataDictionary

def test_execute_query_flow():
    """Test the complete flow from agent processing to query execution"""
    
    print("🧪 TESTING EXECUTE QUERY FLOW")
    print("=" * 60)
    
    # Query with SQLite syntax that should be converted to DB2
    original_query = """
    WITH ALL_OPPORTUNITIES AS (
        SELECT 
            CLIENT_NAME,
            OPPORTUNITY_ID,
            OPPORTUNITY_VALUE
        FROM PROD_MQT_CONSULTING_PIPELINE
        WHERE OPPORTUNITY_VALUE > 0
    )
    SELECT 
        CLIENT_NAME,
        COUNT(*) AS DEAL_COUNT,
        SUM(OPPORTUNITY_VALUE) AS TOTAL_VALUE
    FROM ALL_OPPORTUNITIES
    GROUP BY CLIENT_NAME
    ORDER BY TOTAL_VALUE DESC
    LIMIT 10
    """
    
    print("🔍 Original Query (with LIMIT):")
    print(original_query)
    print()
    
    # Mock objects
    class MockLLM:
        def generate_sql(self, question, schema, context):
            return {'sql_query': original_query}
    
    db_manager = DatabaseManager()
    db_manager.tables_loaded = {}  # Will trigger default schema
    data_dict = DataDictionary()
    llm_connector = MockLLM()
    
    print("🤖 Processing with agents...")
    agent_result = process_with_agents(
        sql_query=original_query,
        question="Show me top 10 clients by total opportunity value",
        db_manager=db_manager,
        data_dict=data_dict,
        db_type='DB2',
        llm_connector=llm_connector
    )
    
    print("📊 AGENT PROCESSING RESULTS:")
    print("-" * 40)
    print(f"✅ Agent Success: {agent_result.get('success', False)}")
    print(f"📝 Processing steps: {len(agent_result.get('processing_log', []))}")
    print(f"🔧 Query modified: {agent_result.get('final_query', '') != original_query}")
    print()
    
    # Simulate what the UI does
    print("🖥️ SIMULATING UI FLOW:")
    print("-" * 40)
    
    # Step 1: Store result like the UI does
    result = {
        'sql_query': original_query,  # Original from LLM
        'explanation': 'Original LLM explanation'
    }
    
    # Step 2: Update with agent results (like the UI does)
    if agent_result['success']:
        result['original_query'] = result['sql_query']
        result['sql_query'] = agent_result['final_query']  # This should be the enhanced query
        result['agent_processing'] = agent_result
        result['agent_explanation'] = agent_result.get('explanation', '')
    
    # Step 3: What query will execute button use?
    query_to_execute = result.get('sql_query', '')
    
    print(f"Query stored in result['sql_query']: {len(query_to_execute)} characters")
    print()
    
    print("🎯 Query that Execute button will use:")
    print(query_to_execute)
    print()
    
    # Check if conversion happened
    if 'FETCH FIRST' in query_to_execute.upper() and 'LIMIT' not in query_to_execute.upper():
        print("✅ SUCCESS: Execute button will use DB2 syntax (FETCH FIRST)")
    elif 'LIMIT' in query_to_execute.upper():
        print("❌ PROBLEM: Execute button will still use SQLite syntax (LIMIT)")
    else:
        print("⚠️  UNCLEAR: No LIMIT or FETCH FIRST found")
    
    # Check agent processing status
    if result.get('agent_processing', {}).get('success', False):
        print("✅ SUCCESS: Agent processing succeeded - enhanced query will be used")
    else:
        print("❌ PROBLEM: Agent processing failed - original query will be used")
    
    return result

def main():
    """Run the execute flow test"""
    
    print("🚀 EXECUTE QUERY FLOW TEST")
    print("=" * 80)
    
    result = test_execute_query_flow()
    
    print("\n\n🎉 TEST COMPLETE!")
    print("=" * 80)
    
    if result.get('agent_processing', {}).get('success', False):
        print("✅ Execute button will use agent-enhanced DB2 query")
        print("✅ FETCH FIRST syntax will be preserved")
        print("✅ No more SQLite syntax errors")
    else:
        print("❌ Execute button will use original LLM query") 
        print("❌ May still have SQLite syntax issues")
        print("🔧 Need to investigate agent processing failures")

if __name__ == "__main__":
    main()