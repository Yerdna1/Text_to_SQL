import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_er_diagram():
    """Create an Entity-Relationship style diagram for the star schema"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define colors
    fact_color = '#E8F4FF'
    fact_border = '#1E88E5'
    dim_color = '#FFF3E0'
    dim_border = '#FF8C00'
    
    # Fact Tables
    pipeline_fact = {
        'name': 'PROD_MQT_CONSULTING_PIPELINE',
        'x': 8, 'y': 8, 'width': 6, 'height': 4,
        'measures': [
            'OPPORTUNITY_VALUE', 'CALL_AMT', 'WON_AMT',
            'UPSIDE_AMT', 'QUALIFY_PLUS_AMT', 'PPV_AMT',
            '+ _PY and _PPY variants'
        ]
    }
    
    budget_fact = {
        'name': 'PROD_MQT_CONSULTING_BUDGET',
        'x': 1, 'y': 4, 'width': 5, 'height': 2.5,
        'measures': [
            'REVENUE_BUDGET_AMT',
            'SIGNINGS_BUDGET_AMT',
            'GROSS_PROFIT_BUDGET_AMT'
        ]
    }
    
    actuals_fact = {
        'name': 'PROD_MQT_CONSULTING_REVENUE_ACTUALS',
        'x': 15, 'y': 4, 'width': 5, 'height': 2.5,
        'measures': [
            'REVENUE_AMT',
            'GROSS_PROFIT_AMT',
            'REVENUE_AMT_PY',
            'GROSS_PROFIT_AMT_PY'
        ]
    }
    
    # Dimensions
    dimensions = [
        {
            'name': 'TIME DIMENSION',
            'x': 8, 'y': 14, 'width': 3.5, 'height': 2,
            'attrs': ['YEAR', 'QUARTER', 'MONTH', 'WEEK', 'REL_QTR_MNEUMONIC']
        },
        {
            'name': 'GEOGRAPHIC DIMENSION',
            'x': 1, 'y': 10, 'width': 3.5, 'height': 1.5,
            'attrs': ['GEOGRAPHY', 'MARKET', 'SECTOR']
        },
        {
            'name': 'PRODUCT DIMENSION',
            'x': 15, 'y': 10, 'width': 3.5, 'height': 1.5,
            'attrs': ['UT15_NAME', 'UT17_NAME', 'UT20_NAME', 'UT30_NAME']
        },
        {
            'name': 'CUSTOMER DIMENSION',
            'x': 8, 'y': 1, 'width': 3.5, 'height': 1.5,
            'attrs': ['CLIENT_NAME', 'INDUSTRY']
        },
        {
            'name': 'SALES DIMENSION',
            'x': 1, 'y': 1, 'width': 3.5, 'height': 1.5,
            'attrs': ['SALES_STAGE', 'DEAL_SIZE']
        },
        {
            'name': 'SNAPSHOT DIMENSION',
            'x': 15, 'y': 1, 'width': 3.5, 'height': 1,
            'attrs': ['SNAPSHOT_LEVEL']
        }
    ]
    
    # Draw fact tables
    for fact in [pipeline_fact, budget_fact, actuals_fact]:
        # Main box
        box = FancyBboxPatch(
            (fact['x'], fact['y']), fact['width'], fact['height'],
            boxstyle="round,pad=0.1",
            facecolor=fact_color,
            edgecolor=fact_border,
            linewidth=2
        )
        ax.add_patch(box)
        
        # Title
        ax.text(fact['x'] + fact['width']/2, fact['y'] + fact['height'] - 0.3,
                fact['name'], ha='center', va='center',
                fontsize=10, fontweight='bold')
        
        # Measures
        y_offset = 0.5
        for measure in fact['measures']:
            ax.text(fact['x'] + 0.2, fact['y'] + fact['height'] - 0.8 - y_offset,
                    f"• {measure}", ha='left', va='center',
                    fontsize=8)
            y_offset += 0.3
    
    # Draw dimensions
    for dim in dimensions:
        # Main box
        box = FancyBboxPatch(
            (dim['x'], dim['y']), dim['width'], dim['height'],
            boxstyle="round,pad=0.1",
            facecolor=dim_color,
            edgecolor=dim_border,
            linewidth=2
        )
        ax.add_patch(box)
        
        # Title
        ax.text(dim['x'] + dim['width']/2, dim['y'] + dim['height'] - 0.2,
                dim['name'], ha='center', va='center',
                fontsize=9, fontweight='bold')
        
        # Attributes
        y_offset = 0.3
        for attr in dim['attrs']:
            if dim['y'] + dim['height'] - 0.5 - y_offset > dim['y']:
                ax.text(dim['x'] + 0.1, dim['y'] + dim['height'] - 0.5 - y_offset,
                        f"• {attr}", ha='left', va='center',
                        fontsize=7)
                y_offset += 0.2
    
    # Draw connections
    # Connect all dimensions to pipeline fact
    for dim in dimensions:
        start_x = dim['x'] + dim['width']/2
        start_y = dim['y'] + dim['height']/2
        end_x = pipeline_fact['x'] + pipeline_fact['width']/2
        end_y = pipeline_fact['y'] + pipeline_fact['height']/2
        
        # Calculate connection points on box edges
        if abs(start_x - end_x) > abs(start_y - end_y):
            # Connect horizontally
            if start_x < end_x:
                start_x = dim['x'] + dim['width']
                end_x = pipeline_fact['x']
            else:
                start_x = dim['x']
                end_x = pipeline_fact['x'] + pipeline_fact['width']
        else:
            # Connect vertically
            if start_y < end_y:
                start_y = dim['y'] + dim['height']
                end_y = pipeline_fact['y']
            else:
                start_y = dim['y']
                end_y = pipeline_fact['y'] + pipeline_fact['height']
        
        ax.plot([start_x, end_x], [start_y, end_y], 'gray', linewidth=1, linestyle='--', alpha=0.5)
    
    # Connect relevant dimensions to budget and actuals
    for dim in dimensions[:4]:  # Only first 4 dimensions connect to all facts
        # To budget
        ax.plot([dim['x'] + dim['width']/2, budget_fact['x'] + budget_fact['width']/2],
                [dim['y'] + dim['height']/2, budget_fact['y'] + budget_fact['height']/2],
                'gray', linewidth=1, linestyle='--', alpha=0.3)
        
        # To actuals
        ax.plot([dim['x'] + dim['width']/2, actuals_fact['x'] + actuals_fact['width']/2],
                [dim['y'] + dim['height']/2, actuals_fact['y'] + actuals_fact['height']/2],
                'gray', linewidth=1, linestyle='--', alpha=0.3)
    
    # Connect fact tables to each other
    ax.plot([pipeline_fact['x'], budget_fact['x'] + budget_fact['width']],
            [pipeline_fact['y'], budget_fact['y'] + budget_fact['height']/2],
            'black', linewidth=2, alpha=0.7)
    
    ax.plot([pipeline_fact['x'] + pipeline_fact['width'], actuals_fact['x']],
            [pipeline_fact['y'], actuals_fact['y'] + actuals_fact['height']/2],
            'black', linewidth=2, alpha=0.7)
    
    # Add title and legend
    ax.text(10, 17, 'IBM Consulting Analytics - Entity Relationship Diagram',
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Legend
    legend_x = 1
    legend_y = 15
    
    # Fact table legend
    fact_legend = FancyBboxPatch(
        (legend_x, legend_y), 1, 0.5,
        boxstyle="round,pad=0.05",
        facecolor=fact_color,
        edgecolor=fact_border,
        linewidth=2
    )
    ax.add_patch(fact_legend)
    ax.text(legend_x + 1.2, legend_y + 0.25, 'Fact Table', ha='left', va='center', fontsize=9)
    
    # Dimension legend
    dim_legend = FancyBboxPatch(
        (legend_x, legend_y - 0.7), 1, 0.5,
        boxstyle="round,pad=0.05",
        facecolor=dim_color,
        edgecolor=dim_border,
        linewidth=2
    )
    ax.add_patch(dim_legend)
    ax.text(legend_x + 1.2, legend_y - 0.45, 'Dimension', ha='left', va='center', fontsize=9)
    
    # Set axis properties
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 18)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def create_measure_hierarchy_diagram():
    """Create a diagram showing the hierarchy of pipeline measures"""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Define the hierarchy
    measures = {
        'OPPORTUNITY_VALUE': {
            'x': 6, 'y': 7, 'width': 3, 'height': 0.8,
            'color': '#E3F2FD', 'desc': 'Total Opportunity Amount'
        },
        'OPEN_PIPELINE_AMT': {
            'x': 6, 'y': 5.5, 'width': 3, 'height': 0.8,
            'color': '#C5E1A5', 'desc': 'All Open Opportunities'
        },
        'QUALIFY_PLUS_AMT': {
            'x': 2, 'y': 4, 'width': 3, 'height': 0.8,
            'color': '#BBDEFB', 'desc': 'Qualify + Later Stages'
        },
        'PROPOSE_PLUS_AMT': {
            'x': 6, 'y': 4, 'width': 3, 'height': 0.8,
            'color': '#B2DFDB', 'desc': 'Propose + Later Stages'
        },
        'NEGOTIATE_PLUS_AMT': {
            'x': 10, 'y': 4, 'width': 3, 'height': 0.8,
            'color': '#FFCCBC', 'desc': 'Negotiate + Closing'
        },
        'CALL_AMT': {
            'x': 2, 'y': 2.5, 'width': 3, 'height': 0.8,
            'color': '#D1C4E9', 'desc': 'FLM Committed'
        },
        'UPSIDE_AMT': {
            'x': 6, 'y': 2.5, 'width': 3, 'height': 0.8,
            'color': '#F8BBD0', 'desc': 'Upside Opportunities'
        },
        'PPV_AMT': {
            'x': 10, 'y': 2.5, 'width': 3, 'height': 0.8,
            'color': '#FFE0B2', 'desc': 'PERFORM Pipeline Value'
        },
        'WON_AMT': {
            'x': 6, 'y': 1, 'width': 3, 'height': 0.8,
            'color': '#C8E6C9', 'desc': 'Closed Won'
        }
    }
    
    # Draw boxes
    for name, props in measures.items():
        box = FancyBboxPatch(
            (props['x'], props['y']), props['width'], props['height'],
            boxstyle="round,pad=0.05",
            facecolor=props['color'],
            edgecolor='black',
            linewidth=1
        )
        ax.add_patch(box)
        
        ax.text(props['x'] + props['width']/2, props['y'] + props['height']/2,
                name, ha='center', va='center',
                fontsize=10, fontweight='bold')
        
        ax.text(props['x'] + props['width']/2, props['y'] - 0.15,
                props['desc'], ha='center', va='center',
                fontsize=8, style='italic')
    
    # Draw relationships
    # OPPORTUNITY_VALUE includes everything
    ax.arrow(6.5, 6.7, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # OPEN_PIPELINE branches to stage-based measures
    ax.arrow(5, 5.3, -1.5, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.arrow(7.5, 5.3, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.arrow(10, 5.3, 1.5, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Stage relationships
    ax.arrow(5, 3.8, 0.5, -0.5, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    ax.arrow(9, 3.8, -0.5, -0.5, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    ax.arrow(11.5, 3.8, 0, -0.5, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # Add annotations
    ax.text(2, 8, 'Pipeline Measures Hierarchy', fontsize=14, fontweight='bold')
    ax.text(2, 7.5, 'Shows how measures relate and aggregate', fontsize=10, style='italic')
    
    # Add stage flow indicators
    stages_y = 0.2
    stages = ['Qualify', 'Design', 'Propose', 'Negotiate', 'Closing']
    for i, stage in enumerate(stages):
        ax.text(2 + i*2.5, stages_y, stage, ha='center', va='center',
                fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow'))
    
    # Set axis properties
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create ER diagram
    er_fig = create_er_diagram()
    er_fig.savefig('er_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create measure hierarchy diagram
    hierarchy_fig = create_measure_hierarchy_diagram()
    hierarchy_fig.savefig('measure_hierarchy.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Diagrams created successfully!")
    print("- er_diagram.png: Entity-Relationship style diagram")
    print("- measure_hierarchy.png: Pipeline measures hierarchy")