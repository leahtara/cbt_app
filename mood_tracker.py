import streamlit as st
import datetime
import json
import os

def create_selection(value, max_value, icon):
    return icon * value + "⚪" * (max_value - value)

def load_mood_data():
    try:
        if os.path.exists('mood_data.json'):
            with open('mood_data.json', 'r') as f:
                content = f.read().strip()
                if not content:  # If file is empty
                    return []
                return json.loads(content)
        return []
    except json.JSONDecodeError:
        # If file is corrupted, delete it and return empty list
        if os.path.exists('mood_data.json'):
            os.remove('mood_data.json')
        return []
    except Exception as e:
        st.error(f"Error loading mood data: {e}")
        return []

def save_mood_data(data):
    try:
        with open('mood_data.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Error saving mood data: {e}")

def clear_mood_history():
    try:
        if os.path.exists('mood_data.json'):
            os.remove('mood_data.json')
        st.session_state.clear()
        # Create a completely empty data structure
        save_mood_data([])
        st.success("Mood history cleared successfully! ✨")
    except Exception as e:
        st.error(f"Error clearing mood history: {e}")

def update_mood():
    mood_data = load_mood_data()
    if mood_data:
        mood_data[-1]["mood"] = st.session_state.mood_radio
        save_mood_data(mood_data)

# Mood Tracker Page
def mood_tracker_page():
    # Initialize session state for mood if it doesn't exist
    if 'mood_radio' not in st.session_state:
        st.session_state.mood_radio = "😐 Meh"

    st.markdown(
        """
        <style>
            body {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            .mood-option {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .mood-option:hover {
                border-color: #2563eb;
                transform: translateY(-2px);
            }
            .mood-option.selected {
                background-color: #1e3a8a;
                border-color: #2563eb;
            }
            .stButton>button {
                background-color: #2563eb;
                color: white;
                border-radius: 10px;
                padding: 10px;
                border: none;
            }
            .stButton>button:hover {
                background-color: #1d4ed8;
            }
            .mood-history {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #404040;
            }
            /* Style for radio buttons */
            .stRadio > div {
                display: flex;
                justify-content: space-between;
                gap: 10px;
            }
            .stRadio > div > div {
                flex: 1;
                text-align: center;
            }
            .stRadio > div > div > div {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                transition: all 0.3s ease;
            }
            .stRadio > div > div > div:hover {
                border-color: #2563eb;
                transform: translateY(-2px);
            }
            .stRadio > div > div > div[data-testid="stRadio"] {
                background-color: #1e3a8a;
                border-color: #2563eb;
            }
            /* Style for clear history button */
            .clear-history-btn {
                background-color: #dc2626 !important;
            }
            .clear-history-btn:hover {
                background-color: #b91c1c !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📒 Mood Tracker Journal")

    # Get the latest mood from chat data
    mood_data = load_mood_data()

    # Mood selection using radio buttons with callback
    st.radio(
        "How are you feeling?",
        ["😊 Good", "😐 Meh", "😞 Bad"],
        horizontal=True,
        key="mood_radio",
        on_change=update_mood
    )

    # Stress, Water, Energy Inputs using selectable icons
    st.write("**Stress Level:**")
    stress_level = st.select_slider(
        "Stress Level", 
        options=list(range(0, 11)),
        value=5,
        format_func=lambda x: create_selection(x, 10, "⚡")
    )
    
    st.write("**Water Intake:**")
    water_intake = st.select_slider(
        "Water Intake", 
        options=list(range(0, 11)),
        value=5,
        format_func=lambda x: create_selection(x, 10, "🥤")
    )
    
    st.write("**Energy Level:**")
    energy_level = st.select_slider(
        "Energy Level", 
        options=list(range(0, 11)),
        value=5,
        format_func=lambda x: create_selection(x, 10, "🔋")
    )

    # Submit Mood Entry
    if st.button("Save Entry"):
        # Create a new entry
        new_entry = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mood": st.session_state.mood_radio,
            "stress": stress_level,
            "water": water_intake,
            "energy": energy_level
        }
        mood_data.append(new_entry)
        save_mood_data(mood_data)
        st.success("Mood logged successfully! ✅")

    # Show Past Entries with improved styling
    st.subheader("📊 Your Mood History")
    if mood_data:
        for entry in reversed(mood_data[-5:]):  # Show last 5 entries
            st.markdown(
                f"""
                <div class="mood-history">
                    <strong>{entry['date']}</strong><br>
                    Mood: {entry['mood']}<br>
                    ⚡{create_selection(entry['stress'], 10, '⚡')}<br>
                    🥤{create_selection(entry['water'], 10, '🥤')}<br>
                    🔋{create_selection(entry['energy'], 10, '🔋')}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.write("No mood records yet. Start tracking today!")

    # Add clear history button at the bottom
    st.markdown("---")  # Add a separator line
    if st.button("🗑️ Clear All History", key="clear_history", help="This will delete all your mood history and start fresh", use_container_width=True):
        clear_mood_history()
        st.rerun()