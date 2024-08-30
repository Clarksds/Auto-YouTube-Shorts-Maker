from dotenv import load_dotenv
import random
import os
import requests
from gtts import gTTS
from moviepy.editor import *
import moviepy.video.fx.crop as crop_vid

# Load environment variables
load_dotenv()

# Ask for video info
title = input("\nEnter the name of the video >  ")
option = input('Do you want AI to generate content? (yes/no) >  ')

if option == 'yes':
    # Generate content using Gemini AI API
    theme = input("\nEnter the theme of the video >  ")

    ### MAKE .env FILE AND SAVE YOUR API KEY ###
    gemini_api_key = os.environ["GEMINI_API"]
    url = "https://api.gemini.ai/v1/generate-script"  # Example URL; replace with the actual Gemini API URL
    headers = {
        "Authorization": f"Bearer {gemini_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": f"Act as a script writer who writes engaging and professional scripts for TikTok shorts. Your scripts include a viral hook, are error-free, and prompt viewers to like and follow without mentioning any channel name. Generate content on - \"{theme}\"",
        "max_length": 200
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        content = response.json().get('content', '')
        print(content)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        exit()

    yes_no = input('\nIs this fine? (yes/no) >  ')
    if yes_no == 'yes':
        content = content
    else:
        content = input('\nEnter >  ')
else:
    content = input('\nEnter the content of the video >  ')

# Create the directory
if not os.path.exists('generated'):
    os.mkdir('generated')

# Generate speech for the video
speech = gTTS(text=content, lang='en', tld='ca', slow=False)
speech.save("generated/speech.mp3")

gp = random.choice(["1", "2"])
start_point = random.randint(1, 480)
audio_clip = AudioFileClip("generated/speech.mp3")

if audio_clip.duration + 1.3 > 58:
    print('\nSpeech too long!\n' + str(audio_clip.duration) + ' seconds\n' + str(audio_clip.duration + 1.3) + ' total')
    exit()

print('\n')

### VIDEO EDITING ###

# Trim a random part of minecraft gameplay and slap audio on it
video_clip = VideoFileClip("gameplay/gameplay_" + gp + ".mp4").subclip(start_point, start_point + audio_clip.duration + 1.3)
final_clip = video_clip.set_audio(audio_clip)

# Resize the video to 9:16 ratio
w, h = final_clip.size
target_ratio = 1080 / 1920
current_ratio = w / h

if current_ratio > target_ratio:
    # The video is wider than the desired aspect ratio, crop the width
    new_width = int(h * target_ratio)
    x_center = w / 2
    y_center = h / 2
    final_clip = crop_vid.crop(final_clip, width=new_width, height=h, x_center=x_center, y_center=y_center)
else:
    # The video is taller than the desired aspect ratio, crop the height
    new_height = int(w / target_ratio)
    x_center = w / 2
    y_center = h / 2
    final_clip = crop_vid.crop(final_clip, width=w, height=new_height, x_center=x_center, y_center=y_center)

# Write the final video
final_clip.write_videofile("generated/" + title + ".mp4", codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
