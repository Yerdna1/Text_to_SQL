#!/usr/bin/env python3
"""
IBM DB2 Sales Pipeline Analytics Simulation
Creates tables from Excel data, runs SQL queries, and generates visualizations
"""

import pandas as pd
import sqlite3  # Using SQLite as DB2 simulator (similar SQL syntax)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class DB2Simulator:
    def __init__(self, db_name='sales_pipeline.db'):
        """Initialize DB2 simulator with SQLite"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        print("🚀 DB2 Simulator initialized")
        
    def load_excel_to_db(self, excel_path, table_name):
        """Load Excel/CSV file into database table"""
        try:
            # Read CSV file
            df = pd.read_csv(excel_path)
            
            # Clean column names (remove special characters)
            df.columns = [col.upper().replace(' ', '_').replace('/', '_') for col in df.columns]
            
            # Write to database
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            print(f"✅ Loaded {len(df)} rows into {table_name}")
            
            return df
        except Exception as e:
            print(f"❌ Error loading {excel_path}: {str(e)}")
            return None
    
    def execute_query(self, query, description=""):
        """Execute a SQL query and return results as DataFrame"""
        try:
            df = pd.read_sql_query(query, self.conn)
            if description:
                print(f"\n📊 {description}")
            print(f"   Returned {len(df)} rows")
            return df
        except Exception as e:
            print(f"❌ Query error: {str(e)}")
            return None
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n🔒 Database connection closed")

def create_visualizations(db):
    """Create comprehensive visualizations from query results"""
    
    print("\n" + "="*60)
    print("📈 GENERATING VISUALIZATIONS")
    print("="*60)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 24))
    
    # 1. Pipeline by Geography
    ax1 = plt.subplot(4, 3, 1)
    query1 = """
    SELECT 
        GEOGRAPHY,
        SUM(OPPORTUNITY_VALUE) / 1000000 AS PIPELINE_M,
        SUM(QUALIFY_PLUS_AMT) / 1000000 AS QUALIFIED_M,
        SUM(PPV_AMT) / 1000000 AS FORECAST_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY GEOGRAPHY
    ORDER BY PIPELINE_M DESC
    LIMIT 10
    """
    df1 = db.execute_query(query1, "Pipeline by Geography")
    if df1 is not None and not df1.empty:
        df1.plot(x='GEOGRAPHY', y=['PIPELINE_M', 'QUALIFIED_M', 'FORECAST_M'], 
                kind='bar', ax=ax1, width=0.8)
        ax1.set_title('Pipeline by Geography ($M)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Geography')
        ax1.set_ylabel('Amount ($M)')
        ax1.legend(['Total Pipeline', 'Qualified', 'Forecast'])
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. Sales Stage Distribution
    ax2 = plt.subplot(4, 3, 2)
    query2 = """
    SELECT 
        SALES_STAGE,
        COUNT(*) AS DEAL_COUNT,
        SUM(OPPORTUNITY_VALUE) / 1000000 AS VALUE_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY SALES_STAGE
    ORDER BY 
        CASE SALES_STAGE
            WHEN 'Closing' THEN 1
            WHEN 'Negotiate' THEN 2
            WHEN 'Propose' THEN 3
            WHEN 'Qualify' THEN 4
            WHEN 'Design' THEN 5
            WHEN 'Engage' THEN 6
            ELSE 7
        END
    """
    df2 = db.execute_query(query2, "Sales Stage Distribution")
    if df2 is not None and not df2.empty:
        # Create dual-axis plot
        ax2_twin = ax2.twinx()
        df2.plot(x='SALES_STAGE', y='VALUE_M', kind='bar', ax=ax2, color='skyblue', alpha=0.7)
        df2.plot(x='SALES_STAGE', y='DEAL_COUNT', kind='line', ax=ax2_twin, 
                color='red', marker='o', linewidth=2, markersize=8)
        ax2.set_title('Sales Funnel Analysis', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Pipeline Value ($M)', color='skyblue')
        ax2_twin.set_ylabel('Deal Count', color='red')
        ax2.tick_params(axis='y', labelcolor='skyblue')
        ax2_twin.tick_params(axis='y', labelcolor='red')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax2.legend(['Pipeline Value'], loc='upper left')
        ax2_twin.legend(['Deal Count'], loc='upper right')
    
    # 3. Win Rate Analysis
    ax3 = plt.subplot(4, 3, 3)
    query3 = """
    WITH win_analysis AS (
        SELECT 
            GEOGRAPHY,
            SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) AS WON,
            SUM(CASE WHEN SALES_STAGE IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS CLOSED,
            SUM(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE ELSE 0 END) / 1000000 AS WON_VALUE_M
        FROM PROD_MQT_CONSULTING_PIPELINE
        GROUP BY GEOGRAPHY
        HAVING CLOSED > 0
    )
    SELECT 
        GEOGRAPHY,
        CAST(WON AS FLOAT) * 100 / CLOSED AS WIN_RATE,
        WON_VALUE_M
    FROM win_analysis
    ORDER BY WIN_RATE DESC
    LIMIT 10
    """
    df3 = db.execute_query(query3, "Win Rate by Geography")
    if df3 is not None and not df3.empty:
        # Scatter plot with bubble size
        scatter = ax3.scatter(df3['WIN_RATE'], df3['WON_VALUE_M'], 
                            s=df3['WON_VALUE_M']*10, alpha=0.6)
        for idx, row in df3.iterrows():
            ax3.annotate(row['GEOGRAPHY'], (row['WIN_RATE'], row['WON_VALUE_M']),
                        fontsize=8, ha='center')
        ax3.set_title('Win Rate vs Won Value', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Win Rate (%)')
        ax3.set_ylabel('Won Value ($M)')
        ax3.grid(True, alpha=0.3)
    
    # 4. Pipeline Coverage vs Budget
    ax4 = plt.subplot(4, 3, 4)
    query4 = """
    SELECT 
        p.MARKET,
        SUM(p.PPV_AMT) / 1000000 AS FORECAST_M,
        SUM(b.REVENUE_BUDGET_AMT) / 1000000 AS BUDGET_M,
        CASE 
            WHEN SUM(b.REVENUE_BUDGET_AMT) > 0 
            THEN (SUM(p.PPV_AMT) / SUM(b.REVENUE_BUDGET_AMT)) * 100
            ELSE 0 
        END AS COVERAGE_PCT
    FROM PROD_MQT_CONSULTING_PIPELINE p
    LEFT JOIN PROD_MQT_CONSULTING_BUDGET b
        ON p.GEOGRAPHY = b.GEOGRAPHY 
        AND p.MARKET = b.MARKET
        AND p.YEAR = b.YEAR
        AND p.QUARTER = b.QUARTER
    WHERE p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.MARKET
    HAVING SUM(b.REVENUE_BUDGET_AMT) > 0
    ORDER BY COVERAGE_PCT DESC
    LIMIT 15
    """
    df4 = db.execute_query(query4, "Pipeline Coverage vs Budget")
    if df4 is not None and not df4.empty:
        # Horizontal bar chart
        y_pos = np.arange(len(df4))
        bars = ax4.barh(y_pos, df4['COVERAGE_PCT'])
        
        # Color bars based on coverage
        for i, (bar, coverage) in enumerate(zip(bars, df4['COVERAGE_PCT'])):
            if coverage >= 100:
                bar.set_color('green')
            elif coverage >= 80:
                bar.set_color('yellow')
            else:
                bar.set_color('red')
        
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(df4['MARKET'])
        ax4.set_xlabel('Coverage %')
        ax4.set_title('Pipeline Coverage by Market', fontsize=14, fontweight='bold')
        ax4.axvline(x=100, color='black', linestyle='--', alpha=0.5)
        
        # Add value labels
        for i, v in enumerate(df4['COVERAGE_PCT']):
            ax4.text(v + 1, i, f'{v:.0f}%', va='center')
    
    # 5. Deal Size Distribution
    ax5 = plt.subplot(4, 3, 5)
    query5 = """
    SELECT 
        DEAL_SIZE,
        COUNT(*) AS COUNT,
        AVG(OPPORTUNITY_VALUE) / 1000000 AS AVG_VALUE_M,
        SUM(OPPORTUNITY_VALUE) / 1000000 AS TOTAL_VALUE_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
        AND DEAL_SIZE IS NOT NULL
    GROUP BY DEAL_SIZE
    """
    df5 = db.execute_query(query5, "Deal Size Distribution")
    if df5 is not None and not df5.empty:
        # Pie chart for deal count
        ax5.pie(df5['COUNT'], labels=df5['DEAL_SIZE'], autopct='%1.1f%%', startangle=90)
        ax5.set_title('Deal Distribution by Size (Count)', fontsize=14, fontweight='bold')
    
    # 6. YoY Performance
    ax6 = plt.subplot(4, 3, 6)
    query6 = """
    SELECT 
        GEOGRAPHY,
        SUM(QUALIFY_PLUS_AMT) / 1000000 AS CURRENT_YEAR_M,
        SUM(QUALIFY_PLUS_AMT_PY) / 1000000 AS PRIOR_YEAR_M,
        CASE 
            WHEN SUM(QUALIFY_PLUS_AMT_PY) > 0 
            THEN ((SUM(QUALIFY_PLUS_AMT) - SUM(QUALIFY_PLUS_AMT_PY)) / SUM(QUALIFY_PLUS_AMT_PY)) * 100
            ELSE 0 
        END AS YOY_GROWTH
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY GEOGRAPHY
    HAVING SUM(QUALIFY_PLUS_AMT_PY) > 0
    ORDER BY YOY_GROWTH DESC
    LIMIT 10
    """
    df6 = db.execute_query(query6, "Year-over-Year Growth")
    if df6 is not None and not df6.empty:
        x = np.arange(len(df6))
        width = 0.35
        
        bars1 = ax6.bar(x - width/2, df6['PRIOR_YEAR_M'], width, label='Prior Year')
        bars2 = ax6.bar(x + width/2, df6['CURRENT_YEAR_M'], width, label='Current Year')
        
        ax6.set_xlabel('Geography')
        ax6.set_ylabel('Pipeline ($M)')
        ax6.set_title('YoY Pipeline Comparison', fontsize=14, fontweight='bold')
        ax6.set_xticks(x)
        ax6.set_xticklabels(df6['GEOGRAPHY'], rotation=45, ha='right')
        ax6.legend()
        
        # Add growth percentage labels
        for i, (geo, growth) in enumerate(zip(df6['GEOGRAPHY'], df6['YOY_GROWTH'])):
            ax6.text(i, max(df6['CURRENT_YEAR_M'].iloc[i], df6['PRIOR_YEAR_M'].iloc[i]) + 5,
                    f'{growth:.0f}%', ha='center', fontsize=8, fontweight='bold',
                    color='green' if growth > 0 else 'red')
    
    # 7. Pipeline Velocity
    ax7 = plt.subplot(4, 3, 7)
    query7 = """
    SELECT 
        SALES_STAGE,
        AVG(PPV_AMT / NULLIF(OPPORTUNITY_VALUE, 0)) * 100 AS AVG_CONVERSION_PROB,
        COUNT(*) AS DEAL_COUNT
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
        AND OPPORTUNITY_VALUE > 0
    GROUP BY SALES_STAGE
    ORDER BY 
        CASE SALES_STAGE
            WHEN 'Closing' THEN 1
            WHEN 'Negotiate' THEN 2
            WHEN 'Propose' THEN 3
            WHEN 'Qualify' THEN 4
            WHEN 'Design' THEN 5
            WHEN 'Engage' THEN 6
            ELSE 7
        END
    """
    df7 = db.execute_query(query7, "Conversion Probability by Stage")
    if df7 is not None and not df7.empty:
        df7.plot(x='SALES_STAGE', y='AVG_CONVERSION_PROB', kind='line', 
                ax=ax7, marker='o', linewidth=3, markersize=10, color='darkblue')
        ax7.set_title('Average Conversion Probability by Stage', fontsize=14, fontweight='bold')
        ax7.set_xlabel('Sales Stage')
        ax7.set_ylabel('Conversion Probability (%)')
        ax7.grid(True, alpha=0.3)
        plt.setp(ax7.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add value labels
        for idx, row in df7.iterrows():
            ax7.text(idx, row['AVG_CONVERSION_PROB'] + 1, 
                    f"{row['AVG_CONVERSION_PROB']:.0f}%", ha='center')
    
    # 8. Top Clients
    ax8 = plt.subplot(4, 3, 8)
    query8 = """
    SELECT 
        CLIENT_NAME,
        SUM(OPPORTUNITY_VALUE) / 1000000 AS TOTAL_PIPELINE_M,
        COUNT(*) AS OPPORTUNITY_COUNT
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
        AND CLIENT_NAME IS NOT NULL
    GROUP BY CLIENT_NAME
    ORDER BY TOTAL_PIPELINE_M DESC
    LIMIT 15
    """
    df8 = db.execute_query(query8, "Top Clients by Pipeline")
    if df8 is not None and not df8.empty:
        # Horizontal bar chart
        df8_sorted = df8.sort_values('TOTAL_PIPELINE_M')
        y_pos = np.arange(len(df8_sorted))
        ax8.barh(y_pos, df8_sorted['TOTAL_PIPELINE_M'], color='coral')
        ax8.set_yticks(y_pos)
        ax8.set_yticklabels([name[:30] + '...' if len(name) > 30 else name 
                            for name in df8_sorted['CLIENT_NAME']], fontsize=8)
        ax8.set_xlabel('Total Pipeline ($M)')
        ax8.set_title('Top 15 Clients by Pipeline Value', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, v in enumerate(df8_sorted['TOTAL_PIPELINE_M']):
            ax8.text(v + 0.5, i, f'${v:.1f}M', va='center', fontsize=8)
    
    # 9. Pipeline Health Score
    ax9 = plt.subplot(4, 3, 9)
    query9 = """
    WITH pipeline_health AS (
        SELECT 
            MARKET,
            SUM(CASE WHEN SALES_STAGE = 'Closing' THEN OPPORTUNITY_VALUE ELSE 0 END) / 
                NULLIF(SUM(QUALIFY_PLUS_AMT), 0) * 100 AS CLOSING_PCT,
            SUM(PPV_AMT) / NULLIF(SUM(QUALIFY_PLUS_AMT), 0) * 100 AS PPV_RATIO,
            COUNT(DISTINCT CLIENT_NAME) AS CLIENT_DIVERSITY,
            AVG(OPPORTUNITY_VALUE) / 1000000 AS AVG_DEAL_SIZE_M
        FROM PROD_MQT_CONSULTING_PIPELINE
        WHERE SALES_STAGE NOT IN ('Won', 'Lost')
        GROUP BY MARKET
        HAVING SUM(QUALIFY_PLUS_AMT) > 0
    )
    SELECT 
        MARKET,
        (CLOSING_PCT * 0.4 + PPV_RATIO * 0.3 + 
         CASE WHEN CLIENT_DIVERSITY > 20 THEN 20 ELSE CLIENT_DIVERSITY END +
         CASE WHEN AVG_DEAL_SIZE_M > 1 THEN 10 ELSE AVG_DEAL_SIZE_M * 10 END) AS HEALTH_SCORE
    FROM pipeline_health
    ORDER BY HEALTH_SCORE DESC
    LIMIT 10
    """
    df9 = db.execute_query(query9, "Pipeline Health Scores")
    if df9 is not None and not df9.empty:
        # Radar chart would be ideal, but using bar chart for simplicity
        colors = ['darkgreen' if score > 70 else 'orange' if score > 50 else 'red' 
                 for score in df9['HEALTH_SCORE']]
        df9.plot(x='MARKET', y='HEALTH_SCORE', kind='bar', ax=ax9, color=colors, legend=False)
        ax9.set_title('Pipeline Health Score by Market', fontsize=14, fontweight='bold')
        ax9.set_xlabel('Market')
        ax9.set_ylabel('Health Score (0-100)')
        ax9.axhline(y=70, color='green', linestyle='--', alpha=0.5, label='Good')
        ax9.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Fair')
        plt.setp(ax9.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax9.legend()
    
    # 10. Weekly Trend
    ax10 = plt.subplot(4, 3, 10)
    query10 = """
    SELECT 
        WEEK,
        SUM(QUALIFY_PLUS_AMT) / 1000000 AS PIPELINE_M,
        SUM(CALL_AMT) / 1000000 AS COMMITTED_M,
        SUM(PPV_AMT) / 1000000 AS FORECAST_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE QUARTER = (SELECT MAX(QUARTER) FROM PROD_MQT_CONSULTING_PIPELINE)
        AND YEAR = (SELECT MAX(YEAR) FROM PROD_MQT_CONSULTING_PIPELINE)
    GROUP BY WEEK
    ORDER BY WEEK
    """
    df10 = db.execute_query(query10, "Weekly Pipeline Trend")
    if df10 is not None and not df10.empty:
        df10.plot(x='WEEK', y=['PIPELINE_M', 'COMMITTED_M', 'FORECAST_M'], 
                 ax=ax10, marker='o', linewidth=2)
        ax10.set_title('Weekly Pipeline Trend', fontsize=14, fontweight='bold')
        ax10.set_xlabel('Week')
        ax10.set_ylabel('Amount ($M)')
        ax10.legend(['Qualified Pipeline', 'Committed', 'Forecast'])
        ax10.grid(True, alpha=0.3)
    
    # 11. GenAI Pipeline Analysis
    ax11 = plt.subplot(4, 3, 11)
    query11 = """
    SELECT 
        CASE 
            WHEN IBM_GEN_AI_IND = 1 THEN 'IBM GenAI'
            WHEN PARTNER_GEN_AI_IND = 1 THEN 'Partner GenAI'
            ELSE 'Traditional'
        END AS AI_TYPE,
        COUNT(*) AS DEAL_COUNT,
        SUM(OPPORTUNITY_VALUE) / 1000000 AS PIPELINE_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY AI_TYPE
    """
    df11 = db.execute_query(query11, "GenAI vs Traditional Pipeline")
    if df11 is not None and not df11.empty:
        # Donut chart
        wedges, texts, autotexts = ax11.pie(df11['PIPELINE_M'], labels=df11['AI_TYPE'], 
                                            autopct='%1.1f%%', startangle=90,
                                            wedgeprops=dict(width=0.5))
        ax11.set_title('Pipeline Distribution: GenAI vs Traditional', fontsize=14, fontweight='bold')
        
        # Add center text
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax11.add_patch(centre_circle)
        ax11.text(0, 0, f"Total\n${df11['PIPELINE_M'].sum():.0f}M", 
                 ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 12. Action Required Summary
    ax12 = plt.subplot(4, 3, 12)
    query12 = """
    WITH risk_summary AS (
        SELECT 
            'At Risk Deals' AS CATEGORY,
            COUNT(*) AS COUNT,
            SUM(OPPORTUNITY_VALUE) / 1000000 AS VALUE_M
        FROM PROD_MQT_CONSULTING_PIPELINE
        WHERE SALES_STAGE NOT IN ('Won', 'Lost')
            AND PPV_AMT < OPPORTUNITY_VALUE * 0.5
        
        UNION ALL
        
        SELECT 
            'Stalled Deals' AS CATEGORY,
            COUNT(*) AS COUNT,
            SUM(OPPORTUNITY_VALUE) / 1000000 AS VALUE_M
        FROM PROD_MQT_CONSULTING_PIPELINE
        WHERE SALES_STAGE IN ('Qualify', 'Design')
            AND OPPORTUNITY_VALUE > 1000000
        
        UNION ALL
        
        SELECT 
            'Need Follow-up' AS CATEGORY,
            COUNT(*) AS COUNT,
            SUM(OPPORTUNITY_VALUE) / 1000000 AS VALUE_M
        FROM PROD_MQT_CONSULTING_PIPELINE
        WHERE SALES_STAGE = 'Negotiate'
            AND CALL_AMT = 0
    )
    SELECT * FROM risk_summary
    """
    df12 = db.execute_query(query12, "Action Required Summary")
    if df12 is not None and not df12.empty:
        # Dual bar chart
        x = np.arange(len(df12))
        width = 0.35
        
        ax12_twin = ax12.twinx()
        bars1 = ax12.bar(x - width/2, df12['COUNT'], width, label='Count', color='lightblue')
        bars2 = ax12_twin.bar(x + width/2, df12['VALUE_M'], width, label='Value ($M)', color='lightcoral')
        
        ax12.set_xlabel('Category')
        ax12.set_ylabel('Deal Count', color='lightblue')
        ax12_twin.set_ylabel('Value ($M)', color='lightcoral')
        ax12.set_title('Action Required Summary', fontsize=14, fontweight='bold')
        ax12.set_xticks(x)
        ax12.set_xticklabels(df12['CATEGORY'], rotation=45, ha='right')
        ax12.tick_params(axis='y', labelcolor='lightblue')
        ax12_twin.tick_params(axis='y', labelcolor='lightcoral')
        
        # Add value labels
        for bar1, bar2, count, value in zip(bars1, bars2, df12['COUNT'], df12['VALUE_M']):
            ax12.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 0.5,
                     f'{count}', ha='center', va='bottom', fontsize=8)
            ax12_twin.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 0.5,
                          f'${value:.0f}M', ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('IBM Sales Pipeline Analytics Dashboard', fontsize=20, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Save the figure
    plt.savefig('sales_pipeline_dashboard.png', dpi=300, bbox_inches='tight')
    print("\n✅ Dashboard saved as 'sales_pipeline_dashboard.png'")
    
    # Show the plot
    plt.show()

def generate_summary_report(db):
    """Generate a text summary report of key metrics"""
    
    print("\n" + "="*60)
    print("📊 EXECUTIVE SUMMARY REPORT")
    print("="*60)
    
    # Total Pipeline
    query = """
    SELECT 
        SUM(OPPORTUNITY_VALUE) / 1000000 AS TOTAL_PIPELINE_M,
        SUM(QUALIFY_PLUS_AMT) / 1000000 AS QUALIFIED_PIPELINE_M,
        SUM(PPV_AMT) / 1000000 AS FORECAST_M,
        COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS,
        COUNT(*) AS TOTAL_OPPORTUNITIES
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    """
    df = db.execute_query(query)
    if df is not None and not df.empty:
        print(f"\n🎯 PIPELINE OVERVIEW:")
        print(f"   Total Pipeline: ${df['TOTAL_PIPELINE_M'].iloc[0]:,.0f}M")
        print(f"   Qualified Pipeline: ${df['QUALIFIED_PIPELINE_M'].iloc[0]:,.0f}M")
        print(f"   Forecast (PPV): ${df['FORECAST_M'].iloc[0]:,.0f}M")
        print(f"   Unique Clients: {df['UNIQUE_CLIENTS'].iloc[0]:,}")
        print(f"   Total Opportunities: {df['TOTAL_OPPORTUNITIES'].iloc[0]:,}")
    
    # Win Rate
    query = """
    SELECT 
        CAST(SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) AS FLOAT) * 100 / 
        NULLIF(SUM(CASE WHEN SALES_STAGE IN ('Won', 'Lost') THEN 1 ELSE 0 END), 0) AS WIN_RATE,
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE END) / 1000000 AS WON_VALUE_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    """
    df = db.execute_query(query)
    if df is not None and not df.empty:
        print(f"\n🏆 WIN RATE ANALYSIS:")
        print(f"   Overall Win Rate: {df['WIN_RATE'].iloc[0]:.1f}%")
        print(f"   Total Won Value: ${df['WON_VALUE_M'].iloc[0]:,.0f}M")
    
    # Top Markets
    query = """
    SELECT 
        MARKET,
        SUM(OPPORTUNITY_VALUE) / 1000000 AS PIPELINE_M
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY MARKET
    ORDER BY PIPELINE_M DESC
    LIMIT 5
    """
    df = db.execute_query(query)
    if df is not None and not df.empty:
        print(f"\n🌍 TOP 5 MARKETS BY PIPELINE:")
        for idx, row in df.iterrows():
            print(f"   {idx+1}. {row['MARKET']}: ${row['PIPELINE_M']:,.0f}M")
    
    # Risk Analysis
    query = """
    SELECT 
        COUNT(CASE WHEN PPV_AMT < OPPORTUNITY_VALUE * 0.5 THEN 1 END) AS AT_RISK_COUNT,
        SUM(CASE WHEN PPV_AMT < OPPORTUNITY_VALUE * 0.5 THEN OPPORTUNITY_VALUE END) / 1000000 AS AT_RISK_VALUE_M,
        COUNT(CASE WHEN SALES_STAGE = 'Negotiate' AND CALL_AMT = 0 THEN 1 END) AS UNCOMMITTED_NEGOTIATE
    FROM PROD_MQT_CONSULTING_PIPELINE
    WHERE SALES_STAGE NOT IN ('Won', 'Lost')
    """
    df = db.execute_query(query)
    if df is not None and not df.empty:
        print(f"\n⚠️  RISK ANALYSIS:")
        print(f"   At-Risk Deals: {df['AT_RISK_COUNT'].iloc[0]} deals worth ${df['AT_RISK_VALUE_M'].iloc[0]:,.0f}M")
        print(f"   Uncommitted Negotiate Deals: {df['UNCOMMITTED_NEGOTIATE'].iloc[0]}")
    
    print("\n" + "="*60)

def main():
    """Main execution function"""
    
    print("="*60)
    print("🚀 IBM DB2 SALES PIPELINE ANALYTICS SIMULATOR")
    print("="*60)
    
    # Initialize database
    db = DB2Simulator()
    
    # Load MQT tables
    print("\n📁 Loading MQT tables from Excel/CSV files...")
    
    data_path = "/Volumes/DATA/Python/IBM_analyza/data_exports/20250709_215809/tables/"
    
    # Load main tables
    tables_to_load = [
        ("PROD_MQT_CONSULTING_PIPELINE.csv", "PROD_MQT_CONSULTING_PIPELINE"),
        ("PROD_MQT_CONSULTING_BUDGET.csv", "PROD_MQT_CONSULTING_BUDGET"),
        ("PROD_MQT_CONSULTING_REVENUE_ACTUALS.csv", "PROD_MQT_CONSULTING_REVENUE_ACTUALS"),
        ("PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE.csv", "PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE"),
        ("PROD_MQT_CONSULTING_REVENUE_FORECAST.csv", "PROD_MQT_CONSULTING_REVENUE_FORECAST")
    ]
    
    for file_name, table_name in tables_to_load:
        db.load_excel_to_db(data_path + file_name, table_name)
    
    # Generate visualizations
    create_visualizations(db)
    
    # Generate summary report
    generate_summary_report(db)
    
    # Close database connection
    db.close()
    
    print("\n✅ Analysis complete! Check 'sales_pipeline_dashboard.png' for visualizations.")

if __name__ == "__main__":
    main()