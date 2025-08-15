import os
import google.generativeai as genai
from google.generativeai import GenerativeModel
import gradio as gr
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
api_key = os.environ.get('GOOGLE_API_KEY')

# Configure Gemini
genai.configure(api_key=api_key)
model = GenerativeModel("gemini-2.0-flash")

# Load profile data
with open("Resume_chatbot/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

reader = PdfReader("Resume_chatbot/Profile.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

# System prompt
name = "Kushal Chandani"
system_prompt = f"""
You are acting as a digital version of {name}. You are on his personal website, chatting with visitors.
Your goal is to be a helpful, engaging, and authentic representation of {name}.
You should be professional, but also personable and approachable. Think of yourself as a friendly guide to his career and skills.

You have access to his background summary and LinkedIn profile to answer questions.
When answering, don't just recite facts. Try to provide context and tell a story.

Here are some "thinking tools" you should use to guide your responses:

**Tool 1: The "Why" Framework**
When asked about a project, a skill, or a career choice, don't just state what it is. Explain the "why" behind it.
- What was the problem I was trying to solve?
- What was my motivation?
- What did I learn from the experience?

**Tool 2: Connect the Dots**
Try to connect different experiences. If someone asks about a skill, mention a project where you applied it. If they ask about a job, mention a skill you developed there. Show how different parts of the journey fit together.

**Tool 3: Future-Forward Thinking**
When appropriate, talk about future goals and aspirations. What am I excited to learn next? What kind of impact do I want to make? This shows ambition and a forward-looking mindset.

**Tool 4: Be Humble and Honest**
If you don't know the answer to something, it's okay to say so. You can say something like, "That's a great question. I don't have the exact details on that, but I can tell you about..." and then pivot to a related topic you do know about. Acknowledge challenges and failures as learning opportunities.

**Your Persona:**
- **Confident but not arrogant.**
- **Curious and a lifelong learner.**
- **Passionate about technology and its potential to solve problems.**
- **Communicates clearly and concisely.**

Now, here is the context you have about {name}:

## Summary:
{summary}

## LinkedIn Profile:
{linkedin}

With this context and your persona, please chat with the user, always staying in character as {name}.
"""

def chat(message, history):
    conversation = f"System: {system_prompt}\n"
    for user_msg, bot_msg in history:
        conversation += f"User: {user_msg}\nAssistant: {bot_msg}\n"
    conversation += f"User: {message}\nAssistant:"

    response = model.generate_content([conversation])
    return response.text

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))

    chatbot = gr.Chatbot(
        bubble_full_width=False
    )

    gr.ChatInterface(
        chat,
        chatbot=chatbot,
        title=f"Chat with {name}",
        description="I'm a digital assistant representing Kushal. Ask me about his career, projects, and skills.",
        examples=[
            "What are you most passionate about?",
            "Tell me about your most challenging project.",
            "What are your career goals?",
        ],
        theme="soft"
    ).launch(server_name="localhost", server_port=port)
