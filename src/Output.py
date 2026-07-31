import wave
import os
import threading
import time
import pyttsx3
import queue
from Helper import Helper

class Output():

    def __init__(self, p_engine):
        self.p = p_engine 
        self.chunk = 1024
        self.helper = Helper()
        
        # Use the new path resolution function
        self.activate_sound_path = self.helper.get_absolute_path(os.path.join("sounds", "activate.wav"))

        # self.speech_queue = queue.Queue()
        # self.tts_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        # self.tts_thread.start()

        # Save the sound to open it only once
        self.audio_frames = []
        self.format = None
        self.channels = None
        self.rate = None

        try:
            with wave.open(self.activate_sound_path, 'rb') as wf:
                self.format = self.p.get_format_from_width(wf.getsampwidth())
                self.channels = wf.getnchannels()
                self.rate = wf.getframerate()
                
                while len(data := wf.readframes(self.chunk)):
                    self.audio_frames.append(data)
                    
            # Output warming up
            # stream_dummy = self.p.open(
            #     format=self.format,
            #     channels=self.channels,
            #     rate=self.rate,
            #     output=True
            # )
            # stream_dummy.write(b'\x00' * self.chunk) # Empty bytes (silence)
            # stream_dummy.stop_stream()
            # stream_dummy.close()
            
        except Exception as e:
            print(f"[ERROR] Failed to preload sound: {e}")

    def stream(self):
        stream_out = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True
            )
        return stream_out

    def sound_recognition(self):

        def _play_sound():
            try:
            
                stream_out = self.stream()

                for data in self.audio_frames:
                    stream_out.write(data)

                time.sleep(0.2)
                
                stream_out.stop_stream()
                stream_out.close()
                
            except Exception as e:
                print(f"[ERROR] Output exception: {e}")

        # Start the background thread
        threading.Thread(target=_play_sound, daemon=True).start()

    def _process_speech_queue(self, phrase):
        # Initialize Text-to-Speech engine
        tts_engine = pyttsx3.init()
        # Speed of the voice (default is usually 200)
        tts_engine.setProperty('rate', 160)
        
        # while True:
        #     phrase = self.speech_queue.get()
        #     if phrase is None:
        #         break # Poison pill to stop the thread if needed
            
        try:
            tts_engine.say(phrase)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"[ERROR] TTS Output exception: {e}")
            # finally:
            #     self.speech_queue.task_done()

    def speak(self, phrase):
        # self.speech_queue.put(phrase)
        tts_thread = threading.Thread(target=self._process_speech_queue(phrase), daemon=True)
        tts_thread.start()