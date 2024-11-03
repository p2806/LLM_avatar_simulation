from openai import OpenAI
from flask import Flask,render_template,request,send_file,send_from_directory,url_for
#import moviepy.editor as mp
from moviepy.editor import VideoFileClip
import os,stat
import ffmpeg as ffmpeg
#from flask_ngrok import run_with_ngrok
import subprocess,random,time
from audio_extract import extract_audio
import requests, jsonify,json
from types import SimpleNamespace

client = OpenAI(api_key = '')

app=Flask(__name__)
#run_with_ngrok(app)


@app.route("/")
def home():
  return render_template("index.html")
@app.route("/video") 
def video():
  return render_template("video.html")
'''@app.route('/favicon.ico')
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')'''
'''@app.route("/favicon.ico")
def favicon():
    return url_for('static', filename='data:,')'''
@app.route("/save-video", methods=['POST'])
def save_video():
    if 'video' not in request.files:
        return "No video file part", 400
    file = request.files['video']
    #DIRNAME = os.path.dirname(__file__)
    #video_path = os.path.join(DIRNAME, 'uploaded_video.webm')
    #audio_path = os.path.join(DIRNAME, 'audio.wav')
#os.chmod(video_path,777)
    if file.filename == '':
        return "No selected file", 400
    if file:
        file.save('uploaded_video.webm')
    #os.chmod('uploaded_video.webm', stat.S_IRWXO)

   
    ffmpeg_path = r'/opt/homebrew/bin/ffmpeg'
    command=[ffmpeg_path,'-y','-i','uploaded_video.webm','-acodec','pcm_s16le','-q:a','0','-map','a','audio.wav']
    result = subprocess.run(command,check=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    

    #extract_audio(input_path="/Users/shiva/Desktop/Project/uploaded_video.webm", output_path="/Users/shiva/Desktop/Project/audio.wav")
    #ffmpeg -i input.webm output.mp4
    '''video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)'''
    
    #audio_file = video_to_audio('uploaded_video.webm', 'audio.wav')
    content = 'You are a patient role-playing scenario for the purpose of training nursing students. As a patient, you should ask for a variety of things that require the nursing student to say \'no\'. Do not take on the role of a nurse or provide medical advice. Instead, insist or ask in different ways if your request is declined, while maintaining a realistic patient perspective. Dont stick too rigidly to the script. If they ask questions, respond in a realistic way, but bring the conversation back to your request.';
    messages = [
    {"role": "system", "content":content}
     ]
    finalrequest= exampleclinical()
    messages.append(
            {"role": "user", "content": finalrequest},
        )

    audio_path = open('audio.wav', "rb")
    #audio_file_path = '/Users/shiva/Desktop/Project/audio.wav'
    transcription = client.audio.translations.create(
    model="whisper-1", 
    file=audio_path
    )
    messages.append(
            {"role": "user", "content": transcription.text},
        )
    chat = client.chat.completions.create(
            model="gpt-4o", messages= messages
        )
    reply = chat.choices[0].message.content
    speech_file_path = 'outputaudio.wav'
    #with client.audio.speech.with_streaming_response.create(
       # model="tts-1",
        #voice="alloy",
        #input=reply,
    #) as response:
      # response.stream_to_file(speech_file_path)

    url = "https://api.d-id.com/talks"

    payload = {
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg",
        "script": {
            "type": "text",
            "subtitles": "false",
            "provider": {
                "type": "microsoft",
                "voice_id": "Sara"
            },
            "input": reply
        },
        "config": {
            "fluent": "false",
            "pad_audio": "0.0"
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic "
    }

    createresponse = requests.post(url, json=payload, headers=headers)
    response_data = json.dumps(createresponse.json(), indent=4)
    #response_data = '{\n    "id": "tlk_Zdbl9wL5i0PdhzoLiD4e8",\n    "created_at": "2024-10-05T20:15:49.428Z",\n    "created_by": "auth0|66cba2cff5083f9b6b524bb0",\n    "status": "created",\n    "object": "talk"\n}'
    #response_data = json.loads(response_data)
    data = json.loads(response_data, object_hook=lambda d: SimpleNamespace(**d))
    responseID = data.id
    url = f'https://api.d-id.com/talks/{responseID}'

    headers = {
        "accept": "application/json",
        "authorization": "Basic "
    }
    try:
        i=0
        while(i<10):
            getresponse = requests.get(url, headers=headers)
            avatarresponse = json.dumps(getresponse.json(),indent =4)
            avatarresponsedata = json.loads(avatarresponse, object_hook=lambda d: SimpleNamespace(**d))
            if(avatarresponsedata.status == 'done'):
                  avatarurl = avatarresponsedata.result_url
                  break;
            else:
                time.sleep(5)
                i=i+1
    
    except:
       print(f"Request failed")
       return None
       
          
    r = requests.get(avatarurl,stream=True)
    with open("avatarvideov1.mp4","wb") as fp:
       #for chunk in r.iter_content(chunk_size=256):
        fp.write(r.content)
    

    
    return send_file('avatarvideov1.mp4', as_attachment=True)
    #return jsonify({"video_url":avatarurl})


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


    #return jsonify({"audio_file": audio_file})


app.run()
