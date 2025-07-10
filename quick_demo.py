#!/usr/bin/env python3
"""
Quick IBM DB2 Sales Pipeline Demo
Creates sample data and runs key queries
"""

import pandas as pd
import sqlite3

def main():
    print("🚀 IBM DB2 Sales Pipeline Demo")
    print("=" * 50)
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Sample data
    pipeline_data = {
        'CALL_AMT': [100000, 0, 250000, 0, 500000, 150000, 0, 300000],
        'WON_AMT': [0, 0, 0, 250000, 0, 0, 180000, 0],
        'OPPORTUNITY_VALUE': [120000, 180000, 300000, 250000, 600000, 200000, 180000, 500000],
        'PPV_AMT': [80000, 90000, 200000, 250000, 400000, 120000, 180000, 300000],
        'SALES_STAGE': ['Negotiate', 'Propose', 'Closing', 'Won', 'Qualify', 'Closing', 'Won', 'Propose'],
        'GEOGRAPHY': ['Americas', 'Americas', 'EMEA', 'APAC', 'Americas', 'EMEA', 'APAC', 'Americas'],
        'MARKET': ['US Federal', 'US Commercial', 'UK', 'Japan', 'Canada', 'Germany', 'Australia', 'US Federal'],
        'CLIENT_NAME': ['Fed Agency A', 'Corp B', 'UK Corp', 'Japan Inc', 'Canada Ltd', 'German Co', 'Aussie Corp', 'Fed Agency B']
    }
    
    df = pd.DataFrame(pipeline_data)
    df.to_sql('PIPELINE', conn, if_exists='replace', index=False)
    
    print(f"✅ Created demo table with {len(df)} opportunities")
    
    # Query 1: Total Pipeline
    print("\n📊 TOTAL PIPELINE VALUE:")
    query1 = "SELECT SUM(OPPORTUNITY_VALUE)/1000 AS TOTAL_K FROM PIPELINE WHERE SALES_STAGE NOT IN ('Won')"
    result1 = pd.read_sql_query(query1, conn)
    print(f"   Active Pipeline: ${result1['TOTAL_K'].iloc[0]:.0f}K")
    
    # Query 2: Pipeline by Geography
    print("\n🌍 PIPELINE BY GEOGRAPHY:")
    query2 = """
    SELECT 
        GEOGRAPHY,
        SUM(OPPORTUNITY_VALUE)/1000 AS PIPELINE_K,
        COUNT(*) AS DEALS
    FROM PIPELINE 
    WHERE SALES_STAGE NOT IN ('Won')
    GROUP BY GEOGRAPHY 
    ORDER BY PIPELINE_K DESC
    """
    result2 = pd.read_sql_query(query2, conn)
    for _, row in result2.iterrows():
        print(f"   {row['GEOGRAPHY']}: ${row['PIPELINE_K']:.0f}K ({row['DEALS']} deals)")
    
    # Query 3: Sales Stages
    print("\n📈 SALES STAGE DISTRIBUTION:")
    query3 = """
    SELECT 
        SALES_STAGE,
        COUNT(*) AS COUNT,
        SUM(OPPORTUNITY_VALUE)/1000 AS VALUE_K
    FROM PIPELINE 
    GROUP BY SALES_STAGE
    ORDER BY VALUE_K DESC
    """
    result3 = pd.read_sql_query(query3, conn)
    for _, row in result3.iterrows():
        print(f"   {row['SALES_STAGE']}: {row['COUNT']} deals, ${row['VALUE_K']:.0f}K")
    
    # Query 4: Win Rate
    print("\n🏆 WIN RATE ANALYSIS:")
    query4 = """
    SELECT 
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) AS WON,
        COUNT(*) AS TOTAL,
        ROUND(SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS WIN_RATE
    FROM PIPELINE
    """
    result4 = pd.read_sql_query(query4, conn)
    print(f"   Win Rate: {result4['WIN_RATE'].iloc[0]}% ({result4['WON'].iloc[0]} of {result4['TOTAL'].iloc[0]} deals)")
    
    # Query 5: Top Clients
    print("\n👥 TOP CLIENTS:")
    query5 = """
    SELECT 
        CLIENT_NAME,
        SUM(OPPORTUNITY_VALUE)/1000 AS PIPELINE_K
    FROM PIPELINE 
    WHERE SALES_STAGE NOT IN ('Won')
    GROUP BY CLIENT_NAME 
    ORDER BY PIPELINE_K DESC 
    LIMIT 5
    """
    result5 = pd.read_sql_query(query5, conn)
    for _, row in result5.iterrows():
        print(f"   {row['CLIENT_NAME']}: ${row['PIPELINE_K']:.0f}K")
    
    # Action Items
    print("\n🎯 KEY INSIGHTS & ACTIONS:")
    
    # Find deals needing attention
    query6 = """
    SELECT CLIENT_NAME, OPPORTUNITY_VALUE/1000 AS VALUE_K, SALES_STAGE
    FROM PIPELINE 
    WHERE SALES_STAGE = 'Negotiate' AND CALL_AMT = 0
    """
    result6 = pd.read_sql_query(query6, conn)
    if not result6.empty:
        print(f"   ⚠️  {len(result6)} deals in Negotiate without commitment:")
        for _, row in result6.iterrows():
            print(f"      - {row['CLIENT_NAME']}: ${row['VALUE_K']:.0f}K")
    
    # Large deals in early stages
    query7 = """
    SELECT CLIENT_NAME, OPPORTUNITY_VALUE/1000 AS VALUE_K, SALES_STAGE
    FROM PIPELINE 
    WHERE SALES_STAGE IN ('Qualify', 'Propose') AND OPPORTUNITY_VALUE > 300000
    """
    result7 = pd.read_sql_query(query7, conn)
    if not result7.empty:
        print(f"   🔥 {len(result7)} large deals need acceleration:")
        for _, row in result7.iterrows():
            print(f"      - {row['CLIENT_NAME']}: ${row['VALUE_K']:.0f}K ({row['SALES_STAGE']})")
    
    # Closing opportunities
    closing_query = "SELECT COUNT(*) as COUNT, SUM(OPPORTUNITY_VALUE)/1000 as VALUE_K FROM PIPELINE WHERE SALES_STAGE = 'Closing'"
    closing_result = pd.read_sql_query(closing_query, conn)
    if closing_result['COUNT'].iloc[0] > 0:
        print(f"   🎯 {closing_result['COUNT'].iloc[0]} deals ready to close: ${closing_result['VALUE_K'].iloc[0]:.0f}K")
    
    conn.close()
    print(f"\n✅ Demo completed successfully!")

if __name__ == "__main__":
    main()