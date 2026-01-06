import streamlit as st

def get_default_profile(key, default_val):
    """Retrieve a value from the user profile in session state, or return default."""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    return st.session_state.user_profile.get(key, default_val)

def update_profile(data):
    """Update user profile in session state."""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    st.session_state.user_profile.update(data)
