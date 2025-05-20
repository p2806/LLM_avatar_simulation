from ollama_serve import *
from feedback import *
from database_connection import *
from patients import *
import ollama
from openai import OpenAI
import librosa
import numpy as np
import atexit, string
from gtts import gTTS
import speech_recognition as sre
from flask import Flask,render_template,request,send_file,jsonify,redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import ffmpeg as ffmpeg
import re
import subprocess,random
import requests,json


app=Flask(__name__)

start_ollama_server()
atexit.register(kill_ollama)


@app.route("/")
def home():
  return render_template("index.html")
@app.route("/video") 
def video():
  return render_template("video.html")
@app.route("/patients")
def patients():
  return render_template("patients.html")
@app.route("/login")
def login():
  return render_template("login.html")
@app.route("/signup")
def signup():
  return render_template("signup.html")
@app.route("/audio") 
def audio():
  return render_template("audio.html")
@app.route("/feedback")
def feedback():
   return render_template("feedback.html")
@app.route("/pastconv")
def pastconv():
   conversations = get_conversation_feedback(user_id)
   if conversations:
        return render_template("conversation.html", conversations=conversations)
   else:
        return render_template("conversation.html", message="No conversation yet")
   
client = OpenAI(api_key = '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')


messages = []
use_case ='dummy'
user_id = 123
conversation_id = 123
@app.route("/login", methods=['POST'])
def user_login():
   data = request.get_json()
   username= data.get("username")
   password = data.get("password")
   response = verify_user(username,password)
   global user_id
   user_id = response
   if response != 0:
      return "Login Successful"
@app.route("/signup", methods=['POST'])
def user_signup():
   data = request.get_json()
   username= data.get("username")
   password = data.get("password")
   response = create_user(username,password)
   global user_id
   user_id = response.inserted_id
   if response.acknowledged:
        return jsonify({"message": "Data inserted successfully!", "inserted_id": str(response.inserted_id)}), 201
   else:
        return jsonify({"message": "Data insertion failed!"}), 500
@app.route("/liked", methods=['POST'])
def user_feedback():
   data = request.get_json()
   liked = data.get("liked")

   response = add_field_to_user(user_id,conversation_id,liked)
   if response == 'Field added successfully.':
      return response
   else:
      return "network error"
@app.route("/comment", methods=['POST'])
def comment():
   data = request.get_json()
   comment = data.get("comment")

   response = add_comment_to_user(user_id,conversation_id,comment)
   if response == 'Field added successfully.':
      return response
   else:
      return "network error"
@app.route("/set-case", methods=['POST'])
def set_case():
   data = request.get_json()
   global use_case
   use_case = data.get("case_name")
   return "Success"

   
@app.route("/save-video", methods=['POST'])
def save_video():
    if 'video' not in request.files:
        return "No video file part", 400
    file = request.files['video']
    if file.filename == '':
        return "No selected file", 400
    if file:
        file.save('uploaded_video.webm')

   
    ffmpeg_path = r'/opt/homebrew/bin/ffmpeg'
    command=[ffmpeg_path,'-y','-i','uploaded_video.webm','-acodec','pcm_s16le','-q:a','0','-map','a','audio.wav']
    result = subprocess.run(command,check=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    
    global messages
    if not messages:
        global conversation_id
        conversation_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        #audio_file = video_to_audio('uploaded_video.webm', 'audio.wav')
        #content = 'Summarize this in **15 or less words**:[You are a patient role-playing scenario for the purpose of training nursing students. As a patient, you should ask for a variety of things that require the nursing student to say \'no\'. Do not take on the role of a nurse or provide medical advice. Instead, insist or ask in different ways if your request is declined, while maintaining a realistic patient perspective. Dont stick too rigidly to the script. If they ask questions, respond in a realistic way, but bring the conversation back to your request.]';
        #vcontent = '[IMPORTANT:You are a persistent difficult PATIENT approaching nurse, requesting denied items realistically without medical advice.Behave like a patient who is talking to a nurse and put them in a critical situation.Be precise with the question, be more human, organic and natural. Be precise in asking questions. Ask question in 15 words. Donot ask all at a time make it feel like a conversation. **DO NOT ALWAYS ASK ABOUT MEDICATIONS ASK DIFFERENTLY EVERYTIME**. Build a conversation in such a way that Nurse asks questions****MAKE NURSE ASK RIGHT QUESTINS***]';
        global use_case
        if use_case == "Eleanor":
           content = elenorthompson()
        elif use_case == "Marcus":
           content = MarcusJohnson()
        elif use_case == "sophia":
           content = SophiaPatel()
        else:
           content = other()
        messages = [
        {"role": "system", "content":content}
        ]
        #finalrequest= exampleclinical()
        '''messages.append(
                {"role": "user", "content": finalrequest},
            )'''
    

    audio_path = open('audio.wav', "rb")
    #audio_file_path = '/Users/shiva/Desktop/Project/audio.wav'
    recognizer = sre.Recognizer()
    with sre.AudioFile("audio.wav") as source:
        audio_data = recognizer.record(source)  # Read entire file
        text = recognizer.recognize_google(audio_data)
    messages.append(
            {"role": "user", "content": text},
        )
    chat = client.chat.completions.create(
            model="gpt-4o", messages= messages,temperature=0.7
        )
    reply = chat.choices[0].message.content
   
    '''response = ollama.chat(model="llama3", messages=messages, options={"temperature": 0.8})
    reply = response['message']['content']'''
    messages.append({"role": "assistant", "content": reply})
    print(reply)
    #speech_file_path = 'outputaudio.wav'
    tts = gTTS(text=reply, lang='en')
    tts.save("outputaudio.mp3")

   # creating an avatar video
    
    '''url = "http://192.168.0.101:5000/generate-video"

    data = {"text":reply}
    response = requests.post(url,json=data, timeout=60)

    if response.status_code == 200:
        with open('avatarvideov1.mp4','wb') as f:
            f.write(response.content)
    else:
        print(response.json())
    
    return send_file('avatarvideov1.mp4', as_attachment=True)'''
    return send_file('outputaudio.mp3', as_attachment=True)

# generate feedback method
@app.route("/generate-feedback", methods=['POST'])
def generate_feedback():
   #print(messages)
   global messages
   global use_case
   conversation_input = messages
   messages = []
   use_case = "dummy"

   role_to_speaker = {
    'system': None,          # System messages are not part of the conversation
    'user': 'Nursing Student',
    'assistant': 'Patient'
   }
   exchanges = []
   for message in conversation_input:
     speaker = role_to_speaker.get(message['role'])
     if speaker:  # Ignore 'system' messages
        exchanges.append({
            "speaker": speaker,
            "content": message['content']
        })
   output = {
    "exchanges": exchanges
    }
   print(output)
   def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

   transcript = output
   correct_answers = read_file("correct_answers.txt")
   speechmetrics= analyze_audio('audio.wav') 

    # Define Socratic feedback prompt
   reply = final_evaluation(transcript,speechmetrics,client)

    # Generate feedback using OpenAI
   '''response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )'''

# Print or save feedback
   print(reply)
   '''feedback = {
        "clarity": "The responses were clear and concise, but additional examples could improve understanding.",
        "accuracy": "The answers demonstrated a good understanding of the key concepts, but one response missed a critical detail about medication dosage.",
        "depth_of_reasoning": "Some responses provided sufficient reasoning, but others lacked a detailed explanation of cause and effect.",
        "relevance": "All responses stayed on topic and addressed the questions, which helped maintain the flow of conversation.",
        "tone": "The tone was empathetic and professional, which contributed to a positive patient experience."
    }'''
   
   print(user_id)
   messages_str = json.dumps(transcript, indent=4)
   if (user_id!=123):
        add_conversation_feedback(user_id,conversation_id,messages_str,reply)
   return {
    "reply": reply,
    "user_id": user_id,
    "conversation_id": conversation_id
        }, 200, {'Content-Type': 'application/json'}

def analyze_audio(audio_path):
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)
    
    # Volume Analysis (RMS Energy)
    rms = librosa.feature.rms(y=y)[0]
    avg_volume = np.mean(rms)
    
    # Pitch Analysis (Fundamental Frequency)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitches = pitches[magnitudes > np.median(magnitudes)]
    avg_pitch = np.mean(pitches) if len(pitches) > 0 else 0

    # Speech Rate (Words per Minute)
    recognizer = sre.Recognizer()
    with sre.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    words = text.split()
    duration_sec = librosa.get_duration(y=y, sr=sr)
    wpm = len(words) / (duration_sec / 60)

    # Pause Analysis (Silences)
    silence_threshold = np.percentile(rms, 10)  # 10% as threshold
    silence_frames = rms < silence_threshold
    pause_count = np.sum(silence_frames)
    metrics = {
        "volume": round(avg_volume,2),
        "pitch": round(avg_pitch,2),
        "words_per_minute": round(wpm,2),
        "pauses": round(pause_count,2)}

    return metrics



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 