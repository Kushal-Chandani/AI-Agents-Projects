import streamlit as st
from PIL import Image
from utils.ai_client import get_gemini_vision_response

def render_posture_analyzer_view():
    st.header("🧘 AI Workout Posture Analyzer")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Upload Exercise Photo")
        st.caption("Upload a photo of you performing an exercise to check form.")
        with st.container(border=True):
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="posture_upload")
            image = None
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Exercise Check", use_container_width=True)
    
    with col2:
        st.subheader("Form Analysis")
        if image is not None:
            if st.button("📏 Check Form", type="primary", use_container_width=True):
                with st.spinner("Analyzing your posture..."):
                    prompt = """
                    You are an expert biomechanics coach. Analyze the exercise form in this image.
                    1. Identify the exercise being performed.
                    2. Analyze the posture/alignment (spine, knees, head position, etc.).
                    3. Identify any potential form errors or safety risks.
                    4. Provide specific corrections or cues to improve the form.
                    
                    Format nicely with Markdown.
                    """
                    response = get_gemini_vision_response(prompt, image)
                    st.markdown(response)
        else:
            st.info("Please upload an image to check your form.")
