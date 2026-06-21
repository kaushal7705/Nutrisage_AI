import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.config import DOCS_DIR, METADATA_FILE, validate_config
from src.health_utils import generate_health_summary
from src.meal_planner import generate_meal_plan
from src.rag_engine import NutritionRAGEngine

# Configure page layout and responsiveness
st.set_page_config(
    page_title="NutriSage AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Caching of the RAG Embedding and Database Engine
@st.cache_resource
def get_rag_engine():
    """
    Initialize and cache the RAG retrieval engine on startup.
    This prevents reloading the HuggingFace embedding model on page refreshes.
    """
    return NutritionRAGEngine()

# Check API key configuration status
api_configured = validate_config()

# Load cached RAG Engine (only if configured, or default initialized for schema stats)
rag_engine = get_rag_engine()

# Custom CSS for a clean, premium, and responsive healthcare UI appearance
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Maximize content width and reduce default spacing */
    .main .block-container {
        max-width: 90% !important;
        padding-top: 2rem !important;
        padding-right: 2rem !important;
        padding-left: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Responsive custom sidebar styling */
    [data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
    }
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #F8FAFC;
    }
    
    /* Dashboard main title */
    .dashboard-title {
        font-size: 34px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    
    /* Custom cards */
    .metric-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        text-align: left;
        transition: all 0.25s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-val {
        font-size: 28px;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-sub {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Indian Meal Cards */
    .meal-card-upgrade {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #10B981;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .meal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .meal-title-text {
        font-size: 17px;
        font-weight: 700;
        color: #1E293B;
    }
    .meal-tag {
        font-size: 11px;
        background-color: #ECFDF5;
        color: #065F46;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
    }
    .meal-body {
        font-size: 14px;
        color: #475569;
        line-height: 1.5;
    }
    .meal-footer {
        display: flex;
        gap: 15px;
        font-size: 12px;
        color: #64748B;
        margin-top: 10px;
        border-top: 1px solid #F1F5F9;
        padding-top: 6px;
        font-weight: 500;
    }
    
    /* Info Banner */
    .info-banner {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 12px;
        color: #334155;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 25px;
    }
    
    /* Chat messages */
    .chat-card {
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-size: 14.5px;
        line-height: 1.5;
        max-width: 85%;
    }
    .user-card {
        background-color: #EFF6FF;
        color: #1E40AF;
        margin-left: auto;
        border: 1px solid #DBEAFE;
    }
    .bot-card {
        background-color: #FFFFFF;
        color: #334155;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #10B981;
        margin-right: auto;
    }
    .bot-sources {
        font-size: 11.5px;
        color: #94A3B8;
        border-top: 1px dashed #E2E8F0;
        margin-top: 8px;
        padding-top: 5px;
    }
    
    /* General Disclaimer Footer */
    .medical-disclaimer {
        font-size: 11px;
        color: #94A3B8;
        text-align: center;
        margin-top: 40px;
        border-top: 1px solid #E2E8F0;
        padding-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Chat History in state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Initialize pre-population query handler
if "prepopulated_query" not in st.session_state:
    st.session_state.prepopulated_query = None

# Fetch knowledge base metadata
metadata = rag_engine.get_metadata()

# Sidebar layout
with st.sidebar:
    st.markdown("<h3 style='margin-top:10px; margin-bottom:2px;'>NutriSage AI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:#64748B; margin-top:0; margin-bottom:15px;'>Your Personalized Nutrition Companion</p>", unsafe_allow_html=True)
    
    if not api_configured:
        st.warning("🔑 **AI Coach Offline**: Set up a valid `GEMINI_API_KEY` in `.env` to start chatting.")
    else:
        st.success("⚡ **AI Coach Online**")



# Header layout
st.markdown("<h1 class='dashboard-title'>NutriSage AI 🥗</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:15px; color:#64748B; margin-top:0; margin-bottom:25px;'>Personalized physiological assessments, custom Indian meal planning, and intelligent AI coaching.</p>", unsafe_allow_html=True)

# App Navigation
tab_assess, tab_meals, tab_coach = st.tabs([
    "📊 Health Assessment", 
    "🍽️ Indian Meal Planner", 
    "💬 AI Nutrition Coach"
])

# ----------------- Tab 1: Health Assessment -----------------
with tab_assess:
    st.markdown("""
    <div class="info-banner">
        <strong>Physiological Evaluation</strong><br/>
        Calculate your Body Mass Index (BMI), Basal Metabolic Rate (BMR), and Total Daily Energy Expenditure (TDEE) to customize your daily nutrition targets.
    </div>
    """, unsafe_allow_html=True)
    
    col_input, col_result = st.columns([1, 1.5])
    
    with col_input:
        st.subheader("Physiological Specifications")
        with st.form("health_form_refactored"):
            gender = st.selectbox("Biological Gender", ["Male", "Female"])
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=25, step=1)
            weight = st.number_input("Weight (kg)", min_value=10.0, max_value=250.0, value=70.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=175.0, step=1.0)
            
            activity = st.selectbox("Physical Activity Profile", [
                "Sedentary (little/no exercise)",
                "Lightly Active (exercise 1-3 days/week)",
                "Moderately Active (exercise 3-5 days/week)",
                "Very Active (exercise 6-7 days/week)",
                "Extra Active (hard physical job or 2x training)"
            ], index=2)
            
            submit_assess = st.form_submit_button("Compute Health Profile")
            
    with col_result:
        st.subheader("Health Profile Summary")
        if submit_assess or 'health_summary' in st.session_state:
            # Perform calculation
            summary = generate_health_summary(weight, height, age, gender, activity)
            st.session_state.health_summary = summary
            st.session_state.assess_weight = weight
            st.session_state.assess_height = height
            st.session_state.assess_age = age
            st.session_state.assess_gender = gender
            st.session_state.assess_activity = activity
            
            # Display CSS metric cards
            card_col1, card_col2 = st.columns(2)
            with card_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Body Mass Index (BMI)</div>
                    <div class="metric-val" style="color: {summary['bmi_color']};">{summary['bmi']}</div>
                    <div class="metric-sub">Classification: <strong>{summary['bmi_status']}</strong></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="margin-top:15px;" class="metric-card">
                    <div class="metric-label">Target Weight</div>
                    <div class="metric-val" style="color: #3B82F6;">{summary['ideal_weight_kg']} kg</div>
                    <div class="metric-sub">Healthy target weight value</div>
                </div>
                """, unsafe_allow_html=True)
                
            with card_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Basal Metabolic Rate (BMR)</div>
                    <div class="metric-val" style="color: #10B981;">{int(summary['bmr'])} kcal</div>
                    <div class="metric-sub">Calories burned at complete rest</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="margin-top:15px;" class="metric-card">
                    <div class="metric-label">Active Burn (TDEE)</div>
                    <div class="metric-val" style="color: #F59E0B;">{int(summary['tdee'])} kcal</div>
                    <div class="metric-sub">Daily maintenance intake</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div style="background-color:#F8FAFC; border: 1px solid #E2E8F0; border-radius:12px; padding:18px; margin-top:20px; font-size:13.5px; color:#475569;">
                <strong>Health Feedback:</strong> {summary['bmi_feedback']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Please fill out the specifications and click 'Compute Health Profile' to display your body metrics summary.")

# ----------------- Tab 2: Indian Meal Planner -----------------
with tab_meals:
    if 'health_summary' not in st.session_state:
        st.warning("⚠️ Please complete the physiological assessment in the first tab to calibrate your maintenance calories.")
    else:
        col_meal_inputs, col_meal_output = st.columns([1, 1.5])
        
        with col_meal_inputs:
            st.subheader("Calorie & Dietary Configurations")
            goal = st.selectbox("Caloric Target Selection", [
                ("Weight Loss (500 kcal Deficit)", "weight_loss"),
                ("Weight Maintenance (TDEE Match)", "maintenance"),
                ("Weight Gain (500 kcal Surplus)", "weight_gain")
            ], format_func=lambda x: x[0])
            
            diet_type = st.selectbox("Dietary Preference Profile", ["Vegetarian", "Non-Vegetarian"])
            
            st.markdown("""
            **Macro Allocation Philosophy**:
            - **Weight Loss**: High Protein (35%) / Low Carb (40%) to preserve lean mass.
            - **Maintenance**: Balanced distribution (50% Carbs, 20% Protein, 30% Fat).
            - **Weight Gain**: High Carb (55%) / Moderate Protein (25%) for muscle hypertrophy.
            """)
            
        with col_meal_output:
            st.subheader("Target Nutrition Split")
            
            # Generate target splits
            plan = generate_meal_plan(st.session_state.health_summary["tdee"], goal[1], diet_type)
            target_cals = plan["target_calories"]
            macros = plan["macros"]
            meals = plan["meals"]
            
            st.markdown(f"Adjusted Target Caloric Intake: **{int(target_cals)} kcal/day**")
            
            # Plotly Donut Chart representing macro breakdown
            macro_df = pd.DataFrame({
                "Macronutrient": ["Carbohydrates", "Protein", "Fat"],
                "Grams": [macros["carbs_g"], macros["protein_g"], macros["fat_g"]],
                "Calories": [macros["carbs_g"]*4, macros["protein_g"]*4, macros["fat_g"]*9],
                "Color": ["#3B82F6", "#10B981", "#EF4444"]
            })
            
            fig = go.Figure(data=[go.Pie(
                labels=macro_df["Macronutrient"],
                values=macro_df["Calories"],
                hole=.4,
                marker=dict(colors=macro_df["Color"]),
                textinfo="label+percent",
                hoverinfo="text",
                hovertext=[f"{g}g" for g in macro_df["Grams"]]
            )])
            fig.update_layout(
                margin=dict(t=5, b=5, l=5, r=5),
                height=180,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Render meal cards
            st.markdown("### Suggested Daily Meal Plan")
            for m_key, m_info in [("Breakfast", meals["breakfast"]), ("Lunch", meals["lunch"]), ("Snack", meals["snack"]), ("Dinner", meals["dinner"])]:
                st.markdown(f"""
                <div class="meal-card-upgrade">
                    <div class="meal-header">
                        <span class="meal-title-text">{m_key}</span>
                        <span class="meal-tag">{m_info['calories']} kcal</span>
                    </div>
                    <div class="meal-body">{m_info['menu']}</div>
                    <div class="meal-footer">
                        <span>🍗 Protein: <strong>{m_info['protein']}g</strong></span>
                        <span>⚡ Calorie Allocation: <strong>{int((m_info['calories']/target_cals)*100)}%</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ----------------- Tab 3: AI Nutrition Coach -----------------
with tab_coach:
    col_left_space, col_chat, col_right_space = st.columns([1, 4, 1])
    
    with col_chat:
        st.subheader("💬 AI Nutrition Coach")
        
        # Ingestion alert message
        if not api_configured:
            st.warning("🔑 **AI Coach Offline**: Add a valid `GEMINI_API_KEY` to your `.env` file to enable grounded guidelines chat.")
        elif metadata["num_chunks_indexed"] == 0:
            st.warning("⚠️ The coach's knowledge base is currently empty. Place PDF files inside the 'data/raw_documents/' folder and run 'Update Coach Knowledge' in the sidebar to configure the coach.")
            
        # Chat log viewport
        chat_container = st.container(height=380)
        with chat_container:
            for message in st.session_state.chat_messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-card user-card">
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    sources_html = ""
                    if message.get("sources"):
                        sources_list = ", ".join(message["sources"])
                        sources_html = f"<div class='bot-sources'>📖 <b>Verified Guide References:</b> {sources_list}</div>"
                    st.markdown(f"""
                    <div class="chat-card bot-card">
                        {message["content"]}
                        {sources_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
        # Check if an example question was clicked
        current_input_value = ""
        if st.session_state.prepopulated_query:
            current_input_value = st.session_state.prepopulated_query
            # Reset immediately to avoid infinite loop
            st.session_state.prepopulated_query = None
            
        # Chat input element
        user_query = st.chat_input("Ask a nutrition or dietary question...", disabled=not api_configured)
        
        # Handle query from either input field or clicked example question
        active_query = user_query if user_query else current_input_value
        
        if active_query and active_query.strip():
            active_query = active_query.strip()
            # Display user query
            st.session_state.chat_messages.append({"role": "user", "content": active_query})
            
            with st.spinner("Consulting guidelines and synthesizing response..."):
                response = rag_engine.answer_query(active_query)
                
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"]
            })
            st.rerun()


