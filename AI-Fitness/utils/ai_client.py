import google.generativeai as genai
import os
import streamlit as st
from PIL import Image

def configure_genai():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        genai.configure(api_key=api_key)
        return True
    return False

def get_gemini_response(prompt):
    if not configure_genai():
         return "⚠️ **Error:** Gemini API Key not found or invalid. Please set a valid `GEMINI_API_KEY` in the `.env` file."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **Error:** {str(e)}"

def get_gemini_chat_response(history, user_input):
    """
    history: List of dicts matching Gemini format [{'role': 'user'|'model', 'parts': [text]}]
    """
    if not configure_genai():
        return "⚠️ Please configure your API Key first."
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        chat = model.start_chat(history=history)
        response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        return f"⚠️ **Error:** {str(e)}"

def get_gemini_vision_response(prompt, image):
    if not configure_genai():
        return "⚠️ Please configure your API Key first."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"⚠️ **Error:** {str(e)}"
