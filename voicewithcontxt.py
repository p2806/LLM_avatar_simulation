import boto3

def get_voice_for_age(age):
    if age <= 12:
        return "Ivy"
    elif age <= 25:
        return "Justin"
    elif age <= 50:
        return "Joanna"
    elif age <= 70:
        return "Matthew"
    else:
        return "Kimberly"

def get_emotion_ssml(context, mood, voice_id):
    mood = mood.lower()

    # Only Joanna and Matthew support emotion
    if voice_id not in ['Joanna', 'Matthew']:
        return context, "text"

    if mood in ['angry', 'irritated']:
        emotion = "disappointed"
    elif mood == "happy":
        emotion = "excited"
    else:
        return context, "text"

    ssml = f"""
    <speak>
      <amazon:emotion name="{emotion}" intensity="medium">
        {context}
      </amazon:emotion>
    </speak>
    """
    return ssml.strip(), "ssml"

def synthesize_speech(age, context, mood, output_file="output.mp3"):
    polly = boto3.client('polly', region_name='us-east-1')
    voice_id = get_voice_for_age(age)
    print(f"Using voice: {voice_id}")

    text, text_type = get_emotion_ssml(context, mood, voice_id)

    response = polly.synthesize_speech(
        Text=text,
        TextType=text_type,
        OutputFormat="mp3",
        VoiceId=voice_id,
        Engine="neural"  
    )

    with open(output_file, "wb") as out:
        out.write(response["AudioStream"].read())
    print(f"✅ Audio saved as {output_file}")

# --- Example Usage ---
if __name__ == "__main__":
    age = int(input("Enter age: "))
    mood = input("Enter mood (happy, calm, angry, etc.): ")
    context = input("Enter text to speak: ")
    synthesize_speech(age, context, mood)
