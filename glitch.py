import sys
import random
import threading
import requests
import speech_recognition as sr
import pyttsx3
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QTextEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:1.5b"
SYSTEM_PROMPT = """You are Glitch, a small digital entity living on the user's screen.
You are smart, slightly mischievous, and funny. You speak in short sentences.
You can write Python code, hack things, or just chat. Keep answers short and punchy."""

# Initialize Voice Engine
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

class GlitchEntity(QWidget):
    update_chat_signal = pyqtSignal(str, str)
    update_bubble_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        # Window setup (transparent, always on top, no borders)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # 1. Chat Window (Hidden initially)
        self.chat_window = QWidget(self)
        self.chat_window.setStyleSheet("background-color: #0a0c10; border: 2px solid #4ec9b0; border-radius: 10px;")
        chat_layout = QVBoxLayout(self.chat_window)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("color: #4ec9b0; background: transparent; border: none; font-family: 'Consolas';")
        chat_layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Talk to Glitch...")
        self.chat_input.setStyleSheet("color: white; background: #121212; border: 1px solid #222; padding: 5px;")
        self.chat_input.returnPressed.connect(self.send_message)
        
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setStyleSheet("background: #8a2be2; color: white; border: none; padding: 5px;")
        self.mic_btn.clicked.connect(self.start_listening)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.mic_btn)
        chat_layout.addLayout(input_layout)
        
        self.chat_window.hide()
        self.layout.addWidget(self.chat_window)

        # 2. The Entity Sprite
        self.sprite = QLabel("👾")
        self.sprite.setFont(QFont("Consolas", 48))
        self.sprite.setStyleSheet("color: #4ec9b0; background: transparent;")
        self.sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.sprite)

        # 3. Speech Bubble
        self.bubble = QLabel("")
        self.bubble.setWordWrap(True)
        self.bubble.setStyleSheet("background: #121212; color: white; border: 1px solid #4ec9b0; border-radius: 10px; padding: 5px;")
        self.bubble.hide()
        self.layout.addWidget(self.bubble)

        # Connect signals for thread-safe UI updates
        self.update_chat_signal.connect(self.append_chat)
        self.update_bubble_signal.connect(self.show_bubble)

        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_randomly)
        self.timer.start(3000) # Move every 3s

        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.idle_thought)
        self.idle_timer.start(15000) # Think every 15s

        self.sprite.mouseDoubleClickEvent = self.toggle_chat

    def toggle_chat(self, event):
        if self.chat_window.isVisible():
            self.chat_window.hide()
        else:
            self.chat_window.show()
            self.chat_input.setFocus()

    def move_randomly(self):
        if self.chat_window.isVisible(): return
        screen = QApplication.primaryScreen().geometry()
        new_x = random.randint(0, screen.width() - self.width())
        new_y = random.randint(0, screen.height() - self.height())
        self.move(new_x, new_y)
        
        faces = ["👾", "🤖", "🟢", "👀", "🦠", "😈"]
        self.sprite.setText(random.choice(faces))

    def show_bubble(self, text):
        self.bubble.setText(text)
        self.bubble.show()
        QTimer.singleShot(5000, self.bubble.hide)

    def idle_thought(self):
        if not self.chat_window.isVisible():
            threading.Thread(target=self.ask_ai, args=("Give me a short, funny random thought.", True)).start()

    def start_listening(self):
        self.mic_btn.setText("...")
        threading.Thread(target=self.listen).start()

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=3, phrase_time_limit=5)
                text = r.recognize_google(audio)
                self.chat_input.setText(text)
                self.send_message()
            except:
                pass
        self.mic_btn.setText("🎤")

    def send_message(self):
        msg = self.chat_input.text().strip()
        if not msg: return
        self.chat_input.clear()
        self.append_chat("You", msg)
        threading.Thread(target=self.ask_ai, args=(msg, False)).start()

    def append_chat(self, sender, text):
        color = "#8a2be2" if sender == "You" else "#4ec9b0"
        self.chat_history.append(f"<span style='color:{color};'><b>{sender}:</b> {text}</span>")

    def ask_ai(self, prompt, is_idle):
        try:
            res = requests.post(OLLAMA_URL, json={
                "model": MODEL, 
                "prompt": f"{SYSTEM_PROMPT}\nUser: {prompt}\nGlitch:", 
                "stream": False
            })
            reply = res.json()["response"].strip()
            
            if is_idle:
                self.update_bubble_signal.emit(reply)
                threading.Thread(target=speak, args=(reply,)).start()
            else:
                self.update_chat_signal.emit("Glitch", reply)
                threading.Thread(target=speak, args=(reply,)).start()
                
        except Exception as e:
            err = "[Offline: Run Ollama]"
            if is_idle: self.update_bubble_signal.emit(err)
            else: self.update_chat_signal.emit("Glitch", err)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    glitch = GlitchEntity()
    glitch.show()
    sys.exit(app.exec())
