import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mood_tracker import load_mood_data, save_mood_data
from typing import Optional, Dict, List

# Load environment variables from .env file
load_dotenv()

def initialize_client():
    """Initialize the Google AI client with fallback for development"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # For development/testing, return a mock client
        return MockAIClient()
    return genai.Client(api_key=api_key)

class MockAIClient:
    """Mock client for development when API key is not available"""
    def __init__(self):
        self.models = self.MockModels()

    class MockModels:
        def generate_content_stream(self, model, contents, config):
            """Mock response generator"""
            # Get the user's input from contents
            user_input = next((c.parts[0].text for c in contents if c.role == "user"), "")
            
            # Basic response logic
            if "greeting" in user_input.lower():
                response = "Hey there! How can I call you?"
            elif "name" in user_input.lower():
                response = "Nice to meet you! How are you feeling today?"
            else:
                response = "I understand. Would you like to tell me more about how you're feeling?"
            
            # Yield the response in a format similar to the real API
            class MockResponse:
                def __init__(self, text):
                    self.text = text
            
            yield MockResponse(response)

class CBTState:
    def __init__(self):
        self.current_step = "greeting"
        self.user_name = None
        self.sleep_hours = None
        self.activities = {
            "breathing": "guided_breathing",
            "music": "music_therapy",
            "gratitude": "gratitude_journal",
            "exercise": "guided_exercise"
        }

def get_cbt_prompt(current_step: str, user_name: Optional[str] = None) -> str:
    prompts = {
        "greeting": "Hey there! How can I call you?",
        "name_validation": f"Hey {user_name}, how are you doing today?",
        "sleep": f"How long was your sleep last night, {user_name}?",
        "emotional_exploration": f"What made you upset today, {user_name}?",
        "reframing": "Let's take a step back. What is one small positive thing that happened today?",
        "activities": """
        Now, let's do something to make you feel better! Here are some options:
        
        1. 🧘 Guided Breathing Exercise
        2. 🎵 Listen to Relaxing Music
        3. 📓 Write a Gratitude Note
        4. 🏃 Go for a Short Walk & Check Back
        """
    }
    return prompts.get(current_step, "How are you feeling?")

def get_mood_data():
    return load_mood_data()

def analyze_sentiment(text):
    # Expanded word lists for better mood detection
    positive_words = [
        "happy", "great", "awesome", "wonderful", "excellent", "amazing", "good",
        "better", "best", "love", "loved", "enjoy", "enjoying", "enjoyed",
        "excited", "excitement", "glad", "pleased", "delighted", "grateful",
        "thankful", "blessed", "lucky", "fortunate", "peaceful", "calm", "relaxed"
    ]
    
    negative_words = [
        "sad", "terrible", "awful", "horrible", "bad", "worse", "worst", "hate",
        "hated", "angry", "mad", "upset", "frustrated", "annoyed", "worried",
        "anxious", "stressed", "depressed", "lonely", "tired", "exhausted",
        "overwhelmed", "confused", "disappointed", "hurt", "pain", "suffering"
    ]
    
    text = text.lower()
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "😊 Good"
    elif neg_count > pos_count:
        return "😞 Bad"
    else:
        return "😐 Meh"

def get_mood_suggestions(mood):
    suggestions = {
        "😞 Bad": [
            "Take a few deep breaths and try a quick mindfulness exercise",
            "Go for a short walk or do some gentle stretching",
            "Listen to your favorite uplifting music",
            "Write down three things you're grateful for",
            "Try a quick meditation or relaxation technique"
        ],
        "😐 Meh": [
            "Try a new hobby or activity you've been interested in",
            "Connect with a friend or family member",
            "Do something creative like drawing or writing",
            "Take a break and do something you enjoy",
            "Plan something to look forward to"
        ],
        "😊 Good": [
            "Share your positive energy with others",
            "Document what's making you feel good",
            "Build on this momentum with a small achievement",
            "Practice gratitude for this moment",
            "Plan to maintain this positive state"
        ]
    }
    return suggestions.get(mood, [])

def generate_response(user_input, mood_data=None):
    """Generate response with fallback for development"""
    try:
        client = initialize_client()
        model = "gemini-2.0-flash"

        # Get current mood and suggestions
        current_mood = mood_data[-1]["mood"] if mood_data else "😐 Meh"
        mood_suggestions = get_mood_suggestions(current_mood)

        # Prepare the system prompt for conversational style
        system_prompt = f"""You are a supportive CBT chatbot designed for emotion and mood tracking, primarily for women during their monthly phases. Follow these guidelines:
        1. Keep responses short and concise (2-3 sentences max)
        2. Be empathetic and supportive - offer comfort when appropriate
        3. Use a friendly, conversational tone
        4. Focus on the user's current feelings and experiences
        5. Balance between asking questions and providing comfort
        6. Use the mood data to personalize your responses
        7. When offering comfort:
           - Validate their feelings
           - Share a brief encouraging message
           - Offer a gentle suggestion if appropriate
        8. End with either a follow-up question or a supportive statement
        9. Include one of these mood-improving suggestions when relevant:
           {', '.join(mood_suggestions)}
        10. Adapt your tone based on the user's current mood: {current_mood}"""

        # Prepare the conversation context
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=system_prompt)],
            ),
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            )
        ]

        # Add mood data to the context if available
        if mood_data:
            mood_summary = "Here's the user's recent mood data:\n"
            for entry in mood_data[-3:]:  # Use the last 3 mood entries
                mood_summary += (
                    f"Date: {entry['date']}, Mood: {entry['mood']}, "
                    f"Stress: {entry['stress']}, Water: {entry['water']}, "
                    f"Energy: {entry['energy']}\n"
                )
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=mood_summary)],
                )
            )

        # Generate content configuration
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=150,
            response_mime_type="text/plain",
        )

        # If using mock client, handle the response differently
        if isinstance(client, MockAIClient):
            response = ""
            for chunk in client.models.generate_content_stream(
                model="mock-model",
                contents=contents,
                config=generate_content_config,
            ):
                response += chunk.text
            return response

        # Generate the bot's response
        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response += chunk.text

        # Analyze sentiment and update mood data
        detected_mood = analyze_sentiment(user_input)
        if mood_data:
            mood_data[-1]["mood"] = detected_mood
            save_mood_data(mood_data)

        return response

    except Exception as e:
        # Fallback response if something goes wrong
        return "I'm here to help! Would you like to tell me how you're feeling?"
