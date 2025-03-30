# OpenTranslator

OpenTranslator is a real-time, browser-based voice chat and translation app that supports multilingual messaging and speech using Flask and Web APIs.

---

## 📦 Features
- Two-way voice and text messaging
- Translation and Text-to-Speech with per-user language preference
- Real-time auto-playback of translated messages
- Message queueing with persistent history
- Multi-channel support (0–9)
- Fully browser-based frontend

---

## 🛠 Installation Guide

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/opentranslator.git
cd opentranslator
```

### 2. Set Up Python Environment
We recommend using `venv`:
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
```

### 3. Install Required Python Libraries
```bash
pip install -r requirements.txt
```
If you're not using `requirements.txt`, install manually:
```bash
pip install Flask gTTS pydub SpeechRecognition translators
```

### 4. Install ffmpeg
Required by `pydub` to convert between audio formats.

- **macOS** (with Homebrew):
```bash
brew install ffmpeg
```
- **Ubuntu/Debian**:
```bash
sudo apt install ffmpeg
```
- **Windows**:
Download from https://ffmpeg.org/download.html and add it to your PATH.

### 5. Install ngrok (Optional for Public URL)
Go to: https://ngrok.com/download

Once installed:
```bash
ngrok config add-authtoken <YOUR_NGROK_AUTH_TOKEN>
ngrok http 5050
```
This will expose your Flask server (running on port 5050) to a public URL.

---

## 🚀 Run the App

### Start the Flask server:
```bash
python app.py
```

### Open the App
Go to `http://localhost:5050/` or your public ngrok URL.

---

## 📂 Folder Structure
```
project/
├── app.py
├── frontend.html
├── history/                # Contains saved .wav and .txt files
├── static/                 # Not used anymore unless needed for fallback
├── README.md
└── requirements.txt        # Optional, for easy dependency install
```

---

## ✅ Dependencies Summary
- Flask (API server)
- gTTS (Text-to-Speech)
- pydub (Audio conversion)
- ffmpeg (Required for pydub)
- SpeechRecognition (for audio transcription)
- translators (for translation)
- ngrok (optional public URL tunneling)

---

## 👥 Multi-user & Multi-channel
- Each user (`user1`, `user2`) can choose a language
- Each channel (`0`–`9`) keeps its own queues
- Messages are translated and saved per user per channel with timestamped filenames

---

## 🧪 Want to Contribute?
Feel free to submit a pull request or log issues!

---

## 🧠 Made with 💡 by [Your Name]
For demo or collaboration, contact you@example.com

