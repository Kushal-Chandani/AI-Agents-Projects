# 💪 AI Fitness Planner

An all-in-one AI-powered health and fitness companion built with **Streamlit** and **Google Gemini AI**.

## 🌟 Features

- **📊 Profile & BMI Calculator**: Calculate BMI, handle Metric/Imperial units, and personalize your experience.
- **🏋️ AI Workout Generator**: Create personalized weekly workout routines based on your goals, equipment, and schedule.
- **🥗 AI Diet Planner**: Generate detailed weekly meal plans with macros, grocery lists, and recipes tailored to your dietary preferences.
- **💬 Personal Trainer Chatbot**: 24/7 AI assistant to answer all your fitness and nutrition questions.
- **📸 AI Meal Analyzer**: Upload a photo of your food to get an instant breakdown of calories, macros, and healthiness.
- **🧘 Posture Analyzer**: Upload a photo/video of your exercise form to get safety checks and correction cues.
- **📄 PDF Export**: Download your workout and diet plans as PDF files.
- **🌙 Light/Dark Mode**: Beautiful, responsive UI with theme support.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.5 Flash
- **PDF Generation**: FPDF
- **Image Processing**: Pillow

## 🚀 Setup & Installation

1.  **Clone the repository** (if you haven't already).
2.  **Navigate to the project directory**:
    ```bash
    cd AI-Fitness
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up Environment Variables**:
    -   Create a `.env` file in the `AI-Fitness` directory.
    -   Add your Google Gemini API Key:
        ```env
        GEMINI_API_KEY=your_api_key_here
        ```
    -   *Note: You can get a free API key from [Google AI Studio](https://aistudio.google.com/).*

5.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## 📂 Project Structure

-   `app.py`: Main application entry point.
-   `views/`: Contains UI logic for each feature (Profile, Workout, Diet, Chat, Vision).
-   `utils/`: Helper functions for AI, PDF generation, and common logic.
-   `requirements.txt`: Python dependencies.

## ⚠️ Notes

-   Ensure you have a stable internet connection for AI generation.
-   The vision features (Meal/Posture) require the `gemini-2.5-flash` model which is multimodal.
