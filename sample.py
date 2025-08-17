import boto3

polly = boto3.client('polly', region_name='us-east-1')

ssml_text = """
<speak>
  <amazon:emotion name="disappointed" intensity="medium">
    take medicine at 9 am.
  </amazon:emotion>
</speak>
"""

response = polly.synthesize_speech(
    Text=ssml_text,
    TextType='ssml',
    OutputFormat='mp3',
    VoiceId='Joanna',
    Engine='neural'
)

with open('test_output.mp3', 'wb') as f:
    f.write(response['AudioStream'].read())

print("Audio saved to test_output.mp3")
