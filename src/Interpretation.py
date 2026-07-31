from vosk import Model, KaldiRecognizer
from Helper import Helper
from Action import Action
import json
import re

class Interpretation():

    def __init__(self, recognizer, output):
        self.helper = Helper()
        self.action = Action(output)
        self.intents = self.helper.load_intents()
        self.recognizer = recognizer
        self.word = self.helper.load_config("assistant_name")

    def check_word(self, data):
        # Returns True exactly when it detects a pause or silence indicating you finished the phrase
        if self.recognizer.AcceptWaveform(data):
            result = self.recognizer.Result()
            res_dict = json.loads(result)
            heard_text = res_dict.get("text", "")
        else:
            # Speaking without stopping
            partial_result = self.recognizer.PartialResult()
            res_dict = json.loads(partial_result)
            heard_text = res_dict.get("partial", "")
            
        if heard_text != "":
            print(f"{heard_text}")

        heard_text = self.helper.remove_accents(heard_text)
        if self.word in heard_text:
            return True
            
        return False
    
    def check_petition(self, data):
        # Returns True exactly when it detects a pause or silence
        if self.recognizer.AcceptWaveform(data):
            result = self.recognizer.Result()
            res_dict = json.loads(result)
            petition = res_dict.get("text", "")
            petition = self.helper.remove_accents(petition)
            return petition, True
        else:
            return None, False  # No pause detected, request is not complete yet
        
    def process_petition(self, intention_or_description):
        print(f"\n[INFO] Analyzing petition: '{intention_or_description}'")
        self.intents = self.helper.load_intents()
        
        for pattern, intent in self.intents.items():
            match = re.search(pattern, intention_or_description)
            
            if match:
                parameter = match.group(1) if match.groups() else None
                print(f"[JSON] Fast command detected -> Action: {intent} | Parameter: {parameter}")
                self.action.execute(intent, parameter, description=None, is_known=True)
                return
        print("[LLM] Unknown command structure. Routing to LLM for learning...")
        self.action.execute(intention=None, parameter=None, description=intention_or_description, is_known=False)
        return