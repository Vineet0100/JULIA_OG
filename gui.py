import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from speech_to_text import listen_to_voice, text_to_speech
import threading

class JuliaGUI:
    def __init__(self, root, gif_path="julia_face.gif"):
        self.root = root
        self.root.title("Julia AI")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # Load GIF
        self.gif = Image.open(gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(self.gif)]
        self.frame_index = 0

        self.label_img = tk.Label(root)
        self.label_img.pack(pady=20)
        self.animate_gif()  # Start GIF animation

        # Response box
        self.response_box = tk.Text(root, height=10, width=50, wrap='word')
        self.response_box.pack(pady=10)

        # Start Listening button
        self.listen_button = tk.Button(root, text="Speak to Julia", command=self.start_listening)
        self.listen_button.pack(pady=10)

    def animate_gif(self):
        self.label_img.configure(image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.root.after(100, self.animate_gif)  # Adjust 100ms for speed

    def start_listening(self):
        threading.Thread(target=self.listen_and_reply).start()

    def listen_and_reply(self):
        self.response_box.insert(tk.END, "🎤 Listening...\n")
        self.response_box.see(tk.END)
        user_query = listen_to_voice()
        if user_query:
            self.response_box.insert(tk.END, f"🗣️ You said: {user_query}\n")
            self.response_box.see(tk.END)
            # Replace with your main logic (Gemini or automation)
            reply = f"Julia says: {user_query[::-1]}"  # Temporary: reversed text
            self.response_box.insert(tk.END, f"{reply}\n")
            self.response_box.see(tk.END)
            text_to_speech(reply)

if __name__ == "__main__":
    root = tk.Tk()
    gui = JuliaGUI(root, gif_path="julia_face.gif")  # Your GIF file here
    root.mainloop()
