import streamlit as st
from ai_model import generate_response, get_mood_data
from mood_tracker import save_mood_data, load_mood_data

def analyze_sentiment(text):
    text = text.lower()
    # Positive words
    positive_words = ['good', 'great', 'excellent', 'happy', 'wonderful', 'amazing', 'fantastic', 'better', 'fine', 'okay', 'alright']
    # Negative words
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'depressed', 'anxious', 'worried', 'upset', 'angry', 'frustrated']
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    # Determine mood
    if negative_count > positive_count:
        return "😞 Bad"
    elif positive_count > negative_count:
        return "😊 Good"
    else:
        return "😐 Meh"

# CBT Chatbot Page
def cbt_chatbot_page():
    # Set page title and styling
    st.title("💬 CBT Chatbot")
    st.markdown(
        """
        <style>
            /* Main background */
            .stApp {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            
            /* Chat messages */
            .stChatMessage {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #404040;
            }
            
            /* User message specific styling */
            .stChatMessage[data-testid="userChatMessage"] {
                background-color: #1e3a8a;
                border: 1px solid #2563eb;
            }
            
            /* Assistant message specific styling */
            .stChatMessage[data-testid="assistantChatMessage"] {
                background-color: #2d2d2d;
                border: 1px solid #404040;
            }
            
            /* Chat input area */
            .stChatInput {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #404040;
            }
            
            /* Input text area */
            .stTextInput > div > div > input {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
            }
            
            /* Send button */
            .stChatInput button {
                background-color: #2563eb;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
                border: none;
            }
            
            /* Send button hover */
            .stChatInput button:hover {
                background-color: #1d4ed8;
            }
            
            /* Title color */
            h1 {
                color: #ffffff;
            }
            
            /* Markdown text color */
            .stMarkdown {
                color: #ffffff;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Get mood data
    mood_data = get_mood_data()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Chat input
    if prompt := st.chat_input("How are you feeling today?"):
        # Display user message
        with st.chat_message('user'):
            st.markdown(prompt)
        
        # Store user message
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        # Generate and display bot response
        with st.chat_message('assistant'):
            bot_response = generate_response(prompt, mood_data)
            st.markdown(bot_response)
        
        # Store bot response
        st.session_state.messages.append({'role': 'assistant', 'content': bot_response})

        # Analyze sentiment and update mood tracker
        detected_mood = analyze_sentiment(prompt)
        mood_data = load_mood_data()
        if mood_data:
            mood_data[-1]["mood"] = detected_mood
            save_mood_data(mood_data)