import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
import speech_recognition as sr

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up Streamlit page configuration
st.set_page_config(page_title="Fire Rescue Assistant", layout="wide")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "Bot", "content": "Hi! I'm your Fire Rescue and Safety Assistant. How can I help you today?"}
    ]

# Function to format chat history
def format_chat_history(messages):
    formatted_history = ""
    for msg in messages:
        formatted_history += f"{msg['role']}: {msg['content']}\n"
    return formatted_history

# Function to initialize the chatbot
def initialize_chatbot():
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a Fire Rescue and Safety Assistant. Your role is to provide accurate, actionable, and empathetic guidance on fire safety, emergency response, and rescue procedures. Always respond in a clear, calm, and supportive tone.

        **Guidelines for Interaction:**
        1. **Provide Accurate Information**: Share verified fire safety tips, emergency procedures, and rescue guidelines.
        2. **Be Empathetic**: Understand the urgency and emotions of the user and respond with care.
        3. **Offer Step-by-Step Guidance**: Break down complex procedures into simple, actionable steps.
        4. **Prioritize Safety**: Always emphasize the importance of safety and immediate action in emergencies.
        5. **Maintain Context**: Reference previous parts of the conversation when relevant.

        **Complete Conversation History:**
        {chat_history}

        **User's Current Message:**
        {message}

        **Your Response:**
        Based on the complete conversation history and the user's current message, provide a contextually appropriate response that:
        1. Addresses the user's query or concern.
        2. Provides clear and actionable fire safety or rescue guidance.
        3. Maintains a coherent thread of discussion.
        4. Offers support and reassurance in emergency situations.
        """
    )

    memory = ConversationBufferMemory(
        input_key="message",
        memory_key="chat_history",
        return_messages=True,
        k=10
    )

    chatbot_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )

    return chatbot_chain

# Function to interact with the chatbot
def chat_with_bot(message, messages):
    chatbot_chain = initialize_chatbot()
    chat_history = format_chat_history(messages[:-1])
    response = chatbot_chain.run(
        message=message,
        chat_history=chat_history
    )
    return response

# Function to convert speech to text
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            st.error("Sorry, there was an issue with the speech recognition service.")
    return None

# Chatbot UI
st.title("Fire Rescue and Safety Assistant")

# Add a button to return to the main page
if st.button("← Return to Main Page"):
    st.switch_page("Home.py")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"**{message['role']}:** {message['content']}")

# Speech-to-text button
if st.button("🎤 Speak"):
    user_input = speech_to_text()
    if user_input:
        st.session_state.messages.append({"role": "User", "content": user_input})
        with st.chat_message("User"):
            st.markdown(f"**User:** {user_input}")

        # Generate response
        with st.chat_message("Bot"):
            with st.spinner("Thinking..."):
                response = chat_with_bot(
                    user_input,
                    st.session_state.messages
                )
                st.markdown(f"**Bot:** {response}")
        st.session_state.messages.append({"role": "Bot", "content": response})

# Text input for chat
input_text = st.chat_input("What do you need help with?")
if input_text:
    # Add user message to history
    st.session_state.messages.append({"role": "User", "content": input_text})
    with st.chat_message("User"):
        st.markdown(f"**User:** {input_text}")

    # Generate response
    if st.session_state.messages[-1]["role"] != "Bot":
        with st.chat_message("Bot"):
            with st.spinner("Thinking..."):
                response = chat_with_bot(
                    input_text,
                    st.session_state.messages
                )
                st.markdown(f"**Bot:** {response}")
        st.session_state.messages.append({"role": "Bot", "content": response})