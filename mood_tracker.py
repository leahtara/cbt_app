import streamlit as st
import datetime
import json
import os
from datetime import datetime, timedelta

# Helper function to create selection icons
def create_selection(value, max_value, icon):
    return icon * value + "⚪" * (max_value - value)

# Load mood data from JSON file
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
        if os.path.exists('mood_data.json'):
            os.remove('mood_data.json')
        return []
    except Exception as e:
        st.error(f"Error loading mood data: {e}")
        return []

# Save mood data to JSON file
def save_mood_data(data):
    try:
        with open('mood_data.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Error saving mood data: {e}")

# Clear mood history
def clear_mood_history():
    try:
        if os.path.exists('mood_data.json'):
            os.remove('mood_data.json')
        st.session_state.clear()
        save_mood_data([])
        st.success("Mood history cleared successfully! ✨")
    except Exception as e:
        st.error(f"Error clearing mood history: {e}")

# Update mood in session state
def update_mood():
    mood_data = load_mood_data()
    if mood_data:
        mood_data[-1]["mood"] = st.session_state.mood_radio
        save_mood_data(mood_data)

# Mood Tracker Page
def mood_tracker_page():
    if 'mood_radio' not in st.session_state:
        st.session_state.mood_radio = "😐 Meh"

    mood_data = load_mood_data()

    # Mood Calendar Section
    st.subheader("📅 Mood Calendar")
    mood_colors = {
        "😞 Bad": "#FFCCCB",
        "😐 Meh": "#ADD8E6",
        "😊 Good": "#FFB6C1",
        "😄 Great": "#FFFF99",
    }

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    st.write(f"### {today.strftime('%B %Y')}")
    first_day_of_month = datetime(current_year, current_month, 1)
    num_days_in_month = (datetime(current_year, current_month + 1, 1) - timedelta(days=1)).day

    # Calendar Grid
    cols = st.columns(7)
    for i, col in enumerate(cols):
        col.write(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i])

    day_counter = 1
    for week in range(6):
        cols = st.columns(7)
        for i, col in enumerate(cols):
            if (week == 0 and i < first_day_of_month.weekday()) or day_counter > num_days_in_month:
                col.write("")
            else:
                date_str = datetime(current_year, current_month, day_counter).strftime("%Y-%m-%d")
                mood_for_day = None
                for entry in mood_data:
                    if entry["date"].startswith(date_str):
                        mood_for_day = entry["mood"]
                        break

                bg_color = mood_colors.get(mood_for_day, "#FFFFFF")
                
                col.markdown(
                    f'<div style="background-color: {bg_color}; border-radius: 5px; padding: 10px; text-align: center; color: #555555; font-weight: bold;">{day_counter}</div>',
                    unsafe_allow_html=True
                )
                day_counter += 1

    # Mood Selection
    st.radio(
        "How are you feeling?",
        ["😞 Bad", "😐 Meh", "😊 Good", "😄 Great"],
        horizontal=True,
        key="mood_radio",
        on_change=update_mood
    )

    # Metric Sliders
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

    # Save Entry
    if st.button("Save Entry"):
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mood": st.session_state.mood_radio,
            "stress": stress_level,
            "water": water_intake,
            "energy": energy_level
        }
        mood_data.append(new_entry)
        save_mood_data(mood_data)
        st.success("Mood logged successfully! ✅")

    # History Section
    st.subheader("📊 Your Mood History")
    if mood_data:
        for entry in reversed(mood_data[-5:]):
            st.markdown(
                f"""
                <div style="background-color: #2d2d2d; border-radius: 10px; padding: 15px; margin: 10px 0; border: 1px solid #404040;">
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

    # Clear History
    st.markdown("---")
    if st.button("🗑️ Clear All History", key="clear_history"):
        clear_mood_history()
        st.rerun()

if __name__ == "__main__":
    mood_tracker_page()
