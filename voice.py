import boto3

def get_voice_for_age(age):
    """
    Map age ranges to Polly voices.
    """
    if age <= 12:
        return "Ivy"      # Female, child-like voice
    elif age <= 25:
        return "Justin"   # Male, teen/young adult
    elif age <= 50:
        return "Joanna"   # Female, adult
    elif age <= 70:
        return "Matthew"  # Male, mature
    else:
        return "Kimberly"  # Female, elderly-sounding

def synthesize_speech(age, context, output_file="output.mp3"):
    """
    Use Amazon Polly to convert text to speech based on age.
    """
    # Initialize the Polly client
    polly = boto3.client("polly")

    # Get appropriate voice based on age
    voice_id = get_voice_for_age(age)

    # Call Polly to synthesize speech
    response = polly.synthesize_speech(
        Text=context,
        
        OutputFormat="mp3",
        VoiceId=voice_id
    )

    # Save the audio stream to a file
    with open(output_file, "wb") as file:
        file.write(response["AudioStream"].read())

    print(f"✅ Saved speech to {output_file} using voice '{voice_id}'")

# ---------- EXAMPLE USAGE ----------
if __name__ == "__main__":
    age = int(input("Enter age: "))
    context = input("Enter text to speak: ")
    synthesize_speech(age, context)
