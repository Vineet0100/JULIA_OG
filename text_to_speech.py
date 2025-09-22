import pyttsx3
import re
import threading
import keyboard   # pip install keyboard

engine = pyttsx3.init()
voices = engine.getProperty('voices')
if len(voices) > 2:   # ensure index exists
    engine.setProperty('voice', voices[2].id)  # female voice
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

stop_flag = False

def clean_text(text):
    """Remove unwanted symbols and normalize text."""
    text = re.sub(r'[*_#`]', '', text)
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def text_to_speech(text):
    """Speak text in main thread, interruptible with stop_flag."""
    global stop_flag
    stop_flag = False
    text = clean_text(text)
    sentences = text.split('. ')
    for sentence in sentences:
        if stop_flag:
            break
        engine.say(sentence)
        engine.runAndWait()

def stop_speech():
    """Stop ongoing speech immediately."""
    global stop_flag
    stop_flag = True
    engine.stop()

def esc_listener():
    """Background thread: listens for Esc key to stop speech."""
    while True:
        keyboard.wait("esc")
        print("\n⛔ ESC pressed: Speech stopped.")
        stop_speech()

# Start ESC listener in background
threading.Thread(target=esc_listener, daemon=True).start()
