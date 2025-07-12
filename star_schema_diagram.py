import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def create_star_schema_diagram():
    """Create an interactive star schema diagram for IBM Consulting tables"""
    
    # Create figure
    fig = go.Figure()
    
    # Define positions for fact tables (center)
    fact_tables = {
        'PIPELINE': {'x': 0, 'y': 0, 'color': '#1f77b4'},
        'BUDGET': {'x': -3, 'y': -3, 'color': '#ff7f0e'},
        'ACTUALS': {'x': 3, 'y': -3, 'color': '#2ca02c'}
    }
    
    # Define positions for dimensions (surrounding)
    dimensions = {
        'TIME': {'x': 0, 'y': 4, 'color': '#d62728'},
        'GEOGRAPHIC': {'x': 4, 'y': 2, 'color': '#9467bd'},
        'PRODUCT': {'x': 4, 'y': -2, 'color': '#8c564b'},
        'CUSTOMER': {'x': 0, 'y': -6, 'color': '#e377c2'},
        'SALES': {'x': -4, 'y': -2, 'color': '#7f7f7f'},
        'SNAPSHOT': {'x': -4, 'y': 2, 'color': '#bcbd22'}
    }
    
    # Add fact table boxes
    for name, props in fact_tables.items():
        if name == 'PIPELINE':
            full_name = 'PROD_MQT_CONSULTING_PIPELINE'
            measures = [
                'OPPORTUNITY_VALUE',
                'CALL_AMT (FLM Committed)',
                'WON_AMT',
                'UPSIDE_AMT',
                'QUALIFY_PLUS_AMT',
                'PROPOSE_PLUS_AMT',
                'NEGOTIATE_PLUS_AMT',
                'OPEN_PIPELINE_AMT',
                'PPV_AMT',
                '+ All _PY and _PPY variants'
            ]
        elif name == 'BUDGET':
            full_name = 'PROD_MQT_CONSULTING_BUDGET'
            measures = [
                'REVENUE_BUDGET_AMT',
                'SIGNINGS_BUDGET_AMT',
                'GROSS_PROFIT_BUDGET_AMT'
            ]
        else:  # ACTUALS
            full_name = 'PROD_MQT_CONSULTING_REVENUE_ACTUALS'
            measures = [
                'REVENUE_AMT',
                'GROSS_PROFIT_AMT',
                'REVENUE_AMT_PY',
                'GROSS_PROFIT_AMT_PY'
            ]
        
        # Create hover text
        hover_text = f"<b>{full_name}</b><br><br><b>Measures:</b><br>" + "<br>".join(f"• {m}" for m in measures)
        
        # Add fact table box
        fig.add_trace(go.Scatter(
            x=[props['x']],
            y=[props['y']],
            mode='markers+text',
            marker=dict(size=80, color=props['color'], symbol='square'),
            text=[name],
            textposition='middle center',
            textfont=dict(size=12, color='white'),
            hovertext=hover_text,
            hoverinfo='text',
            name=full_name
        ))
    
    # Add dimension boxes
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
            attrs = ['SALES_STAGE', 'DEAL_SIZE', 'IBM_GEN_AI_IND', 'PARTNER_GEN_AI_IND']
        else:  # SNAPSHOT
            attrs = ['SNAPSHOT_LEVEL (W/M/Q)']
        
        hover_text = f"<b>{name} DIMENSION</b><br><br><b>Attributes:</b><br>" + "<br>".join(f"• {a}" for a in attrs)
        
        fig.add_trace(go.Scatter(
            x=[props['x']],
            y=[props['y']],
            mode='markers+text',
            marker=dict(size=60, color=props['color'], symbol='diamond'),
            text=[name],
            textposition='middle center',
            textfont=dict(size=10, color='white'),
            hovertext=hover_text,
            hoverinfo='text',
            name=f'{name} Dimension'
        ))
    
    # Add connections from dimensions to fact tables
    for dim_name, dim_props in dimensions.items():
        for fact_name, fact_props in fact_tables.items():
            # Add line
            fig.add_trace(go.Scatter(
                x=[dim_props['x'], fact_props['x']],
                y=[dim_props['y'], fact_props['y']],
                mode='lines',
                line=dict(color='gray', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='none'
            ))
    
    # Add connections between fact tables
    fig.add_trace(go.Scatter(
        x=[fact_tables['PIPELINE']['x'], fact_tables['BUDGET']['x']],
        y=[fact_tables['PIPELINE']['y'], fact_tables['BUDGET']['y']],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,
        hoverinfo='none'
    ))
    
    fig.add_trace(go.Scatter(
        x=[fact_tables['PIPELINE']['x'], fact_tables['ACTUALS']['x']],
        y=[fact_tables['PIPELINE']['y'], fact_tables['ACTUALS']['y']],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,
        hoverinfo='none'
    ))
    
    fig.add_trace(go.Scatter(
        x=[fact_tables['BUDGET']['x'], fact_tables['ACTUALS']['x']],
        y=[fact_tables['BUDGET']['y'], fact_tables['ACTUALS']['y']],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # Add annotations
    fig.add_annotation(
        x=0, y=5.5,
        text="<b>IBM Consulting Analytics - Star Schema</b>",
        showarrow=False,
        font=dict(size=20)
    )
    
    fig.add_annotation(
        x=0, y=-7.5,
        text="<i>Hover over elements for details</i>",
        showarrow=False,
        font=dict(size=12, color='gray')
    )
    
    # Update layout
    fig.update_layout(
        width=1000,
        height=800,
        showlegend=True,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-8, 6]),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig

def create_detailed_relationship_diagram():
    """Create a detailed diagram showing measure relationships"""
    
    fig = go.Figure()
    
    # Define pipeline stages flow
    stages = [
        {'name': 'Open Pipeline', 'x': 0, 'y': 5, 'color': '#636EFA'},
        {'name': 'Qualify', 'x': 0, 'y': 4, 'color': '#EF553B'},
        {'name': 'Design', 'x': 0, 'y': 3, 'color': '#00CC96'},
        {'name': 'Propose', 'x': 0, 'y': 2, 'color': '#AB63FA'},
        {'name': 'Negotiate', 'x': 0, 'y': 1, 'color': '#FFA15A'},
        {'name': 'Closing', 'x': 0, 'y': 0, 'color': '#19D3F3'},
        {'name': 'Won', 'x': -2, 'y': -1, 'color': '#2CA02C'},
        {'name': 'Lost', 'x': 2, 'y': -1, 'color': '#D62728'}
    ]
    
    # Add stage boxes
    for stage in stages:
        fig.add_trace(go.Scatter(
            x=[stage['x']],
            y=[stage['y']],
            mode='markers+text',
            marker=dict(size=50, color=stage['color']),
            text=[stage['name']],
            textposition='middle right' if stage['x'] == 0 else 'top center',
            textfont=dict(size=12),
            showlegend=False,
            hoverinfo='text',
            hovertext=stage['name']
        ))
    
    # Add flow arrows
    for i in range(len(stages)-3):
        fig.add_annotation(
            x=stages[i]['x'], y=stages[i]['y'],
            ax=stages[i+1]['x'], ay=stages[i+1]['y'],
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="gray"
        )
    
    # Add Won/Lost arrows
    fig.add_annotation(
        x=stages[5]['x'], y=stages[5]['y'],
        ax=stages[6]['x'], ay=stages[6]['y'],
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="green"
    )
    
    fig.add_annotation(
        x=stages[5]['x'], y=stages[5]['y'],
        ax=stages[7]['x'], ay=stages[7]['y'],
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="red"
    )
    
    # Add measure groupings
    fig.add_shape(
        type="rect",
        x0=-0.5, y0=0.5, x1=0.5, y1=4.5,
        line=dict(color="blue", width=2, dash="dash"),
        fillcolor="lightblue",
        opacity=0.2
    )
    
    fig.add_annotation(
        x=1, y=2.5,
        text="QUALIFY_PLUS_AMT",
        showarrow=False,
        font=dict(size=10, color="blue"),
        textangle=-90
    )
    
    fig.add_shape(
        type="rect",
        x0=-0.5, y0=0.5, x1=0.5, y1=2.5,
        line=dict(color="purple", width=2, dash="dash"),
        fillcolor="lavender",
        opacity=0.2
    )
    
    fig.add_annotation(
        x=1.5, y=1.5,
        text="PROPOSE_PLUS_AMT",
        showarrow=False,
        font=dict(size=10, color="purple"),
        textangle=-90
    )
    
    fig.add_shape(
        type="rect",
        x0=-0.5, y0=0.5, x1=0.5, y1=1.5,
        line=dict(color="orange", width=2, dash="dash"),
        fillcolor="peachpuff",
        opacity=0.2
    )
    
    fig.add_annotation(
        x=2, y=1,
        text="NEGOTIATE_PLUS_AMT",
        showarrow=False,
        font=dict(size=10, color="orange"),
        textangle=-90
    )
    
    # Add title
    fig.add_annotation(
        x=0, y=6,
        text="<b>Pipeline Stage Flow & Measure Groupings</b>",
        showarrow=False,
        font=dict(size=16)
    )
    
    # Update layout
    fig.update_layout(
        width=800,
        height=600,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2, 6.5]),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig

if __name__ == "__main__":
    # Create and show the star schema diagram
    star_schema_fig = create_star_schema_diagram()
    star_schema_fig.write_html("star_schema_diagram.html")
    star_schema_fig.show()
    
    # Create and show the detailed relationship diagram
    relationship_fig = create_detailed_relationship_diagram()
    relationship_fig.write_html("pipeline_flow_diagram.html")
    relationship_fig.show()
    
    print("Diagrams created successfully!")
    print("- star_schema_diagram.html: Interactive star schema visualization")
    print("- pipeline_flow_diagram.html: Pipeline stage flow and measure relationships")