import os
import json
import serial
import time
from os.path import join, dirname
from dotenv import load_dotenv
from watson_developer_cloud import SpeechToTextV1 as SpeechToText
from watson_developer_cloud import ConversationV1
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import TextToSpeechV1

from audio_io.audio_io import AudioIO 


context = {}

def transcribe_audio(stt, path_to_audio_file):
  with open(join(dirname(__file__), path_to_audio_file), 'rb') as audio_file:
    return stt.recognize(audio_file,
      content_type='audio/wav')


def main():
  try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    ser.isOpen()
    print ("port is opened")
  except IOError:
    ser.close()
    ser.open()
    print("port was already open, was closed and opene again")


  dotenv_path = join(dirname(__file__), '.env')
  load_dotenv(dotenv_path)
  
  stt = SpeechToText(
          username=os.environ.get("STT_USERNAME"),
          password=os.environ.get("STT_PASSWORD"))

  workspace_id = os.environ.get("WORKSPACE_ID")
  conversation = ConversationV1(
      username=os.environ.get("CONVERSATION_USERNAME"),
      password=os.environ.get("CONVERSATION_PASSWORD"),
      version='2016-09-20')

  tone_analyzer = ToneAnalyzerV3(
      username=os.environ.get("TONE_ANALYZER_USERNAME"),
      password=os.environ.get("TONE_ANALYZER_PASSWORD"),
      version='2016-02-11')

  tts = TextToSpeechV1(
    username=os.environ.get("TTS_USERNAME"),
    password=os.environ.get("TTS_PASSWORD"),
    x_watson_learning_opt_out=True)  # Optional flag

  current_action = ''
  msg_out = ''

  while current_action != 'end_conversation':
    message = listen(stt)
#    emotion = get_emotion(tone_analyzer, message)
    print(message)
    response = send_message(conversation, workspace_id, message, "sad") 

    # Check for a text response from API
    if response['output']['text']:
      msg_out = response['output']['text'][0]

    # Check for action flags sent  by the dialog
    if 'action' in response['output']:
      current_action = response['output']['action']

    # User asked what time is it, so we output the local system time
    if current_action == 'display_time':
      msg_out = 'The current time is ' + time.strftime('%I:%M %p')
      current_action = ''

    # User asked robot to step forward
    if current_action == 'step forward':
      msg_out = 'Walking forward'
      ser.write("1,1=".encode())
      current_action = ''

    # User asked robot to step back
    if current_action == 'step back':
      msg_out = 'stepping back'
      ser.write("1,2=".encode())
      current_action = ''

    # User asked robot to move left
    if current_action == 'step left':
      msg_out = 'Moving to the left'
      ser.write("1,5=".encode())
      current_action = ''

    # User asked robot to move right
    if current_action == 'step right':
      msg_out = 'moving to the right'
      ser.write("1,6=".encode())
      current_action = ''


    # User asked robot to wave
    if current_action == 'wave':
      msg_out = 'Waving'
      ser.write("2,2=".encode())
      current_action = ''

    print(msg_out)

    speak(tts, msg_out)
    #recorder.play_from_file("output.wav")

  ser.close()
    

def listen(stt):
  recorder = AudioIO("input.wav")

  print("Please say something into the microphone\n")
  recorder.record_to_file()

  print("Transcribing audio....\n")
  result = transcribe_audio(stt, 'input.wav')

  print(result)

  try:
    text = result['results'][0]['alternatives'][0]['transcript']
  except IndexError:
    text = "I didn't get it"
  print("Text: " + text + "\n")
  return text  


def get_emotion(tone_analyzer, text):
  result = tone_analyzer.tone(text=text)
  tones = result['document_tone']['tone_categories'][0]['tones']

  max_score = 0
  max_emotion = ''
  for tone in tones:
    if float(tone['score']) > max_score:
      max_emotion = tone['tone_id']
      max_score = float(tone['score'])

  return max_emotion


def send_message(conversation, workspace_id, message, emotion):
  global context
  context['emotion'] = emotion

  response = conversation.message(
    workspace_id=workspace_id,
    input={'text': message},
    context=context)

  if response['output']['text']:
    print(response['output']['text'][0])

  print(json.dumps(response, indent=4))
  
  context = response['context']

  return response

def speak(tts, text):
  with open('output.wav', 'wb') as audio_file:
    audio_file.write(
      tts.synthesize(
        text, 
        accept="audio/wav",
        voice="en-US_AllisonVoice"))

  player = AudioIO("output.wav")

  #print("Please say something into the microphone\n")
  player.play_from_file("output.wav")

  
  
if __name__ == '__main__':
  try:
    main()
  except:
    print("IOError detected, restarting...")
    main()



