import streamlit as st
from PIL import Image
from utils.ai_client import get_gemini_vision_response

def render_meal_analyzer_view():
    st.header("📸 AI Meal Analyzer")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Upload Meal Photo")
        with st.container(border=True):
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            image = None
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Meal", use_container_width=True)
    
    with col2:
        st.subheader("Analysis Results")
        if image is not None:
            if st.button("🔍 Analyze Nutrition", type="primary", use_container_width=True):
                with st.spinner("Analyzing your meal..."):
                    prompt = """
                    You are an expert nutritionist. Analyze the food in this image.
                    Provide a detailed breakdown including:
                    1. Identification of food items.
                    2. Estimated Portion Size.
                    3. Total Calories (approximate).
                    4. Macronutrients (Protein, Carbs, Fats).
                    5. Healthiness rating (1-10) and brief explanation.
                    
                    Format nicely with Markdown.
                    """
                    response = get_gemini_vision_response(prompt, image)
                    st.markdown(response)
        else:
            st.info("Please upload an image to start analysis.")
