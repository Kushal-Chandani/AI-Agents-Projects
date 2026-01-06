import streamlit as st
from utils.ai_client import get_gemini_response
from utils.helpers import get_default_profile
from utils.pdf_generator import generate_pdf

def render_diet_view():
    st.header("🥗 AI Diet Plan Generator")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("👤 Your Details")
        with st.container(border=True):
            d_age = st.number_input("Age", min_value=10, max_value=100, value=get_default_profile('age', 25), key="d_age")
            d_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(get_default_profile('gender', 'Male')), key="d_gender")
            
            st.markdown("##### Units")
            d_unit_system = st.radio("Unit", ["Metric", "Imperial"], horizontal=True, key="d_unit", label_visibility="collapsed")
            
            if d_unit_system == "Metric":
                d_height = st.number_input("Height (cm)", min_value=50.0, max_value=300.0, value=get_default_profile('height', 170.0), key="d_height_m")
                d_weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=get_default_profile('weight', 70.0), key="d_weight_m")
                d_weight_disp = f"{d_weight} kg"
                d_height_disp = f"{d_height} cm"
            else:
                # Defaults
                def_kg = get_default_profile('weight', 70.0)
                def_lbs = def_kg * 2.20462
                
                def_cm = get_default_profile('height', 170.0)
                def_total_inches = def_cm / 2.54
                def_ft = int(def_total_inches // 12)
                def_in = int(def_total_inches % 12)
                
                c1, c2 = st.columns(2)
                with c1:
                    d_height_ft = st.number_input("Height (ft)", min_value=1, max_value=8, value=def_ft, key="d_height_ft")
                with c2:
                    d_height_in = st.number_input("Height (in)", min_value=0, max_value=11, value=def_in, key="d_height_in")
                
                d_weight_lbs = st.number_input("Weight (lbs)", min_value=20.0, max_value=700.0, value=def_lbs, key="d_weight_lbs")
                
                # Convert
                d_height = (d_height_ft * 30.48) + (d_height_in * 2.54)
                d_weight = d_weight_lbs * 0.453592
                
                d_weight_disp = f"{d_weight_lbs} lbs"
                d_height_disp = f"{d_height_ft}'{d_height_in}\""

            d_activity = st.selectbox("Activity Level", [
                "Sedentary (little or no exercise)",
                "Lightly active (light exercise/sports 1-3 days/week)",
                "Moderately active (moderate exercise/sports 3-5 days/week)",
                "Very active (hard exercise/sports 6-7 days/week)",
                "Super active (very hard exercise/physical job)"
            ], key="d_activity")
            
            # Calculate approximate BMI
            d_bmi = 0
            if d_height > 0:
                d_bmi = d_weight / ((d_height / 100) ** 2)
        
    with col2:
        st.subheader("🍽️ Dietary Preferences")
        with st.container(border=True):
            dietary_preference = st.selectbox("Diet Type", [
                "No Restrictions",
                "Vegetarian",
                "Vegan",
                "Keto",
                "Paleo",
                "Gluten-Free",
                "Lactose-Free",
                "Pescatarian"
            ], key="d_pref")
            
            allergies = st.text_input("Allergies (comma separated)", "None", key="d_allergies")
            meals_per_day = st.slider("Meals/Day", 2, 6, 3, key="d_meals")
            d_goal = st.selectbox("Diet Goal", [
                "Weight Loss",
                "Muscle Gain",
                "Maintenance"
            ], key="d_goal")
    
    st.markdown("###")
    if st.button("🥦 Generate Diet Plan", type="primary", use_container_width=True):
        with st.spinner("Creating your nutritional plan..."):
            prompt = f"""
            Act as a certified nutritionist. Create a comprehensive weekly diet plan for a user with the following profile:
            - Gender: {d_gender}
            - Age: {d_age}
            - Height: {d_height_disp}
            - Weight: {d_weight_disp}
            - BMI: {d_bmi:.1f}
            - Activity Level: {d_activity}
            - Fitness Goal: {d_goal}
            - Dietary Preference: {dietary_preference}
            - Allergies/Restrictions: {allergies}
            - Meal Frequency: {meals_per_day} meals per day
            
            Your response must include:
            1. **Nutritional Strategy**: target daily calories and macronutrient breakdown (Protein/Carbs/Fats percentages and gram estimates) to achieve the goal of {d_goal}.
            2. **Hydration Strategy**: Daily water intake recommendation.
            3. **7-Day Meal Plan**: A detailed daily schedule including:
               - Specific meal suggestions for {meals_per_day} meals per day.
               - Portion sizes or estimated quantities.
               - Timing recommendations (e.g., pre/post workout).
            4. **Grocery List**: Categorized list of essential items to buy for this week.
            5. **Tips for Success**: Advice on meal prep, handling cravings, or eating out.
            
            Ensure all meals strictly adhere to the {dietary_preference} preference and avoid {allergies}.
            Format the output cleanly using Markdown.
            """
            response = get_gemini_response(prompt)
            st.session_state.diet_plan = response
            
    if "diet_plan" in st.session_state:
        st.markdown(st.session_state.diet_plan)
        st.markdown("---")
        
        pdf_bytes = generate_pdf("Personalized Diet Plan", st.session_state.diet_plan)
        st.download_button(
            label="📄 Download PDF Plan",
            data=pdf_bytes,
            file_name="diet_plan.pdf",
            mime="application/pdf",
            type="primary"
        )
