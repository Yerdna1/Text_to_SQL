#!/usr/bin/env python3
"""
Test script for the multi-agent SQL orchestration system
"""

from sql_agent_orchestrator import SQLAgentOrchestrator, QueryContext

def test_orchestrator():
    """Test the orchestrator with a simple example"""
    
    # Create orchestrator
    orchestrator = SQLAgentOrchestrator()
    
    # Test query
    test_query = "SELECT SUM(PPV_AMT) FROM PROD_MQT_CONSULTING_PIPELINE"
    test_question = "What is the total AI revenue forecast for Americas in Q4 2024?"
    
    # Mock context
    context = QueryContext(
        question=test_question,
        schema_info="Table: PROD_MQT_CONSULTING_PIPELINE\nColumns: PPV_AMT, GEOGRAPHY, YEAR, QUARTER, IBM_GEN_AI_IND, SALES_STAGE, SNAPSHOT_LEVEL, WEEK",
        data_dictionary="PPV_AMT: AI-based revenue forecast",
        tables_available=["PROD_MQT_CONSULTING_PIPELINE"],
        columns_available={
            "PROD_MQT_CONSULTING_PIPELINE": ["PPV_AMT", "GEOGRAPHY", "YEAR", "QUARTER", "IBM_GEN_AI_IND", "SALES_STAGE", "SNAPSHOT_LEVEL", "WEEK"]
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
    
    print("🔍 Original Query:")
    print(result["original_query"])
    print("\n✨ Enhanced Query:")
    print(result["final_query"])
    print(f"\n📊 Overall Confidence: {result['overall_confidence']:.0%}")
    print(f"\n✅ Success: {result['success']}")
    
    if result["success"]:
        improvements = result.get("improvements", {})
        print(f"\n🔧 Improvements Made:")
        print(f"  • Syntax corrections: {improvements.get('syntax_corrections', 0)}")
        print(f"  • WHERE enhancements: {improvements.get('where_enhancements', 0)}")
        print(f"  • Optimizations: {improvements.get('optimizations', 0)}")
        
        print(f"\n📝 Processing Log:")
        for step in result["processing_log"]:
            print(f"  • {step['agent']}: {step['message']}")
            if step.get('enhancements'):
                for enhancement in step['enhancements']:
                    print(f"    - {enhancement}")
    
    return result

if __name__ == "__main__":
    print("🚀 Testing Multi-Agent SQL Orchestration System\n")
    result = test_orchestrator()
    print("\n✅ Test completed!")