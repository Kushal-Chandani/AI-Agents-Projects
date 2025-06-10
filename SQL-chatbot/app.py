import streamlit as st
import pandas as pd
from datetime import datetime
from db.initialize_db import init_db
from utils.sql_generator import SQLGenerator
from utils.db_utils import execute_query

# Initialize DB at startup
try:
    init_db()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
    st.stop()

# Set Streamlit page configuration
st.set_page_config(
    page_title="SQL Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for aesthetic dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
        color: #ffffff;
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
    }
    
    /* Header styling with subtle gradient */
    .main-header {
        padding: 2.5rem 0 1.5rem 0;
        text-align: center;
        color: #ffffff;
        background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, transparent 100%);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        font-size: 1.1rem;
        color: #a0a0a0;
        margin: 1rem 0 0 0;
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    /* Chat container with enhanced styling */
    .chat-container {
        padding: 2rem 1rem;
        min-height: 450px;
        max-height: 650px;
        overflow-y: auto;
        background: rgba(255,255,255,0.01);
        border-radius: 16px;
        margin: 1rem 0 2rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* Enhanced message styling */
    .user-message {
        background: linear-gradient(135deg, #2a2a2a 0%, #333333 100%);
        color: #ffffff;
        padding: 1.25rem 1.5rem;
        border-radius: 18px 18px 6px 18px;
        margin: 1rem 0;
        margin-left: auto;
        max-width: 75%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        font-weight: 400;
        line-height: 1.5;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        color: #ffffff;
        padding: 1.25rem 1.5rem;
        border-radius: 18px 18px 18px 6px;
        margin: 1rem 0;
        margin-right: auto;
        max-width: 85%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .result-message {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #ffffff;
        padding: 1.25rem 1.5rem;
        border-radius: 18px 18px 18px 6px;
        margin: 1rem 0;
        margin-right: auto;
        max-width: 85%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        line-height: 1.6;
    }
    
    .sql-code {
        background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
        color: #ffffff;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        margin: 0.8rem 0;
        font-size: 0.9rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        line-height: 1.4;
        overflow-x: auto;
    }
    
    /* Enhanced input container */
    .input-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        padding: 1.5rem;
        border-radius: 20px;
        position: sticky;
        bottom: 0;
        z-index: 100;
        margin: 2rem 0 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
    }
    
    /* Enhanced sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #000000 0%, #0a0a0a 100%);
        color: #ffffff;
    }
    
    .conversation-item {
        background: linear-gradient(135deg, #2a2a2a 0%, #333333 100%);
        color: #ffffff;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .conversation-item:hover {
        background: linear-gradient(135deg, #3a3a3a 0%, #444444 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border-color: rgba(255,255,255,0.15);
    }
    
    .conversation-preview {
        font-size: 0.9rem;
        color: #d0d0d0;
        font-weight: 400;
        line-height: 1.4;
    }
    
    .conversation-time {
        font-size: 0.8rem;
        color: #888888;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Enhanced stats cards */
    .stats-card {
        background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%);
        color: #ffffff;
        padding: 1.25rem 1rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }
    
    .stats-number {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stats-label {
        font-size: 0.85rem;
        color: #b0b0b0;
        margin-top: 0.25rem;
        font-weight: 400;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #444444 0%, #555555 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #555555 0%, #666666 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Enhanced text input styling */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 0.875rem 1.25rem;
        font-size: 0.95rem;
        font-weight: 400;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        outline: none;
        border-color: rgba(255,255,255,0.3);
        box-shadow: 0 0 0 3px rgba(255,255,255,0.1);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #888888;
        font-weight: 300;
    }
    
    /* Enhanced scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #555555 0%, #444444 100%);
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #666666 0%, #555555 100%);
    }
    
    /* Welcome section enhancement */
    .welcome-section {
        text-align: center;
        padding: 3rem 2rem;
        color: #a0a0a0;
        background: rgba(255,255,255,0.02);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .welcome-section h3 {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        letter-spacing: -0.01em;
    }
    
    .welcome-section ul {
        text-align: left;
        display: inline-block;
        list-style: none;
        padding: 0;
    }
    
    .welcome-section li {
        padding: 0.5rem 0;
        color: #d0d0d0;
        font-weight: 400;
        line-height: 1.5;
    }
    
    .welcome-section li:before {
        content: "→";
        color: #666666;
        margin-right: 0.75rem;
        font-weight: 600;
    }
    
    .welcome-section code {
        background: rgba(255,255,255,0.1);
        color: #ffffff;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Form enhancement */
    .stForm {
        background: transparent;
        border: none;
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-color: #666666 transparent transparent transparent;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = []
if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = []
if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# Enhanced Sidebar
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 1.5rem; font-weight: 600; color: #ffffff;'>Conversations</h3>", unsafe_allow_html=True)
    
    # Enhanced Stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(st.session_state.conversations)}</div>
            <div class="stats-label">Conversations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{st.session_state.query_count}</div>
            <div class="stats-label">Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # New conversation button
    if st.button("✨ New Conversation", use_container_width=True):
        if st.session_state.current_conversation:
            conversation_title = st.session_state.current_conversation[0]['content'][:45] + "..." if len(st.session_state.current_conversation[0]['content']) > 45 else st.session_state.current_conversation[0]['content']
            st.session_state.conversations.append({
                'title': conversation_title,
                'messages': st.session_state.current_conversation.copy(),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'id': len(st.session_state.conversations)
            })
        st.session_state.current_conversation = []
        st.session_state.conversation_count += 1
        st.rerun()
    
    # Display conversation history
    if st.session_state.conversations:
        st.markdown("<h4 style='margin: 1.5rem 0 1rem 0; font-weight: 500; color: #cccccc;'>Recent Chats</h4>", unsafe_allow_html=True)
        for i, conv in enumerate(reversed(st.session_state.conversations[-8:])):
            with st.container():
                if st.button(f"{conv['title']}", key=f"conv_{i}", use_container_width=True):
                    st.session_state.current_conversation = conv['messages'].copy()
                    st.rerun()
                st.markdown(f'<div class="conversation-time">📅 {conv["timestamp"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Clear all conversations
    if st.session_state.conversations:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
            st.session_state.conversations = []
            st.session_state.current_conversation = []
            st.session_state.query_count = 0
            st.rerun()

# Enhanced Main content
st.markdown("""
<div class="main-header">
    <h1>SQL Assistant</h1>
    <p>Transform your questions into powerful SQL queries</p>
</div>
""", unsafe_allow_html=True)

def format_data_naturally(df):
    """Enhanced data formatting with better structure"""
    if df.empty:
        return "🔍 No data found for your query."
    
    rows = len(df)
    cols = list(df.columns)
    
    # Enhanced summary with emojis
    if rows == 1:
        summary = f"📊 Found **1 record**:\n\n"
    else:
        summary = f"📊 Found **{rows} records**:\n\n"
    
    if rows <= 8:
        result_text = summary
        for i, row in df.iterrows():
            result_text += f"**Record {i+1}:**\n"
            for col in cols:
                value = row[col] if not pd.isna(row[col]) else "*Not specified*"
                result_text += f"   • **{col}:** {value}\n"
            result_text += "\n"
    else:
        result_text = summary
        for i, row in df.head(5).iterrows():
            result_text += f"**Record {i+1}:**\n"
            for col in cols[:5]:  # Show max 5 columns
                value = row[col] if not pd.isna(row[col]) else "*Not specified*"
                result_text += f"   • **{col}:** {value}\n"
            result_text += "\n"
        if rows > 5:
            result_text += f"*... and **{rows - 5}** more records*\n"
    
    return result_text

# Instantiate SQL generator
sql_gen = SQLGenerator()

# Enhanced Chat interface
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.current_conversation:
        st.markdown("""
        <div class="welcome-section">
            <h3>👋 Welcome to SQL Assistant</h3>
            <p style="margin-bottom: 2rem;">Ask questions about your <code>connections</code> database in plain English.</p>
            <div style="margin-bottom: 1.5rem;">
                <strong style="color: #ffffff;">💡 Try these examples:</strong>
            </div>
            <ul>
                <li>Show all connections from last month</li>
                <li>How many active connections do we have?</li>
                <li>What's the average connection duration?</li>
                <li>Find connections with errors</li>
                <li>Show top 10 longest connections</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.current_conversation:
            if msg['role'] == 'user':
                st.markdown(f'<div class="user-message">💬 **You:** {msg["content"]}</div>', unsafe_allow_html=True)
            elif msg['role'] == 'assistant':
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 SQL Query Generated:</strong>
                    <div class="sql-code">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            elif msg['role'] == 'result':
                if isinstance(msg['content'], pd.DataFrame):
                    content = format_data_naturally(msg['content'])
                else:
                    content = msg['content']
                st.markdown(f"""
                <div class="result-message">
                    <strong>📋 Results:</strong><br><br>{content.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Input form
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form('chat_form', clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            'Ask about your connections data:',
            placeholder="e.g., Show me connections from the past week with duration > 5 minutes",
            label_visibility="collapsed"
        )
    with col2:
        submit = st.form_submit_button('🚀 Send', use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Enhanced form submission handling
if submit and user_input:
    st.session_state.current_conversation.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().isoformat()
    })
    
    with st.spinner('🔮 Generating SQL query...'):
        try:
            raw_sql = sql_gen.nl_to_sql(user_input)
            lines = raw_sql.splitlines()
            clean_lines = [line for line in lines if not line.strip().startswith('```')]
            sql_query = '\n'.join(clean_lines).strip()

            st.session_state.current_conversation.append({
                'role': 'assistant',
                'content': sql_query,
                'timestamp': datetime.now().isoformat()
            })
            
            with st.spinner('⚡ Executing query...'):
                cols, rows = execute_query(sql_query)
                if cols and rows:
                    df = pd.DataFrame(rows, columns=cols)
                    st.session_state.current_conversation.append({
                        'role': 'result',
                        'content': df,
                        'timestamp': datetime.now().isoformat()
                    })
                    st.session_state.query_count += 1
                    st.success(f"✅ Query executed successfully! Found {len(rows)} records.")
                else:
                    st.warning("⚠️ Query executed but returned no results.")
                    st.session_state.current_conversation.append({
                        'role': 'result',
                        'content': "🔍 No results found for your query. Try rephrasing or checking your criteria.",
                        'timestamp': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.session_state.current_conversation.append({
                'role': 'result',
                'content': f"❌ **Error occurred:** {str(e)}\n\nPlease try rephrasing your question or check your query parameters.",
                'timestamp': datetime.now().isoformat()
            })
    
    st.rerun()