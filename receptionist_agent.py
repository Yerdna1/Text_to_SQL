#!/usr/bin/env python3
"""
Receptionist Agent for Interactive User Guidance
Helps users provide complete context through guided conversation
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import re
from datetime import datetime

@dataclass
class UserContext:
    """Stores user-provided context information"""
    question: str = ""
    time_period: Optional[str] = None
    geography: Optional[str] = None
    product_type: Optional[str] = None
    metric_focus: Optional[str] = None
    additional_filters: List[str] = None
    confidence_level: float = 0.0
    
    def __post_init__(self):
        if self.additional_filters is None:
            self.additional_filters = []

@dataclass
class MissingContext:
    """Tracks what context is missing from user's question"""
    needs_time: bool = False
    needs_geography: bool = False
    needs_product: bool = False
    needs_metric: bool = False
    suggestions: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = {}

class ReceptionistAgent:
    """Interactive agent that guides users to provide complete context"""
    
    def __init__(self):
        self.name = "Receptionist"
        self.conversation_state = "initial"  # initial, gathering, confirming, complete
        
        # Define available options
        self.time_periods = [
            "Current Quarter", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024",
            "Current Month", "Last Month", "Year to Date", "Last Year",
            "Custom Date Range"
        ]
        
        self.geographies = [
            "Americas", "EMEA", "APAC", "Japan", 
            "USA", "Canada", "UK", "Germany", "France", "China", "India",
            "All Regions"
        ]
        
        self.product_types = [
            "Consulting Services", "Software Products", "Cloud Services",
            "AI/GenAI Solutions", "All Products", "Custom Product"
        ]
        
        self.metrics = [
            "Revenue Forecast", "Pipeline Value", "Win Rate", "Deal Count",
            "Budget Coverage", "PPV Analysis", "Sales Performance", "Custom Metric"
        ]
        
    def analyze_question(self, question: str) -> Tuple[UserContext, MissingContext]:
        """Analyze user's question to identify missing context"""
        
        # Create initial context from question
        context = UserContext(question=question)
        missing = MissingContext()
        
        question_lower = question.lower()
        
        # Analyze time context
        time_detected = self._detect_time_context(question_lower)
        if time_detected:
            context.time_period = time_detected
        else:
            missing.needs_time = True
            missing.suggestions["time"] = self._suggest_time_periods(question_lower)
        
        # Analyze geographic context  
        geo_detected = self._detect_geographic_context(question_lower)
        if geo_detected:
            context.geography = geo_detected
        else:
            missing.needs_geography = True
            missing.suggestions["geography"] = self._suggest_geographies(question_lower)
            
        # Analyze product context
        product_detected = self._detect_product_context(question_lower)
        if product_detected:
            context.product_type = product_detected
        else:
            missing.needs_product = True
            missing.suggestions["product"] = self._suggest_products(question_lower)
            
        # Analyze metric context
        metric_detected = self._detect_metric_context(question_lower)
        if metric_detected:
            context.metric_focus = metric_detected
        else:
            missing.needs_metric = True
            missing.suggestions["metric"] = self._suggest_metrics(question_lower)
        
        # Calculate confidence based on completeness
        total_aspects = 4
        provided_aspects = sum([
            bool(context.time_period),
            bool(context.geography), 
            bool(context.product_type),
            bool(context.metric_focus)
        ])
        context.confidence_level = provided_aspects / total_aspects
        
        return context, missing
    
    def _detect_time_context(self, question: str) -> Optional[str]:
        """Detect time period from question"""
        
        # Current period indicators
        if any(word in question for word in ["current", "this month", "this quarter", "now", "today"]):
            if "quarter" in question:
                return "Current Quarter"
            elif "month" in question:
                return "Current Month"
            else:
                return "Current Quarter"
                
        # Specific quarters
        quarter_match = re.search(r'q(\d)|quarter (\d)', question)
        if quarter_match:
            q_num = quarter_match.group(1) or quarter_match.group(2)
            year_match = re.search(r'20\d{2}', question)
            year = year_match.group() if year_match else "2024"
            return f"Q{q_num} {year}"
            
        # Year indicators
        if "ytd" in question or "year to date" in question:
            return "Year to Date"
        if "last year" in question:
            return "Last Year"
        if "last month" in question:
            return "Last Month"
            
        return None
    
    def _detect_geographic_context(self, question: str) -> Optional[str]:
        """Detect geographic region from question"""
        
        region_mappings = {
            "americas": "Americas",
            "america": "Americas", 
            "us": "USA",
            "usa": "USA",
            "canada": "Canada",
            "emea": "EMEA",
            "europe": "EMEA",
            "uk": "UK",
            "germany": "Germany",
            "france": "France",
            "apac": "APAC",
            "asia": "APAC",
            "pacific": "APAC",
            "china": "China",
            "india": "India",
            "japan": "Japan"
        }
        
        for keyword, region in region_mappings.items():
            if keyword in question:
                return region
                
        return None
    
    def _detect_product_context(self, question: str) -> Optional[str]:
        """Detect product type from question"""
        
        if "consulting" in question:
            return "Consulting Services"
        elif "software" in question:
            return "Software Products"
        elif "cloud" in question:
            return "Cloud Services"
        elif any(word in question for word in ["ai", "genai", "gen ai", "artificial intelligence"]):
            return "AI/GenAI Solutions"
            
        return None
    
    def _detect_metric_context(self, question: str) -> Optional[str]:
        """Detect metric focus from question"""
        
        metric_keywords = {
            "revenue": "Revenue Forecast",
            "forecast": "Revenue Forecast", 
            "pipeline": "Pipeline Value",
            "win rate": "Win Rate",
            "deals": "Deal Count",
            "opportunities": "Deal Count",
            "budget": "Budget Coverage",
            "coverage": "Budget Coverage",
            "ppv": "PPV Analysis",
            "performance": "Sales Performance"
        }
        
        for keyword, metric in metric_keywords.items():
            if keyword in question:
                return metric
                
        return None
    
    def _suggest_time_periods(self, question: str) -> List[str]:
        """Suggest relevant time periods based on question context"""
        suggestions = ["Current Quarter", "Year to Date"]
        
        if "forecast" in question or "pipeline" in question:
            suggestions.extend(["Q4 2024", "Current Month"])
        if "compare" in question or "vs" in question:
            suggestions.extend(["Last Quarter", "Last Year"])
            
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _suggest_geographies(self, question: str) -> List[str]:
        """Suggest relevant geographies"""
        return ["Americas", "EMEA", "APAC", "All Regions"]
    
    def _suggest_products(self, question: str) -> List[str]:
        """Suggest relevant product types"""
        suggestions = ["All Products"]
        
        if any(word in question for word in ["ai", "technology", "innovation"]):
            suggestions.append("AI/GenAI Solutions")
        suggestions.extend(["Consulting Services", "Software Products"])
        
        return suggestions[:4]
    
    def _suggest_metrics(self, question: str) -> List[str]:
        """Suggest relevant metrics"""
        suggestions = []
        
        if any(word in question for word in ["total", "sum", "revenue", "money"]):
            suggestions.append("Revenue Forecast")
        if "pipeline" in question:
            suggestions.append("Pipeline Value")
        if any(word in question for word in ["performance", "success"]):
            suggestions.append("Win Rate")
            
        suggestions.extend(["Budget Coverage", "Deal Count"])
        return suggestions[:4]
    
    def render_interactive_chat(self, context: UserContext, missing: MissingContext) -> UserContext:
        """Render interactive chat interface in Streamlit"""
        
        st.subheader("🤖 Sales Analytics Assistant")
        
        # Show current context
        if context.confidence_level > 0:
            st.success(f"✅ Context Understanding: {context.confidence_level:.0%}")
            
            with st.expander("📋 Current Context", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    if context.time_period:
                        st.write(f"📅 **Time Period**: {context.time_period}")
                    if context.geography:
                        st.write(f"🌍 **Geography**: {context.geography}")
                        
                with col2:
                    if context.product_type:
                        st.write(f"📦 **Product Type**: {context.product_type}")
                    if context.metric_focus:
                        st.write(f"📊 **Metric Focus**: {context.metric_focus}")
        
        # Guide user to complete missing context
        if context.confidence_level < 1.0:
            st.warning("🔍 I need a bit more information to give you the best results!")
            
            # Time Period Selection
            if missing.needs_time:
                st.write("⏰ **Which time period are you interested in?**")
                cols = st.columns(len(missing.suggestions.get("time", self.time_periods[:4])))
                
                for i, period in enumerate(missing.suggestions.get("time", self.time_periods[:4])):
                    with cols[i]:
                        if st.button(period, key=f"time_{i}"):
                            context.time_period = period
                            missing.needs_time = False
                            st.rerun()
            
            # Geography Selection  
            if missing.needs_geography:
                st.write("🌍 **Which geographic region?**")
                cols = st.columns(len(missing.suggestions.get("geography", self.geographies[:4])))
                
                for i, geo in enumerate(missing.suggestions.get("geography", self.geographies[:4])):
                    with cols[i]:
                        if st.button(geo, key=f"geo_{i}"):
                            context.geography = geo
                            missing.needs_geography = False
                            st.rerun()
            
            # Product Type Selection
            if missing.needs_product:
                st.write("📦 **Which product or service type?**")
                cols = st.columns(len(missing.suggestions.get("product", self.product_types[:4])))
                
                for i, product in enumerate(missing.suggestions.get("product", self.product_types[:4])):
                    with cols[i]:
                        if st.button(product, key=f"product_{i}"):
                            context.product_type = product
                            missing.needs_product = False
                            st.rerun()
            
            # Metric Focus Selection
            if missing.needs_metric:
                st.write("📊 **What type of analysis do you want?**")
                cols = st.columns(len(missing.suggestions.get("metric", self.metrics[:4])))
                
                for i, metric in enumerate(missing.suggestions.get("metric", self.metrics[:4])):
                    with cols[i]:
                        if st.button(metric, key=f"metric_{i}"):
                            context.metric_focus = metric
                            missing.needs_metric = False
                            st.rerun()
        
        else:
            st.success("🎯 Perfect! I have all the context I need.")
            
            # Show final refined question
            refined_question = self._build_refined_question(context)
            st.info(f"**Refined Question**: {refined_question}")
            
            # Update context with refined question
            context.question = refined_question
        
        # Recalculate confidence
        total_aspects = 4
        provided_aspects = sum([
            bool(context.time_period),
            bool(context.geography), 
            bool(context.product_type),
            bool(context.metric_focus)
        ])
        context.confidence_level = provided_aspects / total_aspects
        
        return context
    
    def _build_refined_question(self, context: UserContext) -> str:
        """Build a refined question with all context"""
        
        # Start with metric focus
        question_parts = []
        
        if context.metric_focus:
            if "Revenue" in context.metric_focus:
                question_parts.append("What is the total revenue forecast")
            elif "Pipeline" in context.metric_focus:
                question_parts.append("What is the pipeline value")
            elif "Win Rate" in context.metric_focus:
                question_parts.append("What is the win rate")
            elif "Deal Count" in context.metric_focus:
                question_parts.append("How many deals")
            elif "Budget" in context.metric_focus:
                question_parts.append("What is the budget coverage")
            elif "PPV" in context.metric_focus:
                question_parts.append("What is the PPV analysis")
            else:
                question_parts.append("What is the sales performance")
        else:
            question_parts.append("Show me the analysis")
        
        # Add product context
        if context.product_type and context.product_type != "All Products":
            if "AI/GenAI" in context.product_type:
                question_parts.append("for AI and GenAI solutions")
            elif "Consulting" in context.product_type:
                question_parts.append("for consulting services")
            elif "Software" in context.product_type:
                question_parts.append("for software products")
            elif "Cloud" in context.product_type:
                question_parts.append("for cloud services")
        
        # Add geographic context
        if context.geography and context.geography != "All Regions":
            question_parts.append(f"in {context.geography}")
        
        # Add time context
        if context.time_period:
            if "Current Quarter" in context.time_period:
                question_parts.append("for the current quarter")
            elif "Current Month" in context.time_period:
                question_parts.append("for the current month")
            elif "Year to Date" in context.time_period:
                question_parts.append("year to date")
            elif "Q" in context.time_period:
                question_parts.append(f"for {context.time_period}")
            else:
                question_parts.append(f"for {context.time_period}")
        
        return " ".join(question_parts) + "?"
    
    def should_intervene(self, question: str) -> bool:
        """Determine if receptionist should intervene based on question completeness"""
        context, missing = self.analyze_question(question)
        
        # Intervene if confidence is low or critical context is missing
        if context.confidence_level < 0.5:
            return True
            
        # Always intervene if no time period is specified
        if missing.needs_time:
            return True
            
        return False


def create_step_visualization(processing_log: List[Dict]) -> None:
    """Create a detailed step-by-step visualization of agent processing"""
    
    st.write("**🔍 Multi-Agent Processing Pipeline**")
    
    # Create a progress visualization
    total_steps = len(processing_log)
    
    for i, step in enumerate(processing_log):
        agent_name = step['agent']
        success = step['success']
        message = step['message']
        
        # Create step container
        with st.container():
            # Step header
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                # Step number with status
                if success:
                    st.success(f"**{i+1}**")
                else:
                    st.error(f"**{i+1}**")
            
            with col2:
                # Agent info and message
                if agent_name == "DB2SyntaxValidator":
                    st.write(f"🔍 **{agent_name}**: {message}")
                    
                    # Show detailed syntax validation
                    if step.get('confidence'):
                        st.write(f"   📊 Confidence: {step['confidence']:.0%}")
                    
                elif agent_name == "WhereClauseEnhancer":
                    st.write(f"🎯 **{agent_name}**: {message}")
                    
                    # Show enhancements inline
                    if step.get('enhancements'):
                        st.write("   **✅ Enhancements Applied:**")
                        for enhancement in step['enhancements']:
                            st.write(f"   • {enhancement}")
                                
                elif agent_name == "QueryOptimizer":
                    st.write(f"🚀 **{agent_name}**: {message}")
                    
                    # Show optimizations inline
                    if step.get('optimizations'):
                        st.write("   **⚡ Optimizations Applied:**")
                        for opt in step['optimizations']:
                            st.write(f"   • {opt}")
                            
                elif agent_name == "ColumnValidation":
                    st.write(f"🔍 **{agent_name}**: {message}")
                    
                    # Show column validation details
                    if step.get('confidence'):
                        st.write(f"   📊 Confidence: {step['confidence']:.0%}")
                    
                    if step.get('missing_columns'):
                        st.write("   **❌ Missing Columns:**")
                        for col in step['missing_columns']:
                            st.write(f"   • {col['column']} (from {col['table']})")
                    
                    if step.get('substitutions'):
                        st.write("   **🔄 Column Substitutions:**")
                        for sub in step['substitutions']:
                            st.write(f"   • {sub}")
                            
                elif agent_name == "SQLRegeneration":
                    st.write(f"🔄 **{agent_name}**: {message}")
                    
                    if step.get('confidence'):
                        st.write(f"   📊 Regeneration Confidence: {step['confidence']:.0%}")
                        
                elif agent_name == "ColumnValidation-Recheck":
                    st.write(f"✅ **{agent_name}**: {message}")
                    
                    if step.get('confidence'):
                        st.write(f"   📊 Recheck Confidence: {step['confidence']:.0%}")
            
            with col3:
                # Status indicator
                if success:
                    st.write("✅")
                else:
                    st.write("❌")
        
        # Add connecting line (except for last step)
        if i < total_steps - 1:
            st.write("   ⬇️")


# Test function
def test_receptionist():
    """Test the receptionist agent"""
    
    receptionist = ReceptionistAgent()
    
    # Test cases
    test_questions = [
        "What is the total revenue?",  # Missing everything
        "Show me Americas pipeline for Q4",  # Missing product and metric
        "What is the AI revenue forecast for current quarter?",  # Missing geography
        "Show me consulting performance in EMEA for 2024"  # Complete
    ]
    
    for question in test_questions:
        print(f"\n🔍 Question: {question}")
        context, missing = receptionist.analyze_question(question)
        
        print(f"Confidence: {context.confidence_level:.0%}")
        print(f"Should intervene: {receptionist.should_intervene(question)}")
        
        if missing.needs_time:
            print(f"Missing time, suggestions: {missing.suggestions.get('time', [])}")
        if missing.needs_geography:
            print(f"Missing geography, suggestions: {missing.suggestions.get('geography', [])}")
        if missing.needs_product:
            print(f"Missing product, suggestions: {missing.suggestions.get('product', [])}")
        if missing.needs_metric:
            print(f"Missing metric, suggestions: {missing.suggestions.get('metric', [])}")


if __name__ == "__main__":
    test_receptionist()