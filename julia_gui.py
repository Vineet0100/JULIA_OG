import sys
import os
import random
import time
import threading
import queue
import asyncio
import tempfile
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextBrowser, QVBoxLayout
from PyQt5.QtGui import QMovie, QFont, QKeyEvent
from PyQt5.QtCore import Qt, pyqtSignal

# Julia brain imports
import google.generativeai as genai
from config import GEMINI_API_KEY
from persona import JULIA_INFO, USER_INFO, JULIA_TRAITS, JULIA_CATCHPHRASES
from automation import (
    open_vs_code, open_notepad, open_calculator,
    open_folder, open_youtube, open_google
)
from speech_to_text import listen_to_voice, stop_speech

# Edge TTS streaming
import edge_tts
import simpleaudio as sa
import io

# === Gemini Setup ===
def init_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(model, query):
    try:
        response = model.generate_content(query)
        text = getattr(response, "text", None)
        if not text or text.strip() == "":
            return "Hmm, I couldn't generate a response."
        return text.strip()
    except Exception as e:
        return f"Sorry, I had trouble thinking: {str(e)}"

# === Julia GUI ===
class JuliaWindow(QWidget):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Julia — Voice GUI")
        self.showMaximized()
        self.stop_flag = False
        self.listening_line_index = None

        self._setup_ui()
        self.log_signal.connect(self.append_log)
        self.status_signal.connect(self.update_status)

        self.tts_queue = queue.Queue()
        threading.Thread(target=self._tts_worker, daemon=True).start()
        threading.Thread(target=self.julia_loop, daemon=True).start()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        if os.path.exists("julia_anim.gif"):
            self.movie = QMovie("julia_anim.gif")
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.gif_label.setText("(GIF not found)")
        layout.addWidget(self.gif_label, stretch=8)

        self.terminal = QTextBrowser()
        mono = QFont("Courier New")
        mono.setPointSize(10)
        self.terminal.setFont(mono)
        self.terminal.setFixedHeight(200)
        self.terminal.setStyleSheet("background-color: #111; color: #eee; padding: 6px;")
        layout.addWidget(self.terminal, stretch=2)
        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.status_signal.emit("⏹️ ESC pressed: stopping speech...")
            self.stop_flag = True
            stop_speech()
            while not self.tts_queue.empty():
                try:
                    self.tts_queue.get_nowait()
                except queue.Empty:
                    break

    def append_log(self, text):
        self.terminal.append(text)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def update_status(self, text):
        if self.listening_line_index is None:
            self.terminal.append(text)
            self.listening_line_index = self.terminal.document().blockCount() - 1
        else:
            cursor = self.terminal.textCursor()
            cursor.movePosition(cursor.Start)
            for _ in range(self.listening_line_index):
                cursor.movePosition(cursor.Down)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(text)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    # === TTS Worker using Edge TTS streaming directly ===
    def speak_async(self, text: str):
        self.tts_queue.put(text)

    def _tts_worker(self):
        while True:
            text = self.tts_queue.get()
            if text is None:
                break
            self.stop_flag = False
            asyncio.run(self._play_tts_stream(text))

    async def _play_tts_stream(self, text):
        communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        stream = await communicate.stream()
        audio_data = bytearray()
        async for chunk in stream:
            if self.stop_flag:
                return
            if isinstance(chunk, dict) and chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
        if audio_data:
            # Play via simpleaudio
            wave_obj = sa.WaveObject(audio_data, 1, 2, 22050)
            play_obj = wave_obj.play()
            while play_obj.is_playing():
                if self.stop_flag:
                    play_obj.stop()
                    break
                time.sleep(0.05)

    # === Julia Loop ===
    def julia_loop(self):
        self.log_signal.emit("🚀 Julia is starting...")
        time.sleep(0.5)
        self.status_signal.emit("🎧 Julia is listening... (say something)")

        while True:
            self.stop_flag = False
            self.status_signal.emit("🎤 Listening...")
            user_query = listen_to_voice()
            if not user_query:
                continue

            self.listening_line_index = None
            self.log_signal.emit(f"👤 You: {user_query}")
            reply = self.julia_process(user_query)
            self.log_signal.emit(f"🤖 Julia: {reply}\n")
            self.speak_async(reply)

            if "goodbye" in user_query.lower() or "bye" in user_query.lower():
                break

    def julia_process(self, user_query: str) -> str:
        q = user_query.lower()
        if "goodbye" in q or "bye" in q:
            return "Goodbye! Talk to you soon!"
        elif "who are you" in q or "about you" in q:
            reply = JULIA_INFO
        elif "about me" in q or "who am i" in q:
            reply = USER_INFO
        elif "open vs code" in q:
            reply = "Automation mode: " + open_vs_code()
        elif "open notepad" in q:
            reply = "Automation mode: " + open_notepad()
        elif "open calculator" in q or "calculate" in q:
            reply = "Automation mode: " + open_calculator()
        elif "open folder" in q:
            folder = user_query.lower().replace("open folder", "").strip()
            reply = "Automation mode: " + open_folder(folder)
        elif "open youtube" in q:
            reply = "Automation mode: " + open_youtube()
        elif "open google" in q:
            reply = "Automation mode: " + open_google()
        else:
            reply = ask_gemini(self.model, user_query)

        if random.random() < 0.5:
            reply += " " + random.choice(JULIA_TRAITS)
        if random.random() < 0.5:
            reply += " " + random.choice(JULIA_CATCHPHRASES)
        return reply

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = init_gemini()
    win = JuliaWindow(model)
    win.show()
    sys.exit(app.exec_())
