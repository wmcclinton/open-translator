from flask import Flask, request, jsonify, render_template_string
from collections import defaultdict, deque
import translators as ts
from gtts import gTTS
from pydub import AudioSegment
import os
import speech_recognition as sr
from datetime import datetime

from flask import send_from_directory

app = Flask(__name__)

# Channel data: queues and language prefs
channels = defaultdict(lambda: {
    'user1': deque(),
    'user2': deque(),
    'user1_lang': 'ru',
    'user2_lang': 'ru'
})
counters = defaultdict(lambda: {
    'user1_sent': 0,
    'user2_sent': 0,
    'user1_recv': 0,
    'user2_recv': 0
})

HISTORY_DIR = os.path.join(app.root_path, 'history')
os.makedirs(HISTORY_DIR, exist_ok=True)

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def wav_to_text(wav_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Speech recognition error: {e}"

def text_to_wav(text, filename, lang='ru'):
    tts = gTTS(text, lang=lang)
    tts.save("temp.mp3")
    sound = AudioSegment.from_mp3("temp.mp3")
    sound.export(filename, format="wav")

def translate(text, target_lang='ru'):
    try:
        return ts.translate_text(text, to_language=target_lang)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

@app.route('/')
def index():
    return render_template_string(open("frontend.html").read())

@app.route('/history/<path:filename>')
def serve_history_file(filename):
    return send_from_directory('history', filename)

@app.route('/enqueue', methods=['POST'])
def enqueue():
    data = request.get_json()
    sender = data.get('user')
    message = data.get('message')
    channel = data.get('channel', '0')

    if sender not in ['user1', 'user2'] or not message or channel not in map(str, range(10)):
        return jsonify({'error': 'Invalid input'}), 400

    recipient = 'user2' if sender == 'user1' else 'user1'
    lang = channels[channel][f'{recipient}_lang']
    translated_message = translate(message, lang)
    channels[channel][recipient].append(translated_message)
    counters[channel][f'{sender}_sent'] += 1
    counters[channel][f'{recipient}_recv'] += 1

    ts_id = timestamp()
    wav_path = os.path.join(HISTORY_DIR, f'{channel}_{recipient}_{ts_id}.wav')
    text_to_wav(translated_message, filename=wav_path, lang=lang)

    with open(os.path.join(HISTORY_DIR, f'{channel}_{sender}_{ts_id}_original.txt'), 'w') as f:
        f.write(message)
    with open(os.path.join(HISTORY_DIR, f'{channel}_{recipient}_{ts_id}_translated.txt'), 'w') as f:
        f.write(translated_message)

    return jsonify({
        'status': 'Message queued',
        'sent': counters[channel][f'{sender}_sent'],
        'recv': counters[channel][f'{sender}_recv']
    })

@app.route('/dequeue/<user>/<channel>', methods=['GET'])
def dequeue(user, channel):
    if user not in ['user1', 'user2'] or channel not in map(str, range(10)):
        return jsonify({'error': 'Invalid user or channel'}), 400
    if not channels[channel][user]:
        return jsonify({
            'message': None,
            'status': 'Queue is empty',
            'sent': counters[channel][f'{user}_sent'],
            'recv': counters[channel][f'{user}_recv'],
            'queue_size': len(channels[channel][user])
        }), 200
    message = channels[channel][user].popleft()
    return jsonify({
        'message': message,
        'sent': counters[channel][f'{user}_sent'],
        'recv': counters[channel][f'{user}_recv'],
        'queue_size': len(channels[channel][user])
    }), 200

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    audio_file = request.files.get('audio')
    user = request.form.get('user')
    channel = request.form.get('channel', '0')

    if not audio_file or user not in ['user1', 'user2'] or channel not in map(str, range(10)):
        return {'status': 'error', 'message': 'Bad request'}, 400

    ts_id = timestamp()
    input_path = os.path.join(HISTORY_DIR, f'{channel}_{user}_{ts_id}.webm')
    wav_path = os.path.join(HISTORY_DIR, f'{channel}_{user}_{ts_id}.wav')
    audio_file.save(input_path)

    audio = AudioSegment.from_file(input_path)
    audio.export(wav_path, format="wav")

    transcription = wav_to_text(wav_path)
    recipient = 'user2' if user == 'user1' else 'user1'
    lang = channels[channel][f'{recipient}_lang']
    translated = translate(transcription, lang)

    channels[channel][recipient].append(translated)
    counters[channel][f'{user}_sent'] += 1
    counters[channel][f'{recipient}_recv'] += 1

    translated_wav_path = os.path.join(HISTORY_DIR, f'{channel}_{recipient}_{ts_id}_translated.wav')
    text_to_wav(translated, translated_wav_path, lang=lang)

    with open(os.path.join(HISTORY_DIR, f'{channel}_{user}_{ts_id}_original.txt'), 'w') as f:
        f.write(transcription)
    with open(os.path.join(HISTORY_DIR, f'{channel}_{recipient}_{ts_id}_translated.txt'), 'w') as f:
        f.write(translated)

    return jsonify({
        'status': 'success',
        'original_text': transcription,
        'translated_text': translated
    })

@app.route('/set_language', methods=['POST'])
def set_language():
    data = request.get_json()
    user = data.get('user')
    lang = data.get('lang')
    channel = data.get('channel', '0')

    if user not in ['user1', 'user2'] or not lang or channel not in map(str, range(10)):
        return jsonify({'error': 'Invalid input'}), 400

    channels[channel][f'{user}_lang'] = lang
    return jsonify({'status': f'{user} language set to {lang}'})

@app.route('/set_audio', methods=['POST'])
def set_audio():
    data = request.get_json()
    user = data.get('user')
    lang = data.get('lang')
    channel = data.get('channel', '0')
    msg = data.get('message')

    if user not in ['user1', 'user2'] or not lang or channel not in map(str, range(10)):
        return jsonify({'error': 'Invalid input'}), 400

    translated_wav_path = os.path.join(HISTORY_DIR, f'{channel}_{user}_translated.wav')
    text_to_wav(msg, translated_wav_path, lang=lang)
    return jsonify({'status': f'saved to {translated_wav_path}'})

@app.route('/status/<user>/<channel>', methods=['GET'])
def get_status(user, channel):
    if user not in ['user1', 'user2'] or channel not in map(str, range(10)):
        return jsonify({'error': 'Invalid input'}), 400

    queue_size = len(channels[channel][user])
    sent = counters[channel][f'{user}_sent']
    recv = counters[channel][f'{user}_recv']

    return jsonify({
        'queue_size': queue_size,
        'sent': sent,
        'recv': recv
    })

if __name__ == '__main__':
    app.run(debug=True, port=5050)