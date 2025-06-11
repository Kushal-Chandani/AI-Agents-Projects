import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from chat_agent import run_chat_agent
from dashboard_agent import run_dashboard_agent

load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dashboard_html" not in st.session_state:
    st.session_state.dashboard_html = ""

st.title("AI-Powered Database Dashboard")

# Create tabs
tab1, tab2 = st.tabs(["Chatbot", "Dashboard"])

# Chatbot Tab
with tab1:
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    user_query = st.chat_input("Ask a question about the database (e.g., 'Show total revenue by category')")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)
        
        with st.spinner("Fetching response..."):
            try:
                response = asyncio.run(run_chat_agent(user_query))
                st.session_state.messages.append({"role": "assistant", "content": response})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(response)
            except Exception as e:
                st.error(f"Error: {e}")

# Dashboard Tab
with tab2:
    st.header("Database Dashboard")
    if st.button("Generate Dashboard"):
        with st.spinner("Generating dashboard..."):
            try:
                html = asyncio.run(run_dashboard_agent("Analyze my database and suggest a dashboard"))
                st.session_state.dashboard_html = html
                st.html(html)  # Removed height parameter
            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.session_state.dashboard_html:
        st.download_button(
            label="Download Dashboard HTML",
            data=st.session_state.dashboard_html,
            file_name="dashboard.html",
            mime="text/html"
        )