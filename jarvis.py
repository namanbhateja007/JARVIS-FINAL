import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
from google import genai
import jarvis_ui
import threading
import audio_monitor


def speak(text): 
    jarvis_ui.set_state("speaking")

    engine = pyttsx3.init() 
     
    engine.setProperty('rate', 150)
     
    engine.say(text) 
    engine.runAndWait() 
    engine.stop()

    jarvis_ui.set_state("standby")


newsapi = "YOUR_NEWS_API_KEY"


def aiProcessor(command):
    client = genai.Client(api_key="Api_key") 

    chat = client.chats.create(
        model="gemini-3.6-flash"
    )

    # Add this instruction to keep answers brief
    briefer_command = f"Answer in 2-3 sentences maximum, be concise and direct: {command}"
    
    response = chat.send_message(briefer_command)

    return response.text

def processcommand(c):
   
    jarvis_ui.set_command(c)
    jarvis_ui.set_state("thinking")

    if "open google" in c.lower():

     if "open google" in c.lower():
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com/")

    elif "open instagram" in c.lower():
        webbrowser.open("https://www.instagram.com/")

    elif "open linkedin" in c.lower():
        webbrowser.open("https://www.linkedin.com/")

    elif c.lower().startswith("play"):
        song = c.lower().replace("play ", "")
        link = musiclibrary.music[song]
        webbrowser.open(link)

    elif "news" in c.lower():

        response = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}"
        )

        print("Status Code:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:

            data = response.json()

            articles = data.get("articles", [])

            print("Number of articles:", len(articles))

            for article in articles:
                print(article["title"])
                speak(article["title"])

        else:
            print("Failed to fetch news.")

    else:
        output = aiProcessor(c)
        speak(output)
    jarvis_ui.set_state("standby")


if __name__ == "__main__":

    jarvis_ui.start()

    threading.Thread(
        target=audio_monitor.start_audio_monitor,
        daemon=True
    ).start()

    speak("Initialising Jarvis....")

    while True:

        r = sr.Recognizer()

        print("Recognizing...")

        try:
            jarvis_ui.set_state("listening")

            with sr.Microphone() as source:

                print("Listening...")

                audio = r.listen(
                    source,
                    timeout=3,
                    phrase_time_limit=2
                )

            word = r.recognize_google(audio)
            jarvis_ui.set_state("standby")

            print("You said:", word)

            if "jarvis" in word.lower():

             print("WAKE WORD DETECTED")
     
             speak("Yes Sir, I am listening...")

             jarvis_ui.set_state("listening")

            with sr.Microphone() as source:

             print("Jarvis Active...")
     
             audio = r.listen(source)

             command = r.recognize_google(audio)

             print("Command:", command)

             jarvis_ui.set_command(command)
             jarvis_ui.set_state("thinking")
            processcommand(command)

        except Exception as e:

         print("Error:", e)












