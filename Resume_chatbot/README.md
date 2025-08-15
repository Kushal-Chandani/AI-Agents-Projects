# Resume Chatbot

This project is a personal chatbot designed to be integrated into a personal website. It acts as a digital version of Kushal Chandani, answering questions about his career, background, skills, and experience.

## Features

- **Engaging Persona:** The chatbot is designed to be professional, personable, and approachable, providing context and storytelling rather than just reciting facts.
- **Thinking Tools:** The chatbot uses a set of "thinking tools" to formulate more insightful and human-like responses.
- **Gradio Interface:** The application uses the Gradio library to create a simple and intuitive chat interface.

## Technologies Used

- **Google Gemini:** The core of the chatbot is powered by the `gemini-2.0-flash` model from Google.
- **Gradio:** Used to create the web-based chat interface.
- **PyPDF2:** Used to extract text from the PDF resume.
- **python-dotenv:** Used to manage environment variables.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Kushal-Chandani/AI-Agents-Projects.git
    cd AI-Agents-Projects/Resume_chatbot
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file:**
    Create a `.env` file in the `Resume_chatbot` directory and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

The application will be available at `http://localhost:3000`.
