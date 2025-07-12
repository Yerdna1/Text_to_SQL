import streamlit as st
import plotly.graph_objects as go
from star_schema_diagram import create_star_schema_diagram, create_detailed_relationship_diagram
import matplotlib.pyplot as plt
from er_diagram import create_er_diagram, create_measure_hierarchy_diagram

st.set_page_config(page_title="IBM Analytics Star Schema Diagrams", layout="wide")

st.title("IBM Consulting Analytics - Data Model Diagrams")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Star Schema", "Pipeline Flow", "ER Diagram", "Measure Hierarchy"])

with tab1:
    st.header("Interactive Star Schema Diagram")
    st.write("Hover over elements to see details about fact tables and dimensions.")
    
    fig1 = create_star_schema_diagram()
    st.plotly_chart(fig1, use_container_width=True)
    
    with st.expander("Understanding the Star Schema"):
        st.markdown("""
        **Fact Tables (Center):**
        - **PIPELINE**: Contains all opportunity and pipeline metrics
        - **BUDGET**: Contains revenue and signings targets
        - **ACTUALS**: Contains actual revenue and gross profit
        
        **Dimensions (Surrounding):**
        - **TIME**: Year, Quarter, Month, Week temporal attributes
        - **GEOGRAPHIC**: Geography, Market, Sector organizational hierarchy
        - **PRODUCT**: UT15-UT30 product taxonomy hierarchy
        - **CUSTOMER**: Client Name and Industry attributes
        - **SALES**: Sales Stage and Deal Size attributes
        - **SNAPSHOT**: Weekly/Monthly/Quarterly snapshot levels
        
        **Relationships:**
        - All dimensions connect to all fact tables (star pattern)
        - Fact tables can be joined on common dimensions
        """)

with tab2:
    st.header("Pipeline Stage Flow & Measure Groupings")
    st.write("Shows how opportunities flow through stages and how measures aggregate.")
    
    fig2 = create_detailed_relationship_diagram()
    st.plotly_chart(fig2, use_container_width=True)
    
    with st.expander("Understanding Pipeline Measures"):
        st.markdown("""
        **Stage Progression:**
        - Opportunities move from Open Pipeline → Qualify → Design → Propose → Negotiate → Closing → Won/Lost
        
        **Measure Groupings:**
        - **QUALIFY_PLUS_AMT**: Includes Qualify, Design, Propose, Negotiate, and Closing stages
        - **PROPOSE_PLUS_AMT**: Includes Propose, Negotiate, and Closing stages
        - **NEGOTIATE_PLUS_AMT**: Includes Negotiate and Closing stages
        
        **Other Key Measures:**
        - **CALL_AMT**: FLM (First Line Manager) committed pipeline
        - **PPV_AMT**: PERFORM Pipeline Value (quarter-end assessment)
        - **WON_AMT**: Successfully closed opportunities
        """)

with tab3:
    st.header("Entity-Relationship Diagram")
    st.write("Traditional ER-style view of the data model showing all tables and relationships.")
    
    # Create and display the ER diagram
    er_fig = create_er_diagram()
    st.pyplot(er_fig)
    
    with st.expander("Reading the ER Diagram"):
        st.markdown("""
        **Color Coding:**
        - Blue boxes: Fact tables (contain measures/metrics)
        - Orange boxes: Dimension tables (contain descriptive attributes)
        - Solid lines: Strong relationships between fact tables
        - Dashed lines: Dimensional relationships
        
        **Key Points:**
        - All fact tables share the same dimensional structure
        - This enables easy cross-fact analysis and reporting
        - The MQT (Materialized Query Table) design pre-aggregates data for performance
        """)

with tab4:
    st.header("Pipeline Measures Hierarchy")
    st.write("Shows how different pipeline measures relate to each other.")
    
    # Create and display the hierarchy diagram
    hierarchy_fig = create_measure_hierarchy_diagram()
    st.pyplot(hierarchy_fig)
    
    with st.expander("Understanding Measure Relationships"):
        st.markdown("""
        **Hierarchy Levels:**
        1. **OPPORTUNITY_VALUE**: Total value of all opportunities
        2. **OPEN_PIPELINE_AMT**: All non-closed opportunities
        3. **Stage-based Measures**: Different aggregations based on sales stages
        4. **Specialized Measures**: CALL_AMT (committed), UPSIDE_AMT (upside), PPV_AMT (quarter-end)
        5. **WON_AMT**: Successfully closed deals
        
        **Key Relationships:**
        - Each lower level is a subset of the level above
        - QUALIFY_PLUS includes more stages than PROPOSE_PLUS
        - PROPOSE_PLUS includes more stages than NEGOTIATE_PLUS
        - All measures roll up to OPPORTUNITY_VALUE
        """)

# Add sidebar with additional information
st.sidebar.header("About the Data Model")
st.sidebar.markdown("""
### Key Features:
- **Star Schema Design**: Optimized for analytical queries
- **Pre-aggregated MQTs**: Fast query performance
- **Historical Tracking**: Built-in PY/PPY comparisons
- **Snapshot Architecture**: Weekly point-in-time views

### Common Use Cases:
1. **Pipeline Coverage**: Compare pipeline to budget targets
2. **Win Rate Analysis**: Track conversion through stages
3. **YoY Comparisons**: Built-in prior year metrics
4. **Territory Performance**: Analyze by geography/market
5. **Product Performance**: Drill down through UT hierarchy

### Performance Tips:
- Always filter on SNAPSHOT_LEVEL first
- Use RELATIVE_QUARTER_MNEUMONIC for time filters
- Leverage pre-calculated measures
- Join on all relevant dimensions
""")

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Use the tabs above to explore different views of the data model")