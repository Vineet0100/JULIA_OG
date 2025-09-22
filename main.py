import google.generativeai as genai
from config import GEMINI_API_KEY
from speech_to_text import listen_to_voice, text_to_speech, stop_speech
from persona import JULIA_INFO, USER_INFO, JULIA_TRAITS, JULIA_CATCHPHRASES
from automation import (
    open_vs_code,
    open_notepad,
    open_calculator,
    open_folder,
    open_youtube,
    open_google
)
import random
import time
from pynput import keyboard


# === ESC key handler ===
def on_key_press(key):
    try:
        if key == keyboard.Key.esc:
            print("⏹️ Speech stopped by ESC")
            stop_speech()
    except Exception as e:
        print(f"Keyboard listener error: {e}")


def init_gemini():
    """Initialize Gemini model with API key."""
    print(f"🔑 Using API Key: {GEMINI_API_KEY[:6]}********")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


# Keep model as a global for reuse
model = None


def handle_input(user_query: str) -> str:
    """Main entry point for both GUI and voice mode."""
    global model
    if model is None:
        model = init_gemini()

    query_lower = user_query.lower()

    # Exit command
    if "goodbye" in query_lower or "bye" in query_lower:
        farewell_messages = [
            "Goodbye! Talk to you soon!",
            "See you later, Vineet!",
            "Bye! Stay curious!",
            "It was nice chatting with you!"
        ]
        reply = random.choice(farewell_messages)

    # Persona responses
    elif "who are you" in query_lower or "about you" in query_lower:
        reply = JULIA_INFO
    elif "about me" in query_lower or "who am i" in query_lower:
        reply = USER_INFO

    # Automation commands
    elif "open vs code" in query_lower:
        reply = "Automation mode: " + open_vs_code()
    elif "open notepad" in query_lower:
        reply = "Automation mode: " + open_notepad()
    elif "open calculator" in query_lower or "calculate" in query_lower:
        reply = "Automation mode: " + open_calculator()
    elif "open folder" in query_lower:
        folder = user_query.lower().replace("open folder", "").strip()
        reply = "Automation mode: " + open_folder(folder)
    elif "open youtube" in query_lower:
        reply = "Automation mode: " + open_youtube()
    elif "open google" in query_lower:
        reply = "Automation mode: " + open_google()

    # General queries sent to Gemini AI
    else:
        reply = "Gemini mode: " + ask_gemini(model, user_query)

    # Add a fun trait or catchphrase randomly
    if random.random() < 0.5:  # 50% chance to add a fun trait
        reply += " " + random.choice(JULIA_TRAITS)
    if random.random() < 0.5:  # 50% chance to add a catchphrase
        reply += " " + random.choice(JULIA_CATCHPHRASES)

    return reply


def ask_gemini(model, query):
    """Send query to Gemini and return response text."""
    response = model.generate_content(query)
    return response.text


if __name__ == "__main__":
    print("🚀 Julia is starting...")
    model = init_gemini()

    # Start keyboard listener for Esc key
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    while True:
        user_query = listen_to_voice()
        if not user_query:
            continue

        reply = handle_input(user_query)

        print(f"Julia: {reply}")
        text_to_speech(reply)

        if "goodbye" in user_query.lower() or "bye" in user_query.lower():
            time.sleep(1)  # Let speech finish unless Esc is pressed
            break
