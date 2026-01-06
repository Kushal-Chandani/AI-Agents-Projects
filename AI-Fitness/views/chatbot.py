import streamlit as st
from utils.ai_client import get_gemini_chat_response

def render_chatbot_view():
    st.header("💬 AI Personal Trainer")
    st.markdown("---")

    # Initialize chat history for Streamlit UI
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Initialize history for Gemini API
    if "gemini_history" not in st.session_state:
        st.session_state.gemini_history = []
        # Add system prompt
        persona = "You are an expert personal trainer and nutritionist. Be encouraging, concise, and helpful."
        st.session_state.gemini_history.append({'role': 'user', 'parts': [persona]})
        st.session_state.gemini_history.append({'role': 'model', 'parts': ["Understood. I am ready to help!"]})

    # Display chat messages from UI history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about fitness or diet..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to UI history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Get response
        with st.spinner("Thinking..."):
            # Pass ONLY the gemini history
            response = get_gemini_chat_response(st.session_state.gemini_history, prompt)
            
            # Update Gemini history after success (handled by API call usually returns text, but we need to update state manually for next turn)
            # Note: start_chat returns a chat object that maintains history. 
            # But get_gemini_chat_response re-inits chat with history list. 
            # We must append the NEW interaction to our local history list.
            
            st.session_state.gemini_history.append({'role': 'user', 'parts': [prompt]})
            st.session_state.gemini_history.append({'role': 'model', 'parts': [response]})
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Add to UI history
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
