import streamlit as st
from utils.ai_client import get_gemini_response
from utils.helpers import get_default_profile
from utils.pdf_generator import generate_pdf

def render_workout_view():
    st.header("🏋️ AI Workout Routine Generator")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("👤 Your Details")
        with st.container(border=True):
            w_age = st.number_input("Age", min_value=10, max_value=100, value=get_default_profile('age', 25), key="w_age")
            w_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(get_default_profile('gender', 'Male')), key="w_gender")
            
            st.markdown("##### Weight Unit")
            w_unit_system = st.radio("Unit", ["Metric", "Imperial"], horizontal=True, key="w_unit", label_visibility="collapsed")
            
            if w_unit_system == "Metric":
                w_weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=get_default_profile('weight', 70.0), key="w_weight_m")
                w_weight_disp = f"{w_weight} kg"
            else:
                def_kg = get_default_profile('weight', 70.0)
                def_lbs = def_kg * 2.20462
                w_weight_lbs = st.number_input("Weight (lbs)", min_value=20.0, max_value=700.0, value=def_lbs, key="w_weight_lbs")
                # Conversion for prompt only, logic uses display string
                w_weight = w_weight_lbs * 0.453592
                w_weight_disp = f"{w_weight_lbs} lbs"

            w_activity = st.selectbox("Activity Level", [
                "Sedentary (little or no exercise)",
                "Lightly active (light exercise/sports 1-3 days/week)",
                "Moderately active (moderate exercise/sports 3-5 days/week)",
                "Very active (hard exercise/sports 6-7 days/week)",
                "Super active (very hard exercise/physical job)"
            ], index=0, key="w_activity")
        
    with col2:
        st.subheader("⚙️ Preferences")
        with st.container(border=True):
            fitness_goal = st.selectbox("Fitness Goal", [
                "Weight Loss",
                "Muscle Gain",
                "Endurance Improvement",
                "General Fitness",
                "Flexibility"
            ], key="w_goal")
            
            equipment = st.multiselect("Available Equipment", [
                "None (Bodyweight)",
                "Dumbbells",
                "Barbell",
                "Resistance Bands",
                "Gym Machines",
                "Yoga Mat"
            ], default=["None (Bodyweight)"], key="w_equip")
            
            col_d, col_dur = st.columns(2)
            with col_d:
                days_per_week = st.slider("Days/Week", 1, 7, 3, key="w_days")
            with col_dur:
                duration_mins = st.slider("Mins/Session", 15, 120, 45, key="w_duration")
    
    st.markdown("###")
    if st.button("🚀 Generate Workout Plan", type="primary", use_container_width=True):
        with st.spinner("Generating your personalized workout plan..."):
            prompt = f"""
            Act as an expert personal trainer. Create a highly detailed and personalized {days_per_week}-day weekly workout routine for a user with the following profile:
            - Gender: {w_gender}
            - Age: {w_age}
            - Weight: {w_weight_disp}
            - Activity Level: {w_activity}
            - Primary Goal: {fitness_goal}
            - Equipment Available: {', '.join(equipment)}
            - Session Duration: {duration_mins} minutes per session
            
            Your response must include:
            1. **Executive Summary**: A brief explanation of the training philosophy for this specific user.
            2. **Weekly Schedule**: Overview of split (e.g., Push/Pull/Legs, Upper/Lower, Full Body) including rest days.
            3. **Detailed Workout Sessions**: For each workout day, provide:
               - **Warm-up**: Specific dynamic stretches or light cardio with duration.
               - **Main Workout**: List exercises with:
                 - Sets and Reps (or duration).
                 - Rest intervals between sets.
                 - Form cues/tips for key movements.
               - **Cool-down**: Static stretches.
            4. **Progression Strategy**: How to increase difficulty over time (progressive overload).
            5. **Recovery Advice**: Tips for rest days tailored to their goal.
            
            Format the output cleanly using Markdown with bold headers, bullet points, and tables where appropriate.
            """
            response = get_gemini_response(prompt)
            st.session_state.workout_plan = response
            
    if "workout_plan" in st.session_state:
        st.markdown(st.session_state.workout_plan)
        st.markdown("---")
        
        # PDF Generation
        pdf_bytes = generate_pdf("Personalized Workout Plan", st.session_state.workout_plan)
        st.download_button(
            label="📄 Download PDF Plan",
            data=pdf_bytes,
            file_name="workout_plan.pdf",
            mime="application/pdf",
            type="primary"
        )
