import speech_recognition as sr
import requests
from playsound import playsound
import os
from typing import Union


def generate_audio(message: str,voice : str = "Brian"):
    url: str = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={{{message}}}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.0.0'}
    
    
    try:
        result = requests.get(url=url, headers=headers)
        return result.content
    except:
        return None

def speak(message: str, voice: str = 'Brian', folder: str = "", extension: str = '.mp3') -> Union[None, str]:
    try:
        result_content = generate_audio(message, voice)
        file_path = os.path.join(folder, f"{voice}{extension}")
        with open(file_path, "wb") as file:
            file.write(result_content)
        playsound(file_path)
        os.remove(file_path)
        return None
    except Exception as e:
        print(e)
    

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
   #    
        print("Listening.....")
        r.pause_threshold = 1
        r.energy_threshold = 100
        # r.listen(source, timeout= 3)
        r.non_speaking_duration = 0.7
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)
        print("Say that again Please...")
        return "None"
    return query


speak("Hello there")    