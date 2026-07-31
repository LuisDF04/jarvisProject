import pyaudio
from PyQt6.QtCore import QThread
from Helper import Helper
from Input import Input
from Output import Output
from Interpretation import Interpretation
from Notifications import Notifications

class Audio(QThread):

    def __init__(self):
        super().__init__()
        # Main engine of the program
        lang = Helper().load_config("lang")
        self.p = pyaudio.PyAudio()
        self.input = Input(self.p, lang)
        self.output = Output(self.p)
        self.interpreter = Interpretation(self.input.recognizer, self.output)
        self.notification = Notifications()
        
        self.chunk = 1024

    def recognize(self):
        self.notification.emit_word_detected()
        self.input.recognizer.Reset()
        self.input.stream.stop_stream()
        self.output.sound_recognition()
        self.input.stream.start_stream()

    def run(self):
        print("[INFO] Unified background audio system started...")
        
        try:
            while True:
                # Check if the microphone is active before reading
                if self.input.stream.is_active():
                    data = self.input.stream.read(self.chunk, exception_on_overflow=False)
                    if self.interpreter.check_word(data):
                       
                        print("---- Tell me! ----")
                        self.recognize()

                        # Listen to the request
                        while True:
                            data = self.input.stream.read(self.chunk, exception_on_overflow=False)
                            petition, is_complete = self.interpreter.check_petition(data)
                            
                            if is_complete:
                                # Pause the microphone immediately to prevent buffer overflow
                                self.input.stream.stop_stream()
                                
                                self.notification.emit_end_petition()
                                
                                # Added flush=True to force console output before heavy processing
                                print(f"[INFO] Complete petition: {petition}", flush=True)
                                
                                # Execute the heavy process (LLM, regex mapping, launching programs)
                                self.interpreter.process_petition(petition)
                                
                                # Resume the microphone
                                self.input.stream.start_stream()
                                break

                        self.input.recognizer.Reset()

                else:
                    self.msleep(10)
                    
        finally:
            self.input.stream.close()
            self.p.terminate()