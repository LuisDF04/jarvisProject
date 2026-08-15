import os
import re
import time
import requests
from groq import Groq
from Helper import Helper

class LLM():
    def __init__(self):
        self.helper = Helper() 
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
            
        self.client = Groq(api_key=api_key)

        self.main_model = "openai/gpt-oss-120b" 

        self.fallback_url = "http://localhost:11434/api/generate"
        self.fallback_model = "gemma2"

    def get_intention(self, unknown_text, valid_actions):
        print(f"[INFO] Querying Groq for intent learning: '{unknown_text}'...")
        
        command_intention = 500
        prompt = f"""
        Map the user command to a regex pattern and choose an action from the allowed list, or invent a new snake_case intent if none match.
        
        ALLOWED INTENTS: {valid_actions}
        
        Format REQUIRED: pattern|intent
        No explanations, no markdown, zero extra words.
        
        Examples:
        "open spotify" -> open (.*)|open_program
        "lanza una moneda" -> lanza una moneda|lanzar_moneda
        
        Command: "{unknown_text}" -> 
        """
        return self.llm_result(prompt, command_intention, None)

    # def get_intention(self, unknown_text, valid_actions):
    #     print(f"[INFO] Querying Groq for intent learning: '{unknown_text}'...")
        
    #     command_intention = 250
    #     prompt = f"""
    #     You are a regex and intent mapper for a voice assistant. 
    #     Given the user's voice command, map it to a regex pattern and choose the EXACT action intent from the allowed list.
        
    #     ALLOWED INTENTS TO CHOOSE FROM: {valid_actions}
        
    #     CRITICAL RULE FOR NEW INTENTS:
    #     If NONE of the allowed intents match the user's request, you MUST INVENT a new, descriptive intent name using snake_case (e.g., flip_coin, check_weather, play_game). 
        
    #     Zero extra words. Zero explanations. Zero markdown. 
    #     Strictly return the result separated by a pipe character '|' like this: pattern|intent

    #     Exact examples (Using EXISTING intents):
    #     Command: "open spotify" -> open (.*)|open_program
    #     Command: "search the web for cats" -> search the web for (.*)|web_search
    #     Command: "what time is it" -> what time is it|tell_time

    #     Exact examples (Creating NEW intents in Spanish):
    #     Command: "lanza una moneda" -> lanza una moneda|lanzar_moneda
    #     Command: "sortea quién saca en el partido de vólei" -> sortea quién saca en el partido de (.*)|sortear_saque
    #     Command: "dime cuántos días faltan para navidad" -> dime cuántos días faltan para (.*)|calcular_dias

    #     Command: "{unknown_text}" -> 
    #     """
    #     return self.llm_result(prompt, command_intention, None)

    def get_program_command(self, program):
        print(f"[INFO] Querying Groq for '{program}'...")
        
        command_intention = 250
        prompt = f"""
        You are a strict Windows command translator. 
        Convert the program name to its exact execution command or environment path.
        Zero extra words. Zero explanations. Zero markdown.

        Inference rules:
        1. Microsoft Store Apps (WhatsApp, Netflix): use 'start <name>:'
        2. Browsers and system tools (Chrome, Edge): use 'start <name>'
        3. User apps (Discord, Telegram): use %LOCALAPPDATA% or %APPDATA%

        Exact examples:
        Program: netflix -> start netflix:
        Program: chrome -> start chrome
        Program: spotify -> start spotify:
        Program: whatsapp -> start whatsapp:
        Program: calculator -> calc
        Program: discord -> %LOCALAPPDATA%\\Discord\\Update.exe --processStart Discord.exe
        Program: telegram -> %APPDATA%\\Telegram Desktop\\Telegram.exe

        Program: {program} -> 
        """
        return self.llm_result(prompt, command_intention, None)
    
    def generate_plugin(self, intent_name, description):
        max_tokens = 1000
        prompt = f"""
        Write a Python function named '{intent_name}' that takes a single argument 'parameter'.
        User request: {description}

        CRITICAL RULES FOR DYNAMIC CALCULATION:
        1. If the request involves math or logic, the function MUST parse the 'parameter' (which contains the user's input).
        2. DO NOT return hardcoded values (like 2+2).
        3. Use 'eval()' or a regex parser to extract numbers from 'parameter' and calculate the result dynamically.
        4. Return ONLY valid Python code. No markdown, no explanations.
        
        Example for '{intent_name}':
        def {intent_name}(parameter):
            import re
            # Extract numbers from parameter like 'tres mas dos'
            numbers = re.findall(r'\d+', parameter.replace('tres', '3').replace('dos', '2').replace('mas', '+'))
            # ... or simply use eval if parameter is numeric string ...
            return str(eval(parameter))
        """
        return self.llm_result(prompt, max_tokens, intent_name)

    def _save_plugin_file(self, code, intent_name, source="Groq"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_dir = os.path.join(base_dir, "plugins_library")
        os.makedirs(plugin_dir, exist_ok=True)
        plugin_path = os.path.join(plugin_dir, f"{intent_name}.py")

        with open(plugin_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[INFO] New plugin created at {plugin_path} (via {source})")

    def llm_result(self, prompt, max_tokens, intent_name):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.main_model,
                temperature=0.0, 
                max_tokens=max_tokens,   
            )
            
            raw_text = chat_completion.choices[0].message.content or ""
            raw_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

            if not raw_text:
                raise ValueError("Empty response received from Groq")

            if intent_name is None:
                print(f"[DEBUG] Groq response: {repr(raw_text)}")
                return self.helper.clean_command(raw_text)
            else:
                code = self.helper.clean_code(raw_text)
                self._save_plugin_file(code, intent_name, source="Groq")
                return

        except Exception as e:
            print(f"[ERROR] Groq connection failed: {e}\n[INFO] Initiating fallback orchestration with Ollama...")

            if not self.helper.is_open("ollama"):
                print("[INFO] Waking up local Ollama server...")
                os.system("start ollama")
                time.sleep(4) 

            payload = {
                "model": self.fallback_model, 
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0 
                }
            }

            try:
                response = requests.post(self.fallback_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    raw_text_local = data.get("response", "")
                    raw_text_local = re.sub(r'<think>.*?</think>', '', raw_text_local, flags=re.DOTALL | re.IGNORECASE).strip()
                    print(f"[DEBUG] {self.fallback_model} (Local) response: {repr(raw_text_local)}")
                    
                    if intent_name is None:
                        return self.helper.clean_command(raw_text_local)
                    else:
                        code = self.helper.clean_code(raw_text_local)
                        self._save_plugin_file(code, intent_name, source="Ollama")
                        return
                        
                else:
                    print(f"[ERROR] Ollama internal error. HTTP Code: {response.status_code}")
                    return None
                
            except requests.exceptions.ConnectionError:
                print("[ERROR] Could not connect to Ollama server despite restart attempt.")
                return None
            except Exception as e:
                print(f"[ERROR] Unexpected local AI error: {e}")
                return None