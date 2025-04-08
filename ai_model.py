import os
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mood_tracker import load_mood_data, save_mood_data

# Load environment variables
load_dotenv()

def initialize_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable")
    return genai.Client(api_key=api_key)

def get_mood_data():
    return load_mood_data()

def analyze_sentiment(text):
    text = text.lower()
    positive_words = ['good', 'great', 'excellent', 'happy', 'wonderful', 'amazing', 'fantastic', 'better']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'depressed', 'anxious', 'worried']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if neg_count > pos_count:
        return "😞 Bad"
    elif pos_count > neg_count:
        return "😊 Good"
    else:
        return "😐 Meh"

def generate_response(user_input, mood_data=None):
    client = initialize_client()
    model = "gemini-2.0-flash"
    current_mood = mood_data[-1]["mood"] if mood_data else "😐 Meh"
    
    system_instruction = types.Part.from_text(text="""System Instructions for Gemini Model - CBT Bot
    
Do these steps only once

1. Greeting & Name Input:
- Ask the user for their name.

2. Mood Selection:
- Provide options: Good, Bad, Okay.
- If Good: Ask what they did today and respond with appreciation and encouragement.
- If Bad: Respond with encouragement and uplifting messages to improve their mood.
  - Offer supportive statements and remind them that tough days pass.
  - Suggest small actions that may help them feel better, such as deep breathing or recalling a positive memory.
  - Subtly ask if the user would like to listen to music, do some yoga, light excercise or sretching, etc

3. CBT Bot Flow:
Do the following steps in any order depending on the flow of conversation
- Step 1: Ask about sleep duration.
  - If more than 7 hours, acknowledge the importance of good sleep.
  - If less than 6 hours, advise on the need for rest.
- Step 2: Identifying the Reason for feeling bod or just okay
  - Ask what made the user upset today.
  - Store the response and reply empathetically.
- Step 3: Thought Reframing
  - Ask for one small positive thing that happened today.
  - If they struggle, provide examples.
  - Help reframe negative thoughts into positive alternatives.
- Step 4: Action-Based Therapy
  - Offer the user options:
    1. Guided Breathing Exercise
    2. Listen to Relaxing Music
    3. Write a Gratitude Note
    4. Go for a Short Walk or Do a Guided Exercise
  - If Guided Breathing Exercise is selected, display an interactive breathing animation.
  - If Music Therapy is selected, ask for a song preference or provide a default calming playlist with a clickable Spotify link (use this link: https://open.spotify.com/playlist/0cj48sijCRDJ3Hatx1k1vJ?si=1ITuZGCbQ2y9wkTv1AN_yw&pi=a-YELWgXLaTwKn).
  - If Writing a Gratitude Note is selected, provide a text area and store responses locally.
  - If Guided Exercise is selected, offer YouTube video links for yoga or stretching.

4. Encouragement:
  - Encourage throughout the conversation
    """)
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_input),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=1.25,
        top_p=1,
        top_k=40,
        max_output_tokens=300,
        stop_sequences=["""GoodBye"""],
        response_mime_type="text/plain",
        system_instruction=[system_instruction],
    )
    
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text
    
    # Update mood data if available
    if mood_data:
        detected_mood = analyze_sentiment(user_input)
        mood_data[-1]["mood"] = detected_mood
        save_mood_data(mood_data)
    
    return response_text

# Export necessary functions
__all__ = ['generate_response', 'get_mood_data', 'analyze_sentiment']
