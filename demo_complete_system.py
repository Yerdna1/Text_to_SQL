#!/usr/bin/env python3
"""
Complete Demo of Enhanced Multi-Agent SQL Orchestration System
Shows all features: Receptionist Agent + Multi-Agent Pipeline + Detailed Visualization
"""

from sql_agent_orchestrator import SQLAgentOrchestrator, QueryContext
from receptionist_agent import ReceptionistAgent, create_step_visualization
import json

def demo_receptionist_agent():
    """Demo the receptionist agent functionality"""
    print("🤖 RECEPTIONIST AGENT DEMO")
    print("=" * 50)
    
    receptionist = ReceptionistAgent()
    
    # Test cases showing different levels of completeness
    test_cases = [
        {
            "question": "What is the total revenue?",
            "description": "Incomplete question - missing everything"
        },
        {
            "question": "Show me Americas pipeline",
            "description": "Partial context - missing time and metric"
        },
        {
            "question": "What is the AI revenue forecast for Americas in Q4 2024?",
            "description": "Complete context - should proceed directly"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {case['description']}")
        print(f"Question: '{case['question']}'")
        
        # Analyze the question
        context, missing = receptionist.analyze_question(case['question'])
        
        print(f"Context Confidence: {context.confidence_level:.0%}")
        print(f"Should Intervene: {receptionist.should_intervene(case['question'])}")
        
        # Show what was detected
        detected = []
        if context.time_period: detected.append(f"Time: {context.time_period}")
        if context.geography: detected.append(f"Geography: {context.geography}")
        if context.product_type: detected.append(f"Product: {context.product_type}")
        if context.metric_focus: detected.append(f"Metric: {context.metric_focus}")
        
        if detected:
            print(f"✅ Detected: {', '.join(detected)}")
        
        # Show what's missing
        missing_items = []
        if missing.needs_time: missing_items.append("Time Period")
        if missing.needs_geography: missing_items.append("Geography")
        if missing.needs_product: missing_items.append("Product Type")
        if missing.needs_metric: missing_items.append("Metric Focus")
        
        if missing_items:
            print(f"❌ Missing: {', '.join(missing_items)}")
            
            # Show suggestions
            for category, suggestions in missing.suggestions.items():
                if suggestions:
                    print(f"💡 {category.title()} suggestions: {', '.join(suggestions[:3])}")
        
        # Show refined question if complete
        if context.confidence_level >= 0.75:
            refined = receptionist._build_refined_question(context)
            print(f"✨ Refined question: '{refined}'")
        
        print("-" * 40)

def demo_detailed_agent_processing():
    """Demo detailed step-by-step agent processing"""
    print("\n\n🔬 DETAILED AGENT PROCESSING DEMO")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = SQLAgentOrchestrator()
    
    # Test with a complex scenario
    test_query = "SELECT PPV_AMT, CLIENT_NAME FROM PROD_MQT_CONSULTING_PIPELINE"
    test_question = "What is the GenAI revenue forecast for EMEA markets in current quarter?"
    
    # Mock context (simulating real app context)
    context = QueryContext(
        question=test_question,
        schema_info="Table: PROD_MQT_CONSULTING_PIPELINE\nColumns: PPV_AMT, CLIENT_NAME, GEOGRAPHY, YEAR, QUARTER, IBM_GEN_AI_IND, SALES_STAGE, SNAPSHOT_LEVEL, WEEK",
        data_dictionary="PPV_AMT: AI-based revenue forecast\nCLIENT_NAME: Customer name\nGEOGRAPHY: Regional classification",
        tables_available=["PROD_MQT_CONSULTING_PIPELINE"],
        columns_available={
            "PROD_MQT_CONSULTING_PIPELINE": ["PPV_AMT", "CLIENT_NAME", "GEOGRAPHY", "YEAR", "QUARTER", "IBM_GEN_AI_IND", "SALES_STAGE", "SNAPSHOT_LEVEL", "WEEK"]
        },
        db_type="SQLite"
    )
    
    print(f"🔍 Original Query: {test_query}")
    print(f"❓ User Question: {test_question}")
    print(f"🎯 Database Type: {context.db_type}")
    print()
    
    # Process through agent pipeline
    result = orchestrator.process_query(
        initial_query=test_query,
        question=test_question,
        schema_info=context.schema_info,
        data_dictionary=context.data_dictionary,
        tables_available=context.tables_available,
        columns_available=context.columns_available,
        db_type=context.db_type
    )
    
    print("🚀 AGENT PROCESSING PIPELINE")
    print("=" * 30)
    
    # Show each agent's detailed steps
    for i, step in enumerate(result["processing_log"], 1):
        agent_name = step['agent']
        success = step['success']
        message = step['message']
        
        status_icon = "✅" if success else "❌"
        print(f"\n{status_icon} STEP {i}: {agent_name}")
        print(f"   Message: {message}")
        
        if agent_name == "DB2SyntaxValidator":
            if step.get('confidence'):
                print(f"   Confidence: {step['confidence']:.0%}")
            # Could show detailed syntax corrections here
            
        elif agent_name == "WhereClauseEnhancer":
            if step.get('enhancements'):
                print("   🎯 Enhancements Applied:")
                for enhancement in step['enhancements']:
                    print(f"      • {enhancement}")
                    
        elif agent_name == "QueryOptimizer":
            if step.get('optimizations'):
                print("   🚀 Optimizations Applied:")
                for opt in step['optimizations']:
                    print(f"      • {opt}")
        
        print("   " + "─" * 40)
    
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 20)
    print(f"✨ Enhanced Query:")
    print(f"   {result['final_query']}")
    print(f"\n📊 Overall Confidence: {result['overall_confidence']:.0%}")
    
    # Show improvements summary
    improvements = result.get("improvements", {})
    print(f"\n🔧 Improvements Summary:")
    print(f"   • Syntax corrections: {improvements.get('syntax_corrections', 0)}")
    print(f"   • WHERE enhancements: {improvements.get('where_enhancements', 0)}")
    print(f"   • Optimizations: {improvements.get('optimizations', 0)}")

def demo_receptionist_with_agent_flow():
    """Demo complete flow: Receptionist -> Agent Processing"""
    print("\n\n🔄 COMPLETE WORKFLOW DEMO")
    print("=" * 50)
    
    # Simulate incomplete user question
    incomplete_question = "Show me the pipeline"
    
    print(f"👤 User asks: '{incomplete_question}'")
    
    # Step 1: Receptionist analysis
    print("\n🤖 RECEPTIONIST ANALYSIS:")
    receptionist = ReceptionistAgent()
    context, missing = receptionist.analyze_question(incomplete_question)
    
    print(f"   Initial confidence: {context.confidence_level:.0%}")
    print(f"   Should intervene: {receptionist.should_intervene(incomplete_question)}")
    
    # Simulate user providing missing context through buttons
    print("\n💬 USER PROVIDES MISSING CONTEXT:")
    print("   [User clicks: 'Current Quarter']")
    print("   [User clicks: 'Americas']") 
    print("   [User clicks: 'AI/GenAI Solutions']")
    print("   [User clicks: 'Revenue Forecast']")
    
    # Update context (simulating user selections)
    context.time_period = "Current Quarter"
    context.geography = "Americas"
    context.product_type = "AI/GenAI Solutions"
    context.metric_focus = "Revenue Forecast"
    context.confidence_level = 1.0
    
    # Build refined question
    refined_question = receptionist._build_refined_question(context)
    print(f"\n✨ REFINED QUESTION: '{refined_question}'")
    
    # Step 2: Generate initial SQL (simulated LLM response)
    print("\n🧠 LLM GENERATES INITIAL SQL:")
    initial_sql = "SELECT SUM(PPV_AMT) AS total_forecast FROM PROD_MQT_CONSULTING_PIPELINE"
    print(f"   {initial_sql}")
    
    # Step 3: Agent processing
    print("\n🤖 MULTI-AGENT ENHANCEMENT:")
    
    # Create context for agents
    agent_context = QueryContext(
        question=refined_question,
        schema_info="Table: PROD_MQT_CONSULTING_PIPELINE\nColumns: PPV_AMT, GEOGRAPHY, YEAR, QUARTER, IBM_GEN_AI_IND, SALES_STAGE, SNAPSHOT_LEVEL, WEEK",
        data_dictionary="PPV_AMT: AI-based revenue forecast",
        tables_available=["PROD_MQT_CONSULTING_PIPELINE"],
        columns_available={
            "PROD_MQT_CONSULTING_PIPELINE": ["PPV_AMT", "GEOGRAPHY", "YEAR", "QUARTER", "IBM_GEN_AI_IND", "SALES_STAGE", "SNAPSHOT_LEVEL", "WEEK"]
        },
        db_type="SQLite"
    )
    
    # Process with agents
    orchestrator = SQLAgentOrchestrator()
    result = orchestrator.process_query(
        initial_query=initial_sql,
        question=refined_question,
        schema_info=agent_context.schema_info,
        data_dictionary=agent_context.data_dictionary,
        tables_available=agent_context.tables_available,
        columns_available=agent_context.columns_available,
        db_type=agent_context.db_type
    )
    
    print(f"   ✅ Processing complete!")
    print(f"   🎯 Final enhanced query ready for execution")
    
    print(f"\n🏆 FINAL ENHANCED SQL:")
    print(f"   {result['final_query']}")
    
    print(f"\n📈 TRANSFORMATION SUMMARY:")
    print(f"   • Started with: Vague question ('{incomplete_question}')")
    print(f"   • Receptionist guided user to provide complete context")
    print(f"   • Refined to: Specific question ('{refined_question}')")
    print(f"   • LLM generated: Basic SQL")
    print(f"   • Agents enhanced: Context-aware, optimized SQL")
    print(f"   • Result: Production-ready query with all necessary filters")

def main():
    """Run complete system demo"""
    print("🚀 ENHANCED MULTI-AGENT SQL SYSTEM - COMPLETE DEMO")
    print("=" * 60)
    print("This demo shows the complete workflow:")
    print("1. 🤖 Receptionist Agent - Guides users to provide complete context")
    print("2. 🔬 Multi-Agent Processing - Validates, enhances, and optimizes SQL")
    print("3. 📊 Detailed Visualization - Shows step-by-step processing")
    print("4. 🔄 Complete Workflow - End-to-end user experience")
    print()
    
    # Run all demos
    demo_receptionist_agent()
    demo_detailed_agent_processing() 
    demo_receptionist_with_agent_flow()
    
    print("\n\n🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("🌟 KEY BENEFITS:")
    print("✅ Users get guided assistance for incomplete questions")
    print("✅ SQL queries are automatically enhanced with contextual filters")
    print("✅ Full transparency with step-by-step processing visualization")
    print("✅ Higher accuracy and more relevant results")
    print("✅ Works with both single LLM and parallel (3-LLM) modes")
    print("\n🚀 Ready for production deployment in IBM Sales Pipeline Analytics!")

if __name__ == "__main__":
    main()