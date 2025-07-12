import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_complete_star_schema():
    """Create comprehensive star schema with all consulting tables"""
    
    fig = go.Figure()
    
    # Define all fact tables with their positions and colors
    fact_tables = {
        # Core MQT Tables (Center cluster)
        'PIPELINE_MQT': {
            'name': 'PROD_MQT_CONSULTING_PIPELINE',
            'x': 0, 'y': 0, 'color': '#1f77b4', 'size': 100,
            'measures': ['OPPORTUNITY_VALUE', 'CALL_AMT', 'WON_AMT', 'QUALIFY_PLUS_AMT', 'PPV_AMT', '+PY variants']
        },
        'BUDGET_MQT': {
            'name': 'PROD_MQT_CONSULTING_BUDGET', 
            'x': -3, 'y': -2, 'color': '#ff7f0e', 'size': 80,
            'measures': ['REVENUE_BUDGET_AMT', 'SIGNINGS_BUDGET_AMT', 'GROSS_PROFIT_BUDGET_AMT']
        },
        'REVENUE_ACT_MQT': {
            'name': 'PROD_MQT_CONSULTING_REVENUE_ACTUALS',
            'x': 3, 'y': -2, 'color': '#2ca02c', 'size': 80,
            'measures': ['REVENUE_AMT', 'GROSS_PROFIT_AMT', 'REVENUE_AMT_PY', 'GROSS_PROFIT_AMT_PY']
        },
        
        # Additional MQT Tables (Outer ring)
        'OPPORTUNITY_MQT': {
            'name': 'PROD_MQT_CONSULTING_OPPORTUNITY',
            'x': -4, 'y': 2, 'color': '#d62728', 'size': 70,
            'measures': ['Individual opportunity details', 'Deal progression tracking', 'Customer information']
        },
        'REVENUE_FORECAST_MQT': {
            'name': 'PROD_MQT_CONSULTING_REVENUE_FORECAST',
            'x': 4, 'y': 2, 'color': '#9467bd', 'size': 70,
            'measures': ['Forecasted revenue amounts', 'Projection metrics', 'Forward-looking data']
        },
        'SIGNINGS_ACT_MQT': {
            'name': 'PROD_MQT_CONSULTING_SIGNINGS_ACTUALS',
            'x': -2, 'y': -4, 'color': '#8c564b', 'size': 70,
            'measures': ['Contract signings', 'Bookings data', 'New business metrics']
        },
        'NET_CALL_MQT': {
            'name': 'PROD_MQT_CONSULTING_PIPELINE_NET_CALL',
            'x': 2, 'y': -4, 'color': '#e377c2', 'size': 70,
            'measures': ['Net pipeline amounts', 'Management adjustments', 'Refined commitments']
        },
        'TEMP_MQT': {
            'name': 'PROD_MQT_TEMP_CONSULTING',
            'x': 0, 'y': -6, 'color': '#7f7f7f', 'size': 50,
            'measures': ['Staging data', 'Work-in-progress', 'Validation tables']
        }
    }
    
    # Base tables (smaller, positioned further out)
    base_tables = {
        'PIPELINE_BASE': {
            'name': 'PROD_CONSULTING_PIPELINE',
            'x': -6, 'y': 0, 'color': '#17becf', 'size': 40
        },
        'BUDGET_BASE': {
            'name': 'PROD_CONSULTING_BUDGET',
            'x': -6, 'y': -3, 'color': '#ffbb78', 'size': 40
        },
        'REVENUE_ACT_BASE': {
            'name': 'PROD_CONSULTING_REVENUE_ACTUALS',
            'x': 6, 'y': -3, 'color': '#98df8a', 'size': 40
        },
        'OPPORTUNITY_BASE': {
            'name': 'PROD_CONSULTING_OPPORTUNITY',
            'x': -6, 'y': 3, 'color': '#ff9999', 'size': 40
        },
        'REVENUE_FORECAST_BASE': {
            'name': 'PROD_CONSULTING_REVENUE_FORECAST',
            'x': 6, 'y': 3, 'color': '#c5b0d5', 'size': 40
        },
        'SIGNINGS_ACT_BASE': {
            'name': 'PROD_CONSULTING_SIGNINGS_ACTUALS',
            'x': -3, 'y': -6, 'color': '#c49c94', 'size': 40
        },
        'NET_CALL_BASE': {
            'name': 'PROD_CONSULTING_PIPELINE_NET_CALL',
            'x': 3, 'y': -6, 'color': '#f7b6d3', 'size': 40
        }
    }
    
    # Dimensions (positioned around the edge)
    dimensions = {
        'TIME': {'x': 0, 'y': 7, 'color': '#bcbd22', 'size': 60},
        'GEOGRAPHIC': {'x': 7, 'y': 0, 'color': '#dbdb8d', 'size': 60},
        'PRODUCT': {'x': 0, 'y': -9, 'color': '#9edae5', 'size': 60},
        'CUSTOMER': {'x': -7, 'y': 0, 'color': '#ffad99', 'size': 60},
        'SALES': {'x': -5, 'y': 5, 'color': '#c7c7c7', 'size': 50},
        'SNAPSHOT': {'x': 5, 'y': 5, 'color': '#f7d794', 'size': 50}
    }
    
    # Add MQT fact tables
    for name, props in fact_tables.items():
        hover_text = f"<b>{props['name']}</b><br><br><b>Type:</b> MQT Fact Table<br><br><b>Key Measures:</b><br>" + "<br>".join(f"• {m}" for m in props['measures'])
        
        fig.add_trace(go.Scatter(
            x=[props['x']], y=[props['y']],
            mode='markers+text',
            marker=dict(size=props['size'], color=props['color'], symbol='square', line=dict(width=2, color='white')),
            text=[name.replace('_', '<br>')],
            textposition='middle center',
            textfont=dict(size=8, color='white'),
            hovertext=hover_text,
            hoverinfo='text',
            name=props['name']
        ))
    
    # Add base tables
    for name, props in base_tables.items():
        hover_text = f"<b>{props['name']}</b><br><br><b>Type:</b> Base Table<br><b>Description:</b> Raw transactional data source for corresponding MQT"
        
        fig.add_trace(go.Scatter(
            x=[props['x']], y=[props['y']],
            mode='markers+text',
            marker=dict(size=props['size'], color=props['color'], symbol='circle', line=dict(width=1, color='gray')),
            text=[name.replace('_', '<br>').replace('BASE', '')],
            textposition='middle center',
            textfont=dict(size=6, color='black'),
            hovertext=hover_text,
            hoverinfo='text',
            name=props['name']
        ))
    
    # Add dimensions
    for name, props in dimensions.items():
        if name == 'TIME':
            attrs = ['YEAR', 'QUARTER', 'MONTH', 'WEEK', 'RELATIVE_QUARTER_MNEUMONIC']
        elif name == 'GEOGRAPHIC':
            attrs = ['GEOGRAPHY', 'MARKET', 'SECTOR']
        elif name == 'PRODUCT':
            attrs = ['UT15_NAME', 'UT17_NAME', 'UT20_NAME', 'UT30_NAME']
        elif name == 'CUSTOMER':
            attrs = ['CLIENT_NAME', 'INDUSTRY']
        elif name == 'SALES':
            attrs = ['SALES_STAGE', 'DEAL_SIZE', 'IBM_GEN_AI_IND']
        else:  # SNAPSHOT
            attrs = ['SNAPSHOT_LEVEL (W/M/Q)']
        
        hover_text = f"<b>{name} DIMENSION</b><br><br><b>Attributes:</b><br>" + "<br>".join(f"• {a}" for a in attrs)
        
        fig.add_trace(go.Scatter(
            x=[props['x']], y=[props['y']],
            mode='markers+text',
            marker=dict(size=props['size'], color=props['color'], symbol='diamond'),
            text=[name],
            textposition='middle center',
            textfont=dict(size=9, color='black'),
            hovertext=hover_text,
            hoverinfo='text',
            name=f'{name} Dimension'
        ))
    
    # Add connections from dimensions to main fact tables (only major ones to avoid clutter)
    main_facts = ['PIPELINE_MQT', 'BUDGET_MQT', 'REVENUE_ACT_MQT']
    for dim_name, dim_props in dimensions.items():
        for fact_name in main_facts:
            fact_props = fact_tables[fact_name]
            fig.add_trace(go.Scatter(
                x=[dim_props['x'], fact_props['x']],
                y=[dim_props['y'], fact_props['y']],
                mode='lines',
                line=dict(color='lightgray', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='none'
            ))
    
    # Add connections between MQT and base tables
    mqt_base_pairs = [
        ('PIPELINE_MQT', 'PIPELINE_BASE'),
        ('BUDGET_MQT', 'BUDGET_BASE'),
        ('REVENUE_ACT_MQT', 'REVENUE_ACT_BASE'),
        ('OPPORTUNITY_MQT', 'OPPORTUNITY_BASE'),
        ('REVENUE_FORECAST_MQT', 'REVENUE_FORECAST_BASE'),
        ('SIGNINGS_ACT_MQT', 'SIGNINGS_ACT_BASE'),
        ('NET_CALL_MQT', 'NET_CALL_BASE')
    ]
    
    for mqt_name, base_name in mqt_base_pairs:
        mqt_props = fact_tables[mqt_name]
        base_props = base_tables[base_name]
        fig.add_trace(go.Scatter(
            x=[mqt_props['x'], base_props['x']],
            y=[mqt_props['y'], base_props['y']],
            mode='lines',
            line=dict(color='darkblue', width=2, dash='dash'),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Add fact table interconnections (main relationships)
    fact_connections = [
        ('PIPELINE_MQT', 'BUDGET_MQT'),
        ('PIPELINE_MQT', 'REVENUE_ACT_MQT'),
        ('PIPELINE_MQT', 'OPPORTUNITY_MQT'),
        ('REVENUE_ACT_MQT', 'REVENUE_FORECAST_MQT'),
        ('PIPELINE_MQT', 'NET_CALL_MQT')
    ]
    
    for fact1, fact2 in fact_connections:
        props1 = fact_tables[fact1]
        props2 = fact_tables[fact2]
        fig.add_trace(go.Scatter(
            x=[props1['x'], props2['x']],
            y=[props1['y'], props2['y']],
            mode='lines',
            line=dict(color='black', width=2),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Add annotations
    fig.add_annotation(
        x=0, y=9,
        text="<b>Complete IBM Consulting Analytics - Star Schema</b>",
        showarrow=False,
        font=dict(size=18)
    )
    
    fig.add_annotation(
        x=-8, y=8,
        text="<b>Legend:</b><br>🔷 Dimensions<br>🟦 MQT Fact Tables<br>⚪ Base Tables",
        showarrow=False,
        font=dict(size=10),
        align="left"
    )
    
    fig.add_annotation(
        x=8, y=8,
        text="<b>Connections:</b><br>━━ Fact relationships<br>┅┅ MQT ↔ Base<br>┈┈ Dimensional",
        showarrow=False,
        font=dict(size=10),
        align="left"
    )
    
    # Update layout
    fig.update_layout(
        width=1400,
        height=1000,
        showlegend=True,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-9, 9]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-10, 10]),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.01,
            font=dict(size=8)
        )
    )
    
    return fig

def create_table_hierarchy_diagram():
    """Create a diagram showing MQT vs Base table relationships"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Define table groups
    table_groups = {
        'Pipeline': {
            'mqt': 'PROD_MQT_CONSULTING_PIPELINE',
            'base': 'PROD_CONSULTING_PIPELINE',
            'x': 2, 'y': 8, 'color': '#1f77b4'
        },
        'Budget': {
            'mqt': 'PROD_MQT_CONSULTING_BUDGET',
            'base': 'PROD_CONSULTING_BUDGET', 
            'x': 2, 'y': 6, 'color': '#ff7f0e'
        },
        'Revenue Actuals': {
            'mqt': 'PROD_MQT_CONSULTING_REVENUE_ACTUALS',
            'base': 'PROD_CONSULTING_REVENUE_ACTUALS',
            'x': 2, 'y': 4, 'color': '#2ca02c'
        },
        'Opportunity': {
            'mqt': 'PROD_MQT_CONSULTING_OPPORTUNITY',
            'base': 'PROD_CONSULTING_OPPORTUNITY',
            'x': 2, 'y': 2, 'color': '#d62728'
        },
        'Revenue Forecast': {
            'mqt': 'PROD_MQT_CONSULTING_REVENUE_FORECAST',
            'base': 'PROD_CONSULTING_REVENUE_FORECAST',
            'x': 2, 'y': 0, 'color': '#9467bd'
        },
        'Signings Actuals': {
            'mqt': 'PROD_MQT_CONSULTING_SIGNINGS_ACTUALS',
            'base': 'PROD_CONSULTING_SIGNINGS_ACTUALS',
            'x': 2, 'y': -2, 'color': '#8c564b'
        },
        'Net Call Pipeline': {
            'mqt': 'PROD_MQT_CONSULTING_PIPELINE_NET_CALL',
            'base': 'PROD_CONSULTING_PIPELINE_NET_CALL',
            'x': 2, 'y': -4, 'color': '#e377c2'
        }
    }
    
    # Add section headers
    ax.text(1, 9.5, 'BASE TABLES\n(Raw Data)', ha='center', va='center',
            fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray'))
    
    ax.text(8, 9.5, 'MQT TABLES\n(Optimized Views)', ha='center', va='center',
            fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue'))
    
    ax.text(14, 9.5, 'CHARACTERISTICS', ha='center', va='center',
            fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow'))
    
    # Draw table pairs
    for name, props in table_groups.items():
        y = props['y']
        
        # Base table
        base_box = FancyBboxPatch(
            (0, y-0.3), 5, 0.6,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=props['color'],
            linewidth=2
        )
        ax.add_patch(base_box)
        ax.text(2.5, y, props['base'], ha='center', va='center', fontsize=9)
        
        # MQT table
        mqt_box = FancyBboxPatch(
            (6, y-0.3), 5, 0.6,
            boxstyle="round,pad=0.1",
            facecolor=props['color'],
            edgecolor=props['color'],
            linewidth=2,
            alpha=0.3
        )
        ax.add_patch(mqt_box)
        ax.text(8.5, y, props['mqt'], ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Arrow from base to MQT
        ax.arrow(5.1, y, 0.8, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
        
        # Characteristics
        if name == 'Pipeline':
            chars = "• Pre-aggregated measures\n• Weekly snapshots\n• Historical comparisons (_PY)"
        elif name == 'Budget':
            chars = "• Target aggregations\n• Multi-dimensional rollups\n• Planning hierarchies"
        elif name == 'Revenue Actuals':
            chars = "• Financial aggregations\n• Period summaries\n• Margin calculations"
        elif name == 'Opportunity':
            chars = "• Deal-level summaries\n• Stage aggregations\n• Customer rollups"
        elif name == 'Revenue Forecast':
            chars = "• Predictive aggregations\n• Forecast summaries\n• Trend calculations"
        elif name == 'Signings Actuals':
            chars = "• Booking aggregations\n• Contract summaries\n• New business metrics"
        else:  # Net Call Pipeline
            chars = "• Adjusted pipeline\n• Management overlays\n• Refined commitments"
        
        ax.text(12, y, chars, ha='left', va='center', fontsize=8)
    
    # Add process flow
    ax.text(2.5, -6, 'ETL PROCESS FLOW', ha='center', va='center',
            fontsize=12, fontweight='bold')
    
    flow_steps = [
        'Raw Data\nCapture',
        'Data\nValidation',
        'Business Logic\nApplication',
        'Aggregation\n& Rollup',
        'MQT\nRefresh'
    ]
    
    for i, step in enumerate(flow_steps):
        x = i * 2.5
        box = FancyBboxPatch(
            (x, -7.5), 2, 1,
            boxstyle="round,pad=0.1",
            facecolor='lightgreen',
            edgecolor='darkgreen',
            linewidth=1
        )
        ax.add_patch(box)
        ax.text(x + 1, -7, step, ha='center', va='center', fontsize=8)
        
        if i < len(flow_steps) - 1:
            ax.arrow(x + 2.1, -7, 0.3, 0, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Set axis properties
    ax.set_xlim(-1, 16)
    ax.set_ylim(-9, 11)
    ax.axis('off')
    
    plt.title('IBM Consulting Tables: MQT vs Base Architecture', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    return fig

if __name__ == "__main__":
    # Create complete star schema
    complete_fig = create_complete_star_schema()
    complete_fig.write_html("complete_star_schema.html")
    complete_fig.show()
    
    # Create table hierarchy diagram
    hierarchy_fig = create_table_hierarchy_diagram()
    hierarchy_fig.savefig('table_hierarchy.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Complete diagrams created successfully!")
    print("- complete_star_schema.html: All consulting tables star schema")
    print("- table_hierarchy.png: MQT vs Base table relationships")