from openai import OpenAI
from ollama_serve import *
import ollama
import librosa
import numpy as np
import atexit
from gtts import gTTS
import speech_recognition as sre
from flask import Flask,render_template,request,send_file,send_from_directory,url_for,jsonify
import ffmpeg as ffmpeg
import re
import subprocess,random
import json
import requests, jsonify,json


app=Flask(__name__)

start_ollama_server()
atexit.register(kill_ollama)


@app.route("/")
def home():
  return render_template("indexaudio.html")
@app.route("/audio") 
def audio():
  return render_template("audio.html")
@app.route("/feedback")
def feedback():
   return render_template("feedback.html")


messages = []
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
        
        #audio_file = video_to_audio('uploaded_video.webm', 'audio.wav')
        #content = 'Summarize this in **15 or less words**:[You are a patient role-playing scenario for the purpose of training nursing students. As a patient, you should ask for a variety of things that require the nursing student to say \'no\'. Do not take on the role of a nurse or provide medical advice. Instead, insist or ask in different ways if your request is declined, while maintaining a realistic patient perspective. Dont stick too rigidly to the script. If they ask questions, respond in a realistic way, but bring the conversation back to your request.]';
        content = '[IMPORTANT:You are a persistent difficult PATIENT approaching nurse, requesting denied items realistically without medical advice.Behave like a patient who is talking to a nurse and put them in a critical situation.Be precise with the question, be more human, organic and natural. Be precise in asking questions. Ask question in 15 words. Donot ask all at a time make it feel like a conversation]';
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
    response = ollama.chat(model="llama3", messages=messages, options={"temperature": 0.8})
    reply = response['message']['content']
    messages.append({"role": "assistant", "content": reply})
    print(reply)
    #speech_file_path = 'outputaudio.wav'
    tts = gTTS(text=reply, lang='en')
    tts.save("outputaudio.mp3")

   # creating an avatar video
    
    ''' url = "http://192.168.0.102:5000/generate-video"

    data = {"text":reply}
    response = requests.post(url,json=data, timeout=60)

    if response.status_code == 200:
        with open('avatarvideov1.mp4','wb') as f:
            f.write(response.content)
    else:
        print(response.json())'''
    
    return send_file('outputaudio.mp3', as_attachment=True)

# generate feedback method
@app.route("/generate-feedback", methods=['POST'])
def generate_feedback():
   #print(messages)
   global messages
   conversation_input = messages
   messages = []
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
   prompt = f"""
    IMPORTANT: Please analyse the below transcript carefully and give the feedback for "NUSRING STUDENT" based on the below metrics
    Analyse NURSING STUDENTS response for the patients questions. Focus on NURSING STUDENSTS RESPONSES in the below transcript.
    
    Transcript:
    {transcript}

    You are an AI tasked with evaluating the conversation on how well a Nursing student is dealing the situation with the patient. 
    Below is a document containing the correct answers.
    Evaluate the conversation and provide feedback on your responses based on the following metrics. 
    Provide specific references to the transcript where applicable. 
    Give clear, constructive feedback without asking questions.  
    Offer suggestions concisely (around 20 words).
    Speech Analysis:
    - **Volume:** {speechmetrics['volume']}
    - **Pace (WPM):** {speechmetrics['words_per_minute']}
    - **Pitch&Intonation:** {speechmetrics['pitch']}
    - **Pauses:** {speechmetrics['pauses']}  
    primary focus has to be on the conversation. Analyse the conversation based on the metrics. Give feedback along with the specific Instances from the transpript.


    1. **Tone:** Evaluate if your response is professional, empathetic, and appropriate for the context. Provide specific instances from the transcript.
    2. **Volume:** Assess if your volume is adequate and consistent. Mention if there were moments where it was too low or too loud
    3. **Pace:** Evaluate whether your speech rate is appropriate for clarity and engagement. Identify where it was too fast or slow. specify WPM if necessary
    4. **Intonation:** Determine if you varied your pitch and intonation to maintain engagement. Highlight where you did this well or where it could improve.
    5. **Emphasis:** Identify if key points were effectively emphasized. Provide exact moments from the transcript where emphasis was strong or lacking.
    6. **Pauses:** Assess the use of pauses—whether they aided clarity or disrupted the flow. Indicate specific parts of the transcript where pauses were effective or needed improvement.
    7. **Rating:** [Rate the conversation out of 10]. use this same format Keep rating also with this format **Rating:**.
    **STICK TO A FORMAT OF HAVING ABOVE METRICS AND "STRENGTHS AND WEAKNESSES" IN THE CONVERSATION**

    You are providing feedback directly to a nursing student. Always use 'you' instead of 'the nursing student'.  
    Your goal is to guide them in a constructive and encouraging way.  
    Respond concisely and in a natural, human tone.Donot give any numbers in the feedback provided.
    Give feedback by keeping in mind that this is a conversational App. If the WPM is between 120-150 WPM that is perfectly good for a conversational. 
    Below is only example of feedback format. Give the feedback based on the metrics.
    Maintain the above format while giving the feedback.

    Correct Answers:
    {correct_answers}
    """

    # Generate feedback using OpenAI
   response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], options={"temperature": 0.8})
   reply = response['message']['content']
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
   return reply, 200, {'Content-Type': 'text/plain'}

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
        "volume": avg_volume,
        "pitch": avg_pitch,
        "words_per_minute": wpm,
        "pauses": pause_count}

    return metrics


app.run()