#!/usr/bin/env python3
"""
Visualization Utilities for IBM Sales Pipeline Analytics
Handles data visualization and tooltips
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import List
from data_dictionary import DataDictionary


def create_hover_tooltip(column: str, data_dict: DataDictionary) -> str:
    """Create hover tooltip for column explanations"""
    info = data_dict.get_column_info(column)
    
    # If we have dictionary info, use it
    if info and info.get('description') and info.get('description') != 'N/A':
        tooltip = f"""
**{column}**

📊 **Category:** {info.get('category', 'N/A')}

📝 **Description:** {info.get('description', 'No description available')}

🇸🇰 **Slovak:** {info.get('slovak_description', 'N/A')}

🔢 **Calculation:** {info.get('calculation', 'N/A')}

💼 **Business Use:** {info.get('business_use', 'N/A')}

📈 **Data Type:** {info.get('data_type', 'N/A')}

💡 **Examples:** {info.get('example_values', 'N/A')}
"""
        return tooltip
    
    # Generate intelligent explanation for computed/derived columns
    column_lower = column.lower()
    column_clean = column.replace('_', ' ').title()
    
    # Smart explanations based on column patterns
    if 'number_of_countries' in column_lower or 'country_count' in column_lower:
        description = "Count of distinct countries present in the dataset"
        category = "Geographic Metrics"
        business_use = "Used to understand geographic distribution and market reach"
        
    elif 'win_rate' in column_lower:
        description = "Percentage of opportunities that resulted in won deals"
        category = "Sales Performance"
        business_use = "Key metric for measuring sales effectiveness and team performance"
        
    elif 'total_revenue' in column_lower or 'revenue_total' in column_lower:
        description = "Sum of all revenue amounts"
        category = "Financial Metrics"
        business_use = "Primary indicator of business performance and growth"
        
    elif 'forecast' in column_lower and ('revenue' in column_lower or 'amt' in column_lower):
        description = "AI-based predicted revenue using PPV_AMT calculations"
        category = "Forecasting"
        business_use = "Strategic planning and pipeline management"
        
    elif 'pipeline' in column_lower and 'value' in column_lower:
        description = "Total value of active opportunities in the sales pipeline"
        category = "Pipeline Metrics"
        business_use = "Monitor potential future revenue and sales capacity"
        
    elif 'deal_count' in column_lower or 'opportunity_count' in column_lower:
        description = "Number of sales opportunities or deals"
        category = "Volume Metrics"
        business_use = "Track sales activity and opportunity generation"
        
    elif 'average' in column_lower or 'avg' in column_lower:
        description = f"Average value calculated from the underlying data"
        category = "Statistical Metrics"
        business_use = "Understand typical performance levels and benchmarks"
        
    elif column_lower.endswith('_m') or 'million' in column_lower:
        description = f"Financial amount expressed in millions of dollars"
        category = "Financial Metrics"
        business_use = "High-level financial reporting and executive dashboards"
        
    elif 'rate' in column_lower or 'percentage' in column_lower:
        description = f"Percentage calculation showing ratio or performance rate"
        category = "Performance Metrics"
        business_use = "Measure efficiency and success rates"
        
    elif 'geography' in column_lower or 'region' in column_lower:
        description = "Geographic region or territory classification"
        category = "Geographic Dimensions"
        business_use = "Regional analysis and territory management"
        
    elif 'sales_stage' in column_lower or 'stage' in column_lower:
        description = "Current stage in the sales process (e.g., Prospect, Qualified, Won, Lost)"
        category = "Sales Process"
        business_use = "Track deal progression and identify bottlenecks"
        
    elif 'client' in column_lower or 'customer' in column_lower:
        description = "Client or customer name/identifier"
        category = "Customer Dimensions"
        business_use = "Customer analysis and relationship management"
        
    else:
        # Generic explanation for unknown columns
        description = f"Data column containing {column_clean.lower()} information"
        category = "Data Field"
        business_use = "Analysis and reporting purposes"
    
    # Format the tooltip
    tooltip = f"""
**{column_clean}**

📊 **Category:** {category}

📝 **Description:** {description}

💼 **Business Use:** {business_use}

🔢 **Type:** {"Numeric" if any(word in column_lower for word in ['count', 'rate', 'total', 'avg', 'sum', 'amount', 'value']) else "Text/Category"}

💡 **Note:** This is a computed column from your SQL query
"""
    
    return tooltip


def create_visualization(df: pd.DataFrame, viz_type: str, _columns_used: List[str]) -> None:
    """Create appropriate visualization based on data and type"""
    
    if df.empty:
        st.warning("No data to visualize")
        return
    
    try:
        st.subheader("📊 Data Visualization")
        
        # Check if viz_type is valid and we have enough columns
        if viz_type == "bar_chart" and len(df.columns) >= 2:
            # Find the best columns for visualization
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                
                fig = px.bar(df, x=x_col, y=y_col, 
                            title=f"{y_col} by {x_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Bar chart requires both categorical and numeric columns. Showing table instead.")
                st.dataframe(df, use_container_width=True)
            
        elif viz_type == "line_chart" and len(df.columns) >= 2:
            # Find numeric columns for line chart
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
                
                fig = px.line(df, x=x_col, y=y_col,
                             title=f"{y_col} trend over {x_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            elif len(numeric_cols) >= 1:
                # Use index as x-axis if only one numeric column
                y_col = numeric_cols[0]
                fig = px.line(df, y=y_col, title=f"{y_col} trend")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Line chart requires numeric columns. Showing table instead.")
                st.dataframe(df, use_container_width=True)
            
        elif viz_type == "pie_chart" and len(df.columns) >= 2:
            # Find appropriate columns for pie chart
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                names_col = categorical_cols[0]
                values_col = numeric_cols[0]
                
                # Aggregate data if needed
                pie_data = df.groupby(names_col)[values_col].sum().reset_index()
                
                fig = px.pie(pie_data, names=names_col, values=values_col,
                            title=f"Distribution of {values_col} by {names_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pie chart requires both categorical and numeric columns. Showing table instead.")
                st.dataframe(df, use_container_width=True)
                
        elif viz_type == "kpi" or viz_type == "metric":
            # Create KPI/Metric dashboard with large numbers and visual indicators
            st.subheader("📊 Key Performance Indicators")
            
            # Find numeric columns for KPIs
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            
            if len(numeric_cols) > 0:
                # If we have multiple rows, try to create a chart as well
                if len(df) > 1:
                    # Try to create a chart visualization
                    categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
                    
                    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                        st.write("**Visual Chart:**")
                        x_col = categorical_cols[0]
                        y_col = numeric_cols[0]
                        
                        fig = px.bar(df.head(10), x=x_col, y=y_col, 
                                    title=f"Top 10: {y_col} by {x_col}")
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Always show KPI metrics
                st.write("**Key Metrics:**")
                cols_per_row = min(len(numeric_cols), 4)
                
                # Create columns for metrics
                metric_cols = st.columns(cols_per_row)
                
                for i, col in enumerate(numeric_cols[:4]):  # Show max 4 KPIs
                    with metric_cols[i % cols_per_row]:
                        total_value = df[col].sum()
                        avg_value = df[col].mean()
                        
                        # Format the numbers nicely
                        if total_value > 1000000:
                            total_display = f"${total_value/1000000:.1f}M"
                        elif total_value > 1000:
                            total_display = f"${total_value/1000:.1f}K"
                        else:
                            total_display = f"${total_value:,.0f}"
                        
                        if avg_value > 1000000:
                            avg_display = f"${avg_value/1000000:.1f}M avg"
                        elif avg_value > 1000:
                            avg_display = f"${avg_value/1000:.1f}K avg"
                        else:
                            avg_display = f"${avg_value:,.0f} avg"
                        
                        st.metric(
                            label=col.replace('_', ' ').title(),
                            value=total_display,
                            delta=avg_display
                        )
            else:
                st.info("No numeric data available for KPI display. Showing table instead.")
                st.dataframe(df, use_container_width=True)
                
        else:
            # Default to table visualization with auto-chart generation
            st.write("**Data Table:**")
            
            # Auto-generate simple visualizations if we have the right data structure
            numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            # Try to create a meaningful chart automatically
            if len(numeric_cols) >= 1 and len(categorical_cols) >= 1 and len(df) > 1 and len(df) <= 50:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                
                # Choose chart type based on data characteristics
                if len(df[x_col].unique()) <= 10:  # Good for bar chart
                    fig = px.bar(df, x=x_col, y=y_col, 
                                title=f"Auto-Generated: {y_col} by {x_col}")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:  # Too many categories, show table only
                    pass
            
            # Always show formatted table as well
            st.write("**Data Table:**")
            
            # Format numeric columns for better display
            formatted_df = df.copy()
            
            for col in numeric_cols:
                if col.upper().endswith('_M') or 'MILLION' in col.upper():
                    # Format as millions
                    formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:.2f}M" if pd.notnull(x) else "")
                elif 'RATE' in col.upper() or 'PERCENT' in col.upper():
                    # Format as percentage
                    formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
                elif 'AMT' in col.upper() or 'VALUE' in col.upper():
                    # Format as currency
                    formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
            
            st.dataframe(formatted_df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.write("Error details:", str(e))
        # Fallback to simple table
        st.dataframe(df, use_container_width=True)


def format_number_for_display(value: float, column_name: str = "") -> str:
    """Format numbers for display based on context"""
    if pd.isna(value):
        return ""
    
    column_lower = column_name.lower()
    
    # Format based on column name patterns
    if column_lower.endswith('_m') or 'million' in column_lower:
        return f"${value:.1f}M"
    elif 'rate' in column_lower or 'percent' in column_lower:
        return f"{value:.1f}%"
    elif 'amt' in column_lower or 'value' in column_lower or 'budget' in column_lower:
        if value >= 1000000:
            return f"${value/1000000:.1f}M"
        elif value >= 1000:
            return f"${value/1000:.1f}K"
        else:
            return f"${value:,.0f}"
    elif 'count' in column_lower:
        return f"{value:,.0f}"
    else:
        # Generic number formatting
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:,.1f}"