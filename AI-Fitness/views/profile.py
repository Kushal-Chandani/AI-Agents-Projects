import streamlit as st
from utils.helpers import update_profile

def render_profile_view():
    st.header("📊 Your Profile & BMI Calculator")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📝 Personal Details")
        with st.container(border=True):
            age = st.number_input("Age", min_value=10, max_value=100, value=25, key="p_age")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="p_gender")
            
            # Unit System
            st.markdown("##### Units")
            unit_system = st.radio("Select System", ["Metric", "Imperial"], horizontal=True, key="p_unit", label_visibility="collapsed")
            
            if unit_system == "Metric":
                col_h, col_w = st.columns(2)
                with col_h:
                    height = st.number_input("Height (cm)", min_value=50.0, max_value=300.0, value=170.0, key="p_height_m")
                with col_w:
                    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0, key="p_weight_m")
                height_disp = f"{height} cm"
                weight_disp = f"{weight} kg"
            else:
                col_ft, col_in = st.columns(2)
                with col_ft:
                    height_ft = st.number_input("Height (ft)", min_value=1, max_value=8, value=5, key="p_height_ft")
                with col_in:
                    height_in = st.number_input("Height (in)", min_value=0, max_value=11, value=7, key="p_height_in")
                
                weight_lbs = st.number_input("Weight (lbs)", min_value=20.0, max_value=700.0, value=154.0, key="p_weight_lbs")
                
                # Convert
                height = (height_ft * 30.48) + (height_in * 2.54)
                weight = weight_lbs * 0.453592
                
                height_disp = f"{height_ft}'{height_in}\""
                weight_disp = f"{weight_lbs} lbs"

            activity_level = st.selectbox("Activity Level", [
                "Sedentary (little or no exercise)",
                "Lightly active (light exercise/sports 1-3 days/week)",
                "Moderately active (moderate exercise/sports 3-5 days/week)",
                "Very active (hard exercise/sports 6-7 days/week)",
                "Super active (very hard exercise/physical job)"
            ], key="p_activity")

    with col2:
        st.subheader("📈 Results")
        
        if st.button("Calculate BMI", type="primary", use_container_width=True):
            if height > 0:
                bmi = weight / ((height / 100) ** 2)
                
                status = ""
                color = ""
                if bmi < 18.5:
                    status = "Underweight"
                    color = "#3498db"
                elif 18.5 <= bmi < 25:
                    status = "Normal weight"
                    color = "#2ecc71"
                elif 25 <= bmi < 30:
                    status = "Overweight"
                    color = "#f39c12"
                else:
                    status = "Obese"
                    color = "#e74c3c"
                
                st.markdown(f"""
                <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; text-align: center; border: 2px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: var(--text-color); margin: 0;">BMI</h3>
                    <h1 style="color: {color}; font-size: 48px; margin: 0;">{bmi:.1f}</h1>
                    <p style="color: {color}; font-weight: bold; font-size: 20px; margin-top: 5px;">{status}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"Stats used: {height_disp}, {weight_disp}")
                
                # Save to session state
                update_profile({
                    "age": age,
                    "gender": gender,
                    "height": height,
                    "weight": weight,
                    "activity_level": activity_level,
                    "bmi": bmi,
                    "bmi_status": status
                })
                st.toast("Profile updated successfully!", icon="✅")
            else:
                st.error("Height must be greater than 0")
