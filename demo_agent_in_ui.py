#!/usr/bin/env python3
"""
Demo: Agent Processing in UI
Simple Streamlit demo to show agent processing steps
"""

import streamlit as st
from sql_agent_orchestrator import process_with_agents
from receptionist_agent import create_step_visualization
from create_interactive_app import DatabaseManager, DataDictionary

def main():
    st.title("🤖 Multi-Agent SQL Enhancement Demo")
    st.write("This demo shows how the multi-agent system processes and enhances SQL queries.")
    
    # Mock LLM connector
    class MockLLM:
        def generate_sql(self, question, schema, context):
            return {'sql_query': 'SELECT OPPORTUNITY_ID FROM PROD_MQT_CONSULTING_PIPELINE'}
    
    # Input section
    st.subheader("📝 Input")
    
    col1, col2 = st.columns(2)
    with col1:
        question = st.text_input(
            "Question:", 
            value="Show me won deals with opportunity IDs"
        )
        
    with col2:
        test_query = st.text_area(
            "SQL Query:", 
            value="""SELECT MARKET, OPPORTUNITY_ID, SALES_STAGE 
FROM PROD_MQT_CONSULTING_PIPELINE 
WHERE SALES_STAGE = 'Won'""",
            height=100
        )
    
    if st.button("🚀 Process with Multi-Agent System"):
        
        with st.spinner("🤖 Processing with agents..."):
            # Create mock objects
            db_manager = DatabaseManager()
            db_manager.tables_loaded = {}  # Empty to trigger default schema
            data_dict = DataDictionary()
            llm_connector = MockLLM()
            
            # Process with agents
            result = process_with_agents(
                sql_query=test_query,
                question=question,
                db_manager=db_manager,
                data_dict=data_dict,
                db_type='SQLite',
                llm_connector=llm_connector
            )
        
        # Display results
        st.subheader("📊 Agent Processing Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Success", "✅" if result.get('success') else "❌")
        with col2:
            st.metric("Processing Steps", len(result.get('processing_log', [])))
        with col3:
            st.metric("Query Enhanced", "✅" if result.get('final_query') != test_query else "❌")
        
        # Show detailed processing steps
        st.subheader("🔍 Processing Pipeline")
        if result.get('processing_log'):
            create_step_visualization(result['processing_log'])
        else:
            st.warning("No processing steps found")
        
        # Show before/after comparison
        if result.get('final_query') != test_query:
            st.subheader("🔄 Query Transformation")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**📝 Original Query:**")
                st.code(test_query, language='sql')
                
            with col2:
                st.write("**✨ Enhanced Query:**")
                st.code(result.get('final_query', ''), language='sql')
            
            # Highlight changes
            if 'OPPORTUNITY_ID' in test_query and 'OPPTY_ID' in result.get('final_query', ''):
                st.success("🔄 **Column Mapping Applied**: OPPORTUNITY_ID → OPPTY_ID")
            
        # Show explanation
        if result.get('explanation'):
            st.subheader("💡 Explanation")
            st.info(result['explanation'])
        
        # Raw result data (for debugging)
        with st.expander("🔧 Raw Agent Data (Debug)", expanded=False):
            st.json(result)

if __name__ == "__main__":
    main()