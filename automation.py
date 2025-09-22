import subprocess
import os
import webbrowser

# -------------------- Open VS Code --------------------
def open_vs_code():
    vscode_path = r"C:\Users\vinee\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    if os.path.exists(vscode_path):
        subprocess.Popen([vscode_path])
        return "Opening VS Code..."
    else:
        return "VS Code not found! Check the path."

# -------------------- Open Notepad --------------------
def open_notepad():
    try:
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad..."
    except FileNotFoundError:
        return "Notepad not found!"

# -------------------- Open Calculator --------------------
def open_calculator():
    try:
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator..."
    except FileNotFoundError:
        return "Calculator not found!"

# -------------------- Open Folder --------------------
def open_folder(path):
    if os.path.exists(path):
        os.startfile(path)
        return f"Opening folder: {path}"
    else:
        return f"Folder not found: {path}"

# -------------------- Open YouTube --------------------
def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube..."

# -------------------- Open Google --------------------
def open_google():
    webbrowser.open("https://www.google.com")
    return "Opening Google..."
