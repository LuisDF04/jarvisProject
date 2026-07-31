import pyaudio
from vosk import Model, KaldiRecognizer

class Input():

    def __init__(self, p_engine, lang):
        self.p = p_engine 
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  
        self.chunk = 1024
        
        self.stream = self.p.open(format=self.format, channels=self.channels, rate=self.rate, input=True)
        
        # Requires the English vosk model to be installed
        model = Model(lang=f"{lang}") 
        self.recognizer = KaldiRecognizer(model, self.rate)