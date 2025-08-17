import boto3

# Define voice mappings by age group and gender
def select_voice(age, gender):
    if gender == 'male':
        if age < 30:
            return 'Joey'
        elif age < 60:
            return 'Matthew'
        else:
            return 'Kevin'
    else:
        if age < 30:
            return 'Kendra'
        elif age < 60:
            return 'Joanna'
        else:
            return 'Ruth'

# Check if the voice supports emotion
def supports_emotion(voice_id):
    return voice_id in ['Joanna', 'Matthew']

# Wrap text in SSML with emotion
def wrap_with_emotion_ssml(text, emotion):
    return f"""<speak>
  <amazon:emotion name="{emotion}" intensity="medium">
    {text}
  </amazon:emotion>
</speak>"""

def synthesize_with_emotion(age, gender, emotion, text, output_file='output.mp3'):
    voice_id = select_voice(age, gender)
    engine = 'neural' if voice_id in ['Matthew', 'Joanna', 'Kendra', 'Joey'] else 'standard'

    use_ssml = supports_emotion(voice_id) and emotion in ['cheerful', 'empathetic']
    input_text = wrap_with_emotion_ssml(text, emotion) if use_ssml else text

    polly = boto3.client('polly', region_name='us-east-1')

    response = polly.synthesize_speech(
        Text=input_text,
        VoiceId=voice_id,
        OutputFormat='mp3',
        Engine=engine,
        TextType='ssml' if use_ssml else 'text'
    )

    with open(output_file, 'wb') as f:
        f.write(response['AudioStream'].read())

    print(f"Voice used: {voice_id} | Emotion: {emotion} | File saved: {output_file}")

# Example usage
synthesize_with_emotion(
    age=45,
    gender='male',
    emotion='cheerful',
    text="Hi there! I'm glad to assist you today."
)
