import subprocess
import datetime
import tempfile
import sounddevice as sd
import scipy.io.wavfile as wav
from gtts import gTTS
from playsound import playsound
import requests
import speech_recognition as sr
NEWS_API_KEY = '886c4cf1a0dc426a8d12508faaa8cddb'
ALPHA_VANTAGE_API_KEY = 'ZIWWO74EIUPXW078'
DEFAULT_LANG = 'en'
class FRIDAYAI:
    def __init__(self):
        self.status_var = "Listening for commands..."
        self.perform_system_checks()
    def speak(self, audio, lang=DEFAULT_LANG):
        tts = gTTS(audio, lang=lang)
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            tts.save(fp.name)
            playsound(fp.name)
    def wishme(self, lang=DEFAULT_LANG):
        hour = datetime.datetime.now().hour
        if 6 <= hour < 12:
            self.speak("Good Morning Mr. Chandra", lang=lang)
        elif 12 <= hour < 18:
            self.speak("Good Afternoon Mr. Chandra", lang=lang)
        elif 18 <= hour < 24:
            self.speak("Good Evening Mr. Chandra", lang=lang)
        else:
            self.speak("Hello Mr. Chandra", lang=lang)
        self.speak("FRIDAY at your service. Please tell me how I can assist you today", lang=lang)
    def fetch_news(self, query=None, lang=DEFAULT_LANG):
        try:
            if query:
                url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
            else:
                url = f'https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}'
            response = requests.get(url)
            response.raise_for_status()
            news_data = response.json()
            if news_data['status'] == 'ok':
                if query:
                    self.speak(f"Here are the top news articles about {query}.", lang=lang)
                else:
                    self.speak("Here are the top news headlines for today.", lang=lang)
                for i, article in enumerate(news_data['articles'][:2], 1):
                    self.speak(f"Headline {i}: {article['title']}", lang=lang)
                    print(f"Headline {i}: {article['title']}")
            else:
                self.speak("I'm sorry, I couldn't fetch the news at the moment.", lang=lang)
        except requests.exceptions.RequestException as e:
            self.speak("There was an error connecting to the news service.", lang=lang)
            print(e)
    
# Taking commands
    def take_command(self):
        fs = 44100
        duration = 5
        print("Listening...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wav.write(f.name, fs, audio)
            f.seek(0)
            recognizer = sr.Recognizer()
            with sr.AudioFile(f.name) as source:
                audio_data = recognizer.record(source)
            try:
                print("Recognizing...")
                query = recognizer.recognize_google(audio_data, language='en-in')
                print(f"You said: {query}")
                return query.lower()
            except sr.UnknownValueError:
                self.speak("I didn't catch that. Could you say it again?")
                return None
            except sr.RequestError as e:
                self.speak(f"Could not request results from Google Speech Recognition service; {e}")
                return None
    
# Basic command handling
    def handle_command(self, command, lang=DEFAULT_LANG):
        if 'time' in command:
            self.tell_time(lang=lang)
        elif 'date' in command:
            self.tell_date(lang=lang)
        elif 'news' in command:
            if 'about' in command:
                query = command.split('about')[1].strip()
                self.fetch_news(query, lang=lang)
            else:
                self.fetch_news(lang=lang)
        
# Basic commands
        elif 'who are you' in command or 'introduce yourself' in command:
            self.speak("I am FRIDAY, your personal assistant.", lang=lang)
        elif 'how are you' in command:
            self.speak("I am fine, thank you. How can I assist you today?", lang=lang)
        elif 'who created you' in command:
            self.speak("I was created by the great Lord Akshat Chandra", lang=lang)
        elif 'what does your name stand for' in command or 'what does friday stand for' in command:
            self.speak("My name stands for: Female Replacement Intelligent Digital Assistant Youth", lang=lang)
        elif 'friday shutdown' in command or 'shutdown friday' in command or 'shut down friday' in command:
            self.speak("Shutting down. Goodbye!", lang=lang,)

# Opening Applications
        elif "open safari" in command:
            self.speak("Opening Safari", lang=lang)
            def open_app(app_name):
                try:
                    subprocess.run(["open", "-a", app_name])
                    print(f"{app_name} opened successfully.")
                except Exception as e:
                    print(f"Could not open {app_name}: {e}")

            open_app("Safari")
        
        elif "open settings" in command:
            self.speak("Opening System Settings", lang=lang)
            def open_app(app_name):
                try:
                    subprocess.run(["open", "-a", app_name])
                    print(f"{app_name} opened successfully.")
                except Exception as e:
                    print(f"Could not open {app_name}: {e}")

            open_app("System Settings")
        
        elif "open spotify" in command:
            self.speak("Opening Spotify", lang=lang)
            def open_app(app_name):
                try:
                    subprocess.run(["open", "-a", app_name])
                    print(f"{app_name} opened successfully.")
                except Exception as e:
                    print(f"Could not open {app_name}: {e}")

            open_app("Spotify")

# Error message
        else:
            self.speak("I am not sure how to respond to that. Can you please repeat?", lang=lang)
        self.speak("Is there anything else you need?", lang=lang)
    def tell_time(self, lang=DEFAULT_LANG):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speak("The time currently is", lang=lang)
        self.speak(current_time, lang=lang)

    def tell_date(self, lang=DEFAULT_LANG):
        current_date = datetime.datetime.now().strftime("%d %B %Y")
        self.speak("And the date currently is", lang=lang)
        self.speak(current_date, lang=lang)

    def perform_system_checks(self):
        try:
            self.speak("Friday personal assistant activating")
            self.speak("System checks complete")
        except Exception as e:
            self.speak(f"Error during system checks: {e}")

        self.wishme()

    def listen_for_commands(self):
        while True:
            command = self.take_command()
            if command:
                self.handle_command(command)

if __name__ == "__main__":
    app = FRIDAYAI()
    app.listen_for_commands()
