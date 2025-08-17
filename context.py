import boto3

def get_voice_for_age(age):
    if age <= 12:
        return "Ivy"
    elif age <= 25:
        return "Justin"
    elif age <= 50:
        return "Joanna"  # SSML supported
    elif age <= 70:
        return "Matthew"  # SSML supported
    else:
        return "Kimberly"

def get_emotion_ssml(context, mood):
    mood = mood.lower()
    if mood in ['angry', 'irritated']:
        emotion = 'disappointed'
    elif mood == 'happy':
        emotion = 'excited'
    elif mood == 'calm':
        return f"<speak>{context}</speak>"  # No emotion tag, just neutral voice
    else:
        return f"<speak>{context}</speak>"  # Default to neutral if mood is unknown

    # Only runs if mood is angry or happy
    return f"""
    <speak>
        <amazon:emotion name="{emotion}" intensity="medium">
            {context}
        </amazon:emotion>
    </speak>
    """


def synthesize_speech(age, context, mood, output_file="output.mp3"):
    polly = boto3.client("polly")
    voice_id = get_voice_for_age(age)
    ssml_text = get_emotion_ssml(context, mood)

    response = polly.synthesize_speech(
        Text=ssml_text,
        TextType="ssml",  # Important!
        OutputFormat="mp3",
        VoiceId=voice_id
    )

    with open(output_file, "wb") as file:
        file.write(response["AudioStream"].read())

    print(f"✅ Saved speech to {output_file} using voice '{voice_id}' with emotion '{mood}'")

# ---------- EXAMPLE USAGE ----------
if __name__ == "__main__":
    age = int(input("Enter age: "))
    mood = input("Enter mood (happy, calm, angry): ")
    context = input("Enter text to speak: ")
    synthesize_speech(age, context, mood)
