import streamlit as st
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Fitness Planner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports
from views.profile import render_profile_view
from views.workout import render_workout_view
from views.diet import render_diet_view
from views.chatbot import render_chatbot_view
from utils.ai_client import configure_genai

# Init GenAI
configure_genai()

# Session State
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

# Sidebar
with st.sidebar:
    st.title("💪 AI Fitness")
    st.caption("Personal Health Companion")
    
    # Theme Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    st.markdown("---")
    
    # Navigation
    selection = st.radio(
        "Navigation",
        ["📊 Profile & BMI", "🏋️ Workout Routine", "🥗 Diet Plan", "💬 AI Trainer Chat"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # About
    with st.expander("ℹ️ About App"):
        st.markdown("""
        **AI Fitness Planner**
        
        Uses Gemini AI to generate personalized:
        - Workout Routines
        - Diet Plans
        
        *Ensure API Key is set.*
        """)
        
    api_key_status = "✅ Connected" if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here" else "❌ Not Connected"
    st.caption(f"Status: {api_key_status}")

# CSS Variables based on Mode
if dark_mode:
    # Dark Theme Colors
    bg_color = "#0E1117"
    sidebar_bg = "#262730"
    card_bg = "#1E1E1E" # Slightly different for contrast
    text_color = "#FAFAFA"
    secondary_text = "#B0B0B0"
    accent = "#FF4B4B"
    border_color = "rgba(250, 250, 250, 0.1)"
    input_bg = "#2C2C2C"
else:
    # Light Theme Colors
    bg_color = "#FFFFFF"
    sidebar_bg = "#F0F2F6"
    card_bg = "#FFFFFF"
    text_color = "#31333F"
    secondary_text = "#555555"
    accent = "#FF4B4B"
    border_color = "rgba(49, 51, 63, 0.1)"
    input_bg = "#FAFAFA"

# Inject CSS
st.markdown(f"""
<style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
        --primary-color: {accent};
        --background-color: {bg_color};
        --sidebar-background: {sidebar_bg};
        --secondary-background-color: {card_bg};
        --text-color: {text_color};
        --font: 'Inter', sans-serif;
    }}
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {text_color};
    }}
    
    /* Main Background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: {text_color} !important;
    }}
    
    /* Global Text Color Override */
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    h1 {{
        background: linear-gradient(120deg, {accent}, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }}
    
    /* Cards (Containers) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 24px;
        border: 1px solid {border_color};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }}
    
    /* Inputs Styles */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color};
        border-radius: 8px;
    }}
    
    /* Fix Labels specifically */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label, .stRadio label {{
        color: {text_color} !important;
        font-weight: 500;
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(90deg, {accent}, #FF914D);
        color: white !important;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
        color: white !important;
    }}
    .stButton > button p {{
        color: white !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {input_bg};
        color: {text_color} !important;
        border-radius: 8px;
        border: 1px solid {border_color};
    }}
    .streamlit-expanderContent {{
        background-color: {card_bg};
        color: {text_color} !important;
        border: 1px solid {border_color};
        border-top: none;
    }}
    
    /* Metric styling override */
    [data-testid="stMetricValue"] {{
        color: {accent} !important;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {bg_color};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {secondary_text};
        border-radius: 4px;
    }}
    
</style>
""", unsafe_allow_html=True)

# Routing
if selection == "📊 Profile & BMI":
    render_profile_view()
elif selection == "🏋️ Workout Routine":
    render_workout_view()
elif selection == "🥗 Diet Plan":
    render_diet_view()
elif selection == "💬 AI Trainer Chat":
    render_chatbot_view()
