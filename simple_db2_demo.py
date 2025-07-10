#!/usr/bin/env python3
"""
Simplified IBM DB2 Sales Pipeline Analytics Demo
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def create_demo_tables():
    """Create demo tables with sample data based on the MQT structure"""
    
    # Connect to database
    conn = sqlite3.connect('pipeline_demo.db')
    
    # Sample Pipeline data
    pipeline_data = {
        'CALL_AMT': [100000, 0, 250000, 0, 500000, 150000, 0, 300000],
        'WON_AMT': [0, 0, 0, 250000, 0, 0, 180000, 0],
        'UPSIDE_AMT': [0, 150000, 0, 0, 0, 0, 0, 200000],
        'QUALIFY_PLUS_AMT': [100000, 150000, 250000, 250000, 500000, 150000, 180000, 500000],
        'OPPORTUNITY_VALUE': [120000, 180000, 300000, 250000, 600000, 200000, 180000, 500000],
        'PPV_AMT': [80000, 90000, 200000, 250000, 400000, 120000, 180000, 300000],
        'SALES_STAGE': ['Negotiate', 'Propose', 'Closing', 'Won', 'Qualify', 'Closing', 'Won', 'Propose'],
        'GEOGRAPHY': ['Americas', 'Americas', 'EMEA', 'APAC', 'Americas', 'EMEA', 'APAC', 'Americas'],
        'MARKET': ['US Federal', 'US Commercial', 'UK Market', 'Japan Market', 'Canada Market', 'Germany Market', 'Australia', 'US Federal'],
        'CLIENT_NAME': ['Federal Agency A', 'Corp B', 'UK Corp C', 'Japan Inc', 'Canada Ltd', 'German Co', 'Aussie Corp', 'Federal Agency B'],
        'DEAL_SIZE': ['large', 'medium', 'large', 'medium', 'large', 'medium', 'small', 'large'],
        'YEAR': [2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
        'QUARTER': [1, 1, 1, 1, 1, 1, 1, 1],
        'WEEK': [3, 3, 3, 3, 3, 3, 3, 3]
    }
    
    pipeline_df = pd.DataFrame(pipeline_data)
    pipeline_df.to_sql('PROD_MQT_CONSULTING_PIPELINE', conn, if_exists='replace', index=False)
    
    # Sample Budget data
    budget_data = {
        'GEOGRAPHY': ['Americas', 'EMEA', 'APAC'],
        'MARKET': ['US Federal', 'UK Market', 'Japan Market'],
        'REVENUE_BUDGET_AMT': [2000000, 1500000, 1200000],
        'YEAR': [2025, 2025, 2025],
        'QUARTER': [1, 1, 1]
    }
    
    budget_df = pd.DataFrame(budget_data)
    budget_df.to_sql('PROD_MQT_CONSULTING_BUDGET', conn, if_exists='replace', index=False)
    
    print("✅ Demo tables created successfully")
    return conn

def run_sample_queries(conn):
    """Run sample queries and display results"""
    
    print("\n" + "="*60)
    print("📊 RUNNING SAMPLE QUERIES")
    print("="*60)
    
    # Query 1: Total Pipeline by Geography
    query1 = """
    SELECT 
        GEOGRAPHY,
        SUM(OPPORTUNITY_VALUE) / 1000 AS TOTAL_PIPELINE_K,
        SUM(QUALIFY_PLUS_AMT) / 1000 AS QUALIFIED_PIPELINE_K,
        SUM(PPV_AMT) / 1000 AS FORECAST_K
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY GEOGRAPHY
    ORDER BY TOTAL_PIPELINE_K DESC
    """
    
    df1 = pd.read_sql_query(query1, conn)
    print("\n🌍 PIPELINE BY GEOGRAPHY:")
    print(df1.to_string(index=False))
    
    # Query 2: Sales Stage Distribution
    query2 = """
    SELECT 
        SALES_STAGE,
        COUNT(*) AS DEAL_COUNT,
        SUM(OPPORTUNITY_VALUE) / 1000 AS VALUE_K,
        AVG(OPPORTUNITY_VALUE) / 1000 AS AVG_DEAL_SIZE_K
    FROM PROD_MQT_CONSULTING_PIPELINE
    GROUP BY SALES_STAGE
    ORDER BY 
        CASE SALES_STAGE
            WHEN 'Won' THEN 1
            WHEN 'Closing' THEN 2
            WHEN 'Negotiate' THEN 3
            WHEN 'Propose' THEN 4
            WHEN 'Qualify' THEN 5
            ELSE 6
        END
    """
    
    df2 = pd.read_sql_query(query2, conn)
    print("\n📈 SALES STAGE DISTRIBUTION:")
    print(df2.to_string(index=False))
    
    # Query 3: Forecast vs Budget
    query3 = """
    SELECT 
        p.GEOGRAPHY,
        SUM(p.PPV_AMT) / 1000 AS FORECAST_K,
        b.REVENUE_BUDGET_AMT / 1000 AS BUDGET_K,
        ROUND((SUM(p.PPV_AMT) * 100.0 / b.REVENUE_BUDGET_AMT), 1) AS COVERAGE_PCT
    FROM PROD_MQT_CONSULTING_PIPELINE p
    LEFT JOIN PROD_MQT_CONSULTING_BUDGET b
        ON p.GEOGRAPHY = b.GEOGRAPHY
    WHERE p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.GEOGRAPHY, b.REVENUE_BUDGET_AMT
    ORDER BY COVERAGE_PCT DESC
    """
    
    df3 = pd.read_sql_query(query3, conn)
    print("\n🎯 FORECAST VS BUDGET:")
    print(df3.to_string(index=False))
    
    # Query 4: Top Clients
    query4 = """
    SELECT 
        CLIENT_NAME,
        SUM(OPPORTUNITY_VALUE) / 1000 AS TOTAL_PIPELINE_K,
        COUNT(*) AS OPPORTUNITY_COUNT,
        MAX(SALES_STAGE) AS LATEST_STAGE
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY CLIENT_NAME
    ORDER BY TOTAL_PIPELINE_K DESC
    """
    
    df4 = pd.read_sql_query(query4, conn)
    print("\n👥 TOP CLIENTS BY PIPELINE:")
    print(df4.to_string(index=False))
    
    # Query 5: Win Rate Analysis
    query5 = """
    SELECT 
        GEOGRAPHY,
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) AS WON_DEALS,
        COUNT(*) AS TOTAL_DEALS,
        ROUND(SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS WIN_RATE_PCT,
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE ELSE 0 END) / 1000 AS WON_VALUE_K
    FROM PROD_MQT_CONSULTING_PIPELINE
    GROUP BY GEOGRAPHY
    ORDER BY WIN_RATE_PCT DESC
    """
    
    df5 = pd.read_sql_query(query5, conn)
    print("\n🏆 WIN RATE BY GEOGRAPHY:")
    print(df5.to_string(index=False))
    
    return [df1, df2, df3, df4, df5]

def create_visualizations(dataframes):
    """Create simple visualizations"""
    
    print("\n" + "="*60)
    print("📊 CREATING VISUALIZATIONS")
    print("="*60)
    
    df1, df2, df3, df4, df5 = dataframes
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('IBM Sales Pipeline Analytics Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Pipeline by Geography
    if not df1.empty:
        ax = axes[0, 0]
        df1.plot(x='GEOGRAPHY', y=['TOTAL_PIPELINE_K', 'QUALIFIED_PIPELINE_K', 'FORECAST_K'], 
                kind='bar', ax=ax, width=0.8)
        ax.set_title('Pipeline by Geography (K$)')
        ax.set_ylabel('Amount (K$)')
        ax.legend(['Total', 'Qualified', 'Forecast'])
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. Sales Stage Distribution
    if not df2.empty:
        ax = axes[0, 1]
        # Pie chart for deal count
        ax.pie(df2['DEAL_COUNT'], labels=df2['SALES_STAGE'], autopct='%1.1f%%', startangle=90)
        ax.set_title('Deal Distribution by Stage')
    
    # 3. Forecast vs Budget
    if not df3.empty:
        ax = axes[0, 2]
        x = np.arange(len(df3))
        width = 0.35
        
        ax.bar(x - width/2, df3['FORECAST_K'], width, label='Forecast', color='lightblue')
        ax.bar(x + width/2, df3['BUDGET_K'], width, label='Budget', color='lightcoral')
        
        ax.set_xlabel('Geography')
        ax.set_ylabel('Amount (K$)')
        ax.set_title('Forecast vs Budget')
        ax.set_xticks(x)
        ax.set_xticklabels(df3['GEOGRAPHY'], rotation=45, ha='right')
        ax.legend()
        
        # Add coverage percentage labels
        for i, pct in enumerate(df3['COVERAGE_PCT']):
            ax.text(i, max(df3['FORECAST_K'].iloc[i], df3['BUDGET_K'].iloc[i]) + 10,
                   f'{pct}%', ha='center', fontweight='bold')
    
    # 4. Top Clients
    if not df4.empty:
        ax = axes[1, 0]
        # Horizontal bar chart
        y_pos = np.arange(len(df4))
        ax.barh(y_pos, df4['TOTAL_PIPELINE_K'], color='green', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df4['CLIENT_NAME'])
        ax.set_xlabel('Pipeline Value (K$)')
        ax.set_title('Top Clients by Pipeline')
        
        # Add value labels
        for i, v in enumerate(df4['TOTAL_PIPELINE_K']):
            ax.text(v + 5, i, f'${v:.0f}K', va='center')
    
    # 5. Win Rate by Geography
    if not df5.empty:
        ax = axes[1, 1]
        # Scatter plot with bubble size
        scatter = ax.scatter(df5['WIN_RATE_PCT'], df5['WON_VALUE_K'], 
                           s=df5['WON_VALUE_K']*2, alpha=0.6, color='purple')
        for idx, row in df5.iterrows():
            ax.annotate(row['GEOGRAPHY'], (row['WIN_RATE_PCT'], row['WON_VALUE_K']),
                       fontsize=10, ha='center')
        ax.set_xlabel('Win Rate (%)')
        ax.set_ylabel('Won Value (K$)')
        ax.set_title('Win Rate vs Won Value')
        ax.grid(True, alpha=0.3)
    
    # 6. Deal Size Analysis
    ax = axes[1, 2]
    # Simple deal size simulation
    deal_sizes = ['small', 'medium', 'large']
    deal_counts = [2, 3, 3]  # From our sample data
    ax.pie(deal_counts, labels=deal_sizes, autopct='%1.1f%%', startangle=90)
    ax.set_title('Deal Distribution by Size')
    
    plt.tight_layout()
    plt.savefig('pipeline_dashboard_demo.png', dpi=300, bbox_inches='tight')
    print("✅ Dashboard saved as 'pipeline_dashboard_demo.png'")
    plt.show()

def generate_executive_summary(conn):
    """Generate executive summary"""
    
    print("\n" + "="*60)
    print("📋 EXECUTIVE SUMMARY")
    print("="*60)
    
    # Overall metrics
    query = """
    SELECT 
        COUNT(*) AS TOTAL_OPPORTUNITIES,
        SUM(OPPORTUNITY_VALUE) / 1000 AS TOTAL_PIPELINE_K,
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE ELSE 0 END) / 1000 AS WON_VALUE_K,
        COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS,
        AVG(OPPORTUNITY_VALUE) / 1000 AS AVG_DEAL_SIZE_K
    FROM PROD_MQT_CONSULTING_PIPELINE
    """
    
    df = pd.read_sql_query(query, conn)
    
    print(f"\n📊 KEY METRICS:")
    print(f"   Total Opportunities: {df['TOTAL_OPPORTUNITIES'].iloc[0]}")
    print(f"   Total Pipeline: ${df['TOTAL_PIPELINE_K'].iloc[0]:,.0f}K")
    print(f"   Won Value: ${df['WON_VALUE_K'].iloc[0]:,.0f}K")
    print(f"   Unique Clients: {df['UNIQUE_CLIENTS'].iloc[0]}")
    print(f"   Average Deal Size: ${df['AVG_DEAL_SIZE_K'].iloc[0]:,.0f}K")
    
    # Risk analysis
    query_risk = """
    SELECT 
        COUNT(CASE WHEN SALES_STAGE = 'Negotiate' AND CALL_AMT = 0 THEN 1 END) AS UNCOMMITTED_NEGOTIATE,
        COUNT(CASE WHEN SALES_STAGE = 'Qualify' THEN 1 END) AS EARLY_STAGE_DEALS,
        SUM(CASE WHEN SALES_STAGE = 'Closing' THEN OPPORTUNITY_VALUE ELSE 0 END) / 1000 AS CLOSING_PIPELINE_K
    FROM PROD_MQT_CONSULTING_PIPELINE
    """
    
    df_risk = pd.read_sql_query(query_risk, conn)
    
    print(f"\n⚠️  ATTENTION REQUIRED:")
    print(f"   Uncommitted Negotiate Deals: {df_risk['UNCOMMITTED_NEGOTIATE'].iloc[0]}")
    print(f"   Early Stage Deals: {df_risk['EARLY_STAGE_DEALS'].iloc[0]}")
    print(f"   Closing Pipeline: ${df_risk['CLOSING_PIPELINE_K'].iloc[0]:,.0f}K")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("   1. Focus on converting Negotiate stage deals to committed")
    print("   2. Accelerate qualification of early-stage opportunities")
    print("   3. Prioritize closing pipeline for end-of-quarter push")
    print("   4. Expand client base to reduce concentration risk")

def main():
    """Main execution function"""
    
    print("="*60)
    print("🚀 IBM DB2 SALES PIPELINE DEMO")
    print("="*60)
    
    # Create demo database and tables
    conn = create_demo_tables()
    
    # Run sample queries
    dataframes = run_sample_queries(conn)
    
    # Create visualizations
    create_visualizations(dataframes)
    
    # Generate executive summary
    generate_executive_summary(conn)
    
    # Close connection
    conn.close()
    
    print("\n✅ Demo completed successfully!")
    print("Check 'pipeline_dashboard_demo.png' for visualizations")

if __name__ == "__main__":
    main()