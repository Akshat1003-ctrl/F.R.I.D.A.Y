import datetime
import tempfile
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import requests
from tkinter import Tk, Label, StringVar
from PIL import Image, ImageTk, ImageSequence

# Go to websites and Add API keys to the following:
NEWS_API_KEY = ''  
ALPHA_VANTAGE_API_KEY = '' 
DEFAULT_LANG = 'en-uk'

class FRIDAYAI:
    def __init__(self, root):
        self.root = root
        self.root.title("FRIDAY AI")
       
        self.root.attributes('-fullscreen', False)
        self.root.configure(bg='black')

        self.status_var = StringVar()
        self.status_var.set("Listening for commands...")

        self.gif_label = Label(root, bg='black')
        self.gif_label.pack(expand=True)

        self.status_label = Label(root, textvariable=self.status_var, fg="white", bg="black")
        self.status_label.pack()

        self.load_gif("/Users/Akshat/Documents/AI Testing/orange_orb.gif")

        self.perform_system_checks()

        self.root.after(1000, self.listen_for_commands)

    def load_gif(self, path):
        self.gif = Image.open(path)
        self.frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.gif)]
        self.frame_index = 0
        self.update_gif()

    def update_gif(self):
        frame = self.frames[self.frame_index]
        self.gif_label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.root.after(1, self.update_gif)  

    def speak(self, audio, lang=DEFAULT_LANG):
        tts = gTTS(audio, lang=lang)
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            tts.save(fp.name)
            playsound(fp.name)

    def wishme(self, lang=DEFAULT_LANG):
        hour = datetime.datetime.now().hour
        if 6 <= hour < 12:
            self.speak("Morning Mr. Chandra", lang=lang)
        elif 12 <= hour < 18:
            self.speak("Afternoon Mr. Chandra", lang=lang)
        elif 18 <= hour < 24:
            self.speak("Evening Mr. Chandra", lang=lang)
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

    def fetch_stock_price(self, symbol, lang=DEFAULT_LANG):
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                price = data['Global Quote']['05. price']
                self.speak(f"The current price of {symbol} is {price} dollars.", lang=lang)
            else:
                self.speak("I'm sorry, I couldn't fetch the stock price at the moment.", lang=lang)
        except requests.exceptions.RequestException as e:
            self.speak("There was an error connecting to the stock market service.", lang=lang)
            print(e)

    def fetch_crypto_price(self, crypto_id, lang=DEFAULT_LANG):
        try:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if crypto_id in data and 'usd' in data[crypto_id]:
                price = data[crypto_id]['usd']
                self.speak(f"The current price of {crypto_id} is {price} dollars.", lang=lang)
            else:
                self.speak("I'm sorry, I couldn't fetch the cryptocurrency price at the moment.", lang=lang)
        except requests.exceptions.RequestException as e:
            self.speak("There was an error connecting to the cryptocurrency service.", lang=lang)
            print(e)

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            self.speak("I didn't catch that. Could you say it again?")
            return None
        except sr.RequestError as e:
            self.speak(f"Could not request results from Google Speech Recognition service; {e}")
            return None

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
        elif 'stock price' in command:
            symbol = command.split('price of')[1].strip().upper()
            self.fetch_stock_price(symbol, lang=lang)
        elif 'crypto price' in command:
            crypto_id = command.split('price of')[1].strip().lower()
            self.fetch_crypto_price(crypto_id, lang=lang)
        elif 'who are you' in command or 'introduce yourself' in command:
            self.speak("I am FRIDAY, your personal assistant.", lang=lang)
        elif 'how are you' in command:
            self.speak("I am fine, thank you. How can I assist you today?", lang=lang)
        elif 'who created you' in command:
            self.speak("I was created by the great Lord Akshat Chandra to serve for Lord Arijit Chandra", lang=lang)
        elif 'what does your name stand for' or 'what does friday stand for'in command:
            self.speak("my name stands for: Female Replacement Intelligent Digital Assistant Youth", lang=lang)
        elif 'friday shutdown' or 'shutdown friday' or 'shut down friday'in command:
            self.speak("Shutting down. Goodbye!", lang=lang)
            self.root.quit()
        else:
            self.speak("I am not sure how to respond to that. Can you please repeat?", lang=lang)

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
        command = self.take_command()
        if command:
            self.handle_command(command)
        self.root.after(1000, self.listen_for_commands)

if __name__ == "__main__":
    root = Tk()
    app = FRIDAYAI(root)
    root.mainloop()
