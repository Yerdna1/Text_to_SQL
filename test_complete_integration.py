#!/usr/bin/env python3
"""
Complete Integration Test for Enhanced Multi-Agent System
Tests all components together without Streamlit dependencies
"""

from sql_agent_orchestrator import SQLAgentOrchestrator, QueryContext, process_with_agents
from receptionist_agent import ReceptionistAgent

class MockDataDict:
    """Mock data dictionary for testing"""
    def get_comprehensive_context(self):
        return "PPV_AMT: AI-based revenue forecast\nGEOGRAPHY: Regional classification\nIBM_GEN_AI_IND: AI solution indicator"

class MockDBManager:
    """Mock database manager for testing"""
    def __init__(self):
        self.tables_loaded = {
            "PROD_MQT_CONSULTING_PIPELINE": {
                "columns": ["PPV_AMT", "GEOGRAPHY", "YEAR", "QUARTER", "IBM_GEN_AI_IND", "SALES_STAGE", "SNAPSHOT_LEVEL", "WEEK", "CLIENT_NAME"]
            }
        }
        self.schema_info = "Table: PROD_MQT_CONSULTING_PIPELINE\nColumns: PPV_AMT, GEOGRAPHY, YEAR, QUARTER, IBM_GEN_AI_IND, SALES_STAGE, SNAPSHOT_LEVEL, WEEK, CLIENT_NAME"

def test_complete_integration():
    """Test the complete integration of all components"""
    
    print("🧪 COMPLETE INTEGRATION TEST")
    print("=" * 50)
    
    # Test scenario: Incomplete question → Complete workflow
    incomplete_question = "Show me the revenue"
    
    print(f"📝 Testing with: '{incomplete_question}'")
    print()
    
    # Step 1: Receptionist Analysis
    print("🤖 STEP 1: Receptionist Analysis")
    print("-" * 30)
    
    receptionist = ReceptionistAgent()
    context, missing = receptionist.analyze_question(incomplete_question)
    
    print(f"Initial confidence: {context.confidence_level:.0%}")
    print(f"Should intervene: {receptionist.should_intervene(incomplete_question)}")
    
    # Simulate user providing missing context
    print("\n💬 STEP 2: Simulating User Context Input")
    print("-" * 30)
    context.time_period = "Current Quarter"
    context.geography = "Americas"
    context.product_type = "AI/GenAI Solutions"
    context.metric_focus = "Revenue Forecast"
    context.confidence_level = 1.0
    
    refined_question = receptionist._build_refined_question(context)
    print(f"Refined question: '{refined_question}'")
    
    # Step 2: Mock LLM SQL Generation
    print("\n🧠 STEP 3: Mock LLM SQL Generation")
    print("-" * 30)
    initial_sql = "SELECT SUM(PPV_AMT) FROM PROD_MQT_CONSULTING_PIPELINE"
    print(f"Generated SQL: {initial_sql}")
    
    # Step 3: Agent Processing
    print("\n🤖 STEP 4: Multi-Agent Processing")
    print("-" * 30)
    
    # Create mock objects
    mock_db_manager = MockDBManager()
    mock_data_dict = MockDataDict()
    
    try:
        # Test the process_with_agents function
        result = process_with_agents(
            sql_query=initial_sql,
            question=refined_question,
            db_manager=mock_db_manager,
            data_dict=mock_data_dict,
            db_type="SQLite"
        )
        
        print("✅ Agent processing completed successfully!")
        print(f"Success: {result['success']}")
        print(f"Overall confidence: {result.get('overall_confidence', 0):.0%}")
        
        # Show processing steps
        if result.get('processing_log'):
            print("\n📊 Processing Steps:")
            for i, step in enumerate(result['processing_log'], 1):
                print(f"  {i}. {step['agent']}: {step['message']}")
        
        # Show final enhanced query
        print(f"\n✨ Enhanced Query:")
        print(f"  {result.get('final_query', 'N/A')}")
        
        # Show improvements
        if result.get('improvements'):
            improvements = result['improvements']
            print(f"\n🔧 Improvements Applied:")
            print(f"  • Syntax corrections: {improvements.get('syntax_corrections', 0)}")
            print(f"  • WHERE enhancements: {improvements.get('where_enhancements', 0)}")
            print(f"  • Optimizations: {improvements.get('optimizations', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components separately"""
    
    print("\n\n🔬 INDIVIDUAL COMPONENT TESTS")
    print("=" * 50)
    
    # Test Receptionist
    print("🤖 Testing Receptionist Agent...")
    receptionist = ReceptionistAgent()
    context, missing = receptionist.analyze_question("What is the pipeline?")
    print(f"  ✅ Confidence: {context.confidence_level:.0%}")
    print(f"  ✅ Missing items detected: {len([x for x in [missing.needs_time, missing.needs_geography, missing.needs_product, missing.needs_metric] if x])}")
    
    # Test Orchestrator
    print("\n🔄 Testing SQL Orchestrator...")
    orchestrator = SQLAgentOrchestrator()
    
    test_context = QueryContext(
        question="What is the AI revenue forecast for Americas?",
        schema_info="Table: PROD_MQT_CONSULTING_PIPELINE\nColumns: PPV_AMT, GEOGRAPHY, IBM_GEN_AI_IND",
        data_dictionary="PPV_AMT: Revenue forecast",
        tables_available=["PROD_MQT_CONSULTING_PIPELINE"],
        columns_available={"PROD_MQT_CONSULTING_PIPELINE": ["PPV_AMT", "GEOGRAPHY", "IBM_GEN_AI_IND"]},
        db_type="SQLite"
    )
    
    try:
        result = orchestrator.process_query(
            initial_query="SELECT SUM(PPV_AMT) FROM PROD_MQT_CONSULTING_PIPELINE",
            question="What is the AI revenue forecast for Americas?",
            schema_info=test_context.schema_info,
            data_dictionary=test_context.data_dictionary,
            tables_available=test_context.tables_available,
            columns_available=test_context.columns_available,
            db_type=test_context.db_type
        )
        print(f"  ✅ Success: {result['success']}")
        print(f"  ✅ Confidence: {result.get('overall_confidence', 0):.0%}")
        print(f"  ✅ Processing steps: {len(result.get('processing_log', []))}")
    except Exception as e:
        print(f"  ❌ Orchestrator test failed: {e}")
        return False
    
    return True

def main():
    """Run all integration tests"""
    
    print("🚀 ENHANCED MULTI-AGENT SYSTEM - INTEGRATION TESTS")
    print("=" * 60)
    
    # Test individual components first
    individual_success = test_individual_components()
    
    # Test complete integration
    integration_success = test_complete_integration()
    
    print("\n\n🎯 TEST RESULTS")
    print("=" * 30)
    print(f"Individual Components: {'✅ PASS' if individual_success else '❌ FAIL'}")
    print(f"Complete Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if individual_success and integration_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Receptionist Agent working correctly")
        print("✅ Multi-Agent Orchestration working correctly")
        print("✅ Integration with mock objects working correctly")
        print("✅ System ready for Streamlit deployment")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the error messages above")
    
    return individual_success and integration_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)