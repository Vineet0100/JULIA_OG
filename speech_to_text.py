import pyttsx3
import re
import speech_recognition as sr

engine = pyttsx3.init()
voices = engine.getProperty('voices')
if len(voices) > 2:
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
    """Speak text, interruptible by stop_speech()."""
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


def listen_to_voice():
    """Listen to user voice and return recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Speak now")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            query = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {query}")
            return query
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected.")
            return None
        except sr.UnknownValueError:
            print("❌ Sorry, I didn't catch that.")
            return None
        except sr.RequestError:
            print("⚠️ Could not connect to speech recognition service.")
            return None
