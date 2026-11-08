
# 👾 Glitch-Buster OS

A cross-platform digital entity. Glitch is a self-moving, AI-powered companion that lives on your desktop.

## 💻 Native App (Python)
The Python version runs natively on Windows, macOS, and Linux. It creates a transparent overlay on your desktop, allowing Glitch to float around your screen like a living creature.

### Prerequisites
1. Install Python 3.8+
2. Install **Ollama** (for the AI brain): [ollama.com](https://ollama.com)
3. Pull the model:
   ```bash
   ollama run qwen2.5-coder:1.5b
   ```

### Installation
Clone the repository and install the required libraries:
```bash
pip install PyQt6 pyttsx3 SpeechRecognition pyaudio requests
```
*(Note: If `pyaudio` fails on Windows, use `pipwin install pyaudio`. On Mac, use `brew install portaudio` first).*

### Usage
Run the script:
```bash
python glitch.py
```

## Features
- **Autonomous Movement:** Glitch wanders around your screen every 3 seconds.
- **Voice AI:** Double-click the entity to open a chat window. Click the 🎤 to talk. Glitch will reply out loud.
- **Local Inference:** Connects to your local Ollama instance. No internet required, no API keys, completely private.
- **Fake OS Interface:** Includes a fully functional HTML terminal simulation in the web version.

Built by OnyxSoul.
and i don't do anything for anyhacking or something is  you and i made it ! and be good
```
