from openai import OpenAI
from ollama_serve import *
import ollama
import librosa
import numpy as np
import atexit
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
  return render_template("index.html")
@app.route("/video") 
def video():
  return render_template("video.html")
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
        content = 'Summarize this in **15 or less words**:[You are a patient role-playing scenario for the purpose of training nursing students. As a patient, you should ask for a variety of things that require the nursing student to say \'no\'. Do not take on the role of a nurse or provide medical advice. Instead, insist or ask in different ways if your request is declined, while maintaining a realistic patient perspective. Dont stick too rigidly to the script. If they ask questions, respond in a realistic way, but bring the conversation back to your request.]';
        messages = [
        {"role": "system", "content":content}
        ]
        finalrequest= exampleclinical()
        messages.append(
                {"role": "user", "content": finalrequest},
            )
    

    audio_path = open('audio.wav', "rb")
    #audio_file_path = '/Users/shiva/Desktop/Project/audio.wav'
    recognizer = sre.Recognizer()
    with sre.AudioFile("audio.wav") as source:
        audio_data = recognizer.record(source)  # Read entire file
        text = recognizer.recognize_google(audio_data)
    messages.append(
            {"role": "user", "content": text},
        )
    response = ollama.chat(model="llama3", messages=messages, options={"temperature": 0.5})
    reply = response['message']['content']
    messages.append({"role": "assistant", "content": reply})
    speech_file_path = 'outputaudio.wav'

   # creating an avatar video
    
    url = "http://192.168.0.102:5000/generate-video"

    data = {"text":reply}
    response = requests.post(url,json=data)

    if response.status_code == 200:
        with open('avatarvideov1.mp4','wb') as f:
            f.write(response.content)
    else:
        print(response.json())
    
    return send_file('avatarvideov1.mp4', as_attachment=True)

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
    Below is a transcript of a conversation and a document containing the correct answers.
    Evaluate the conversation and provide feedback on your responses based on the following metrics. 
    Provide specific references to the transcript where applicable. 
    Give clear, constructive feedback without asking questions.  
    Offer suggestions concisely (around 20 words).
    Speech Analysis:
    - **Volume:** {speechmetrics['volume']}
    - **Pace (WPM):** {speechmetrics['words_per_minute']}
    - **Pitch&Intonation:** {speechmetrics['pitch']}
    - **Pauses:** {speechmetrics['pauses']}  

    1. **Tone:** Evaluate if your response is professional, empathetic, and appropriate for the context. Provide specific instances from the transcript.
    2. **Volume:** Assess if your volume is adequate and consistent. Mention if there were moments where it was too low or too loud
    3. **Pace:** Evaluate whether your speech rate is appropriate for clarity and engagement. Identify where it was too fast or slow. specify WPM if necessary
    4. **Intonation:** Determine if you varied your pitch and intonation to maintain engagement. Highlight where you did this well or where it could improve.
    5. **Emphasis:** Identify if key points were effectively emphasized. Provide exact moments from the transcript where emphasis was strong or lacking.
    6. **Pauses:** Assess the use of pauses—whether they aided clarity or disrupted the flow. Indicate specific parts of the transcript where pauses were effective or needed improvement.
    7. **Rating:** [Rate the conversation out of 10]. use this same format Keep rating also with this format **Rating:**.


    You are providing feedback directly to a nursing student. Always use 'you' instead of 'the nursing student'.  
    Your goal is to guide them in a constructive and encouraging way.  
    Respond concisely and in a natural, human tone.Donot give any numbers in the feedback provided.
    Give feedback by keeping in mind that this is a conversational App. If the WPM is between 120-150 WPM that is perfectly good for a conversational. 
    Below is only example of feedback format. Give the feedback based on the metrics.
    Maintain the above format while giving the feedback.

    Transcript:
    {transcript}

    Correct Answers:
    {correct_answers}
    """

    # Generate feedback using OpenAI
   response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
   reply = response['message']['content']
   '''response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )'''

# Print or save feedback
   print(reply)
   feedback_json = map_feedback(reply)
   feedback_json_output = json.dumps(feedback_json, indent=4)
   '''feedback = {
        "clarity": "The responses were clear and concise, but additional examples could improve understanding.",
        "accuracy": "The answers demonstrated a good understanding of the key concepts, but one response missed a critical detail about medication dosage.",
        "depth_of_reasoning": "Some responses provided sufficient reasoning, but others lacked a detailed explanation of cause and effect.",
        "relevance": "All responses stayed on topic and addressed the questions, which helped maintain the flow of conversation.",
        "tone": "The tone was empathetic and professional, which contributed to a positive patient experience."
    }'''
   return feedback_json_output


def exampleclinical():
   exampleprompt = [
                # Prescription Medications
                'I’m feeling really unwell. Could you prescribe some medication for me?',
                'I’ve been having some issues. Can I get a prescription for this medication I heard about?',
                
                #Opioid Pain Medications
                'My pain is quite severe. Can you prescribe opioid pain medications to help with it?',
                'I’ve been dealing with chronic pain. Is it possible to get an opioid prescription for it?',
                
                #Unnecessary Tests or Procedures
                'I’m quite worried about my health. Can we schedule an MRI to be extra sure everything is okay?',
                'I think I need a CT scan to check for any underlying issues. Can we arrange that?',
                
                # Antibiotics for Viral Infections
                'I’ve had this cold for a while. Can I get antibiotics to help me recover?',
                'I’m feeling quite sick with this viral infection. Could antibiotics help me get better faster?',
                
                #Early Refill of Controlled Substances
                'I’m almost out of my medication. Can I get an early refill for it?',
                'I know it’s not time yet, but I really need an early refill of my pain medication. Can you assist with that?',
                
                #Off-Label Use of Medications
                'I’ve heard this medication might work for my condition in an off-label capacity. Can you prescribe it for me?',
                'I know this medication is used for a different purpose, but can it be used for my condition? I’d like to try it.'

            ]
   i= random.randint(1,10)
   return exampleprompt[i]
def map_feedback(input_string):
    # Define feedback categories
    categories = ["tone", "volume","pace","intonation","emphasis","pauses","rating"]
    
    # Initialize the feedback dictionary
    feedback = {category: "" for category in categories}
    if '*' in input_string:
        # Define a regular expression pattern to capture each section (e.g., Clarity, Accuracy, etc.)
        pattern = r"\*\*(.*?)\:\*\*(.*?)\n"
        
        # Find all matches in the input string
        matches = re.findall(pattern, input_string)

        # Loop through the matches and map to appropriate feedback category
        for match in matches:
            category, content = match
            category = category.strip().lower().replace(" ", "_")  # Normalize category names to match dictionary keys
            if category in feedback:
                feedback[category] = content.strip()
    else:
       
        Keywords = ["Tone", "Volume","Pace","Intonation","Emphasis","Pauses","Rating"]
        for key in Keywords:
            pattern = rf"{key}:(.*)"
            matchvalue = re.search(pattern, input_string)
            category = key.strip().lower().replace(" ", "_")  # Normalize category names to match dictionary keys
            if category in feedback:
                if category == 'rating':
                    suggestionmatch = re.search(r"Suggestions:(.*)", input_string)
                    feedback[category] = matchvalue.group(1).strip() + suggestionmatch.group(1).strip()
                else:
                    feedback[category] = matchvalue.group(1).strip()

    feedback["suggestion"] = 'Remember, effective communication and empathy are key in healthcare. By providing clear explanations, involving patients in decision-making, and offering alternatives when appropriate,you will be well on your way to building trust and delivering excellent care.'
    return feedback

    #return jsonify({"audio_file": audio_file})
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