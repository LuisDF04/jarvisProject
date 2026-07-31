from dotenv import load_dotenv
import unicodedata
import subprocess
import importlib.util
import inspect
import os
import re
import json
import sys

class Helper():

    def __init__(self):
        self.intents_file = self.get_user_path("intents.json")
        self.routes_file = self.get_user_path("routes.json")
        self.config_path = self.get_user_path("config.json")
        env_path = self.get_user_path(".env")      
        
        # Load variables
        load_dotenv(dotenv_path=env_path)

    def get_user_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        return os.path.join(base_path, relative_path)

    def get_absolute_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        return os.path.join(base_path, relative_path)

    def is_open(self, program):
        try:
            output = subprocess.check_output('tasklist', shell=True, text=True).lower()
            if f"{program}.exe" in output or f"{program} app.exe" in output: 
                return True
        except Exception:
            return False

    def clean_patern_and_intention(self, learning_result):
        pattern, intent = learning_result.split("|", 1)
        pattern = pattern.strip().strip('"')
        intent = intent.strip().strip('"')
        return pattern, intent
    
    def clean_code(self, raw_text):
        # Clean the python code from possible markdown
        match = re.search(r'```python\s*(.*?)\s*```', raw_text, re.DOTALL)
        code = match.group(1) if match else raw_text.replace("```python", "").replace("```", "").strip()
        return code

    def clean_command(self, text):
        clear_cmd = text.replace("```cmd", "").replace("```bash", "").replace("```", "")
        lines = [line.strip() for line in clear_cmd.split('\n') if line.strip()]
        
        if lines:
            return lines[0].replace('""', '').replace('"', '')
        return None

    def remove_accents(self, text):
        normalized_text = unicodedata.normalize('NFKD', text)
        clean_text = "".join([c for c in normalized_text if not unicodedata.combining(c)])
        return clean_text.lower().strip()

    def load_config(self, return_key):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    lang = config.get("language", "es")
                    assistant_name = config.get("assistant_name", "jarvis")
                    
                    if return_key.startswith("lang"):
                        return lang
                    else:
                        return assistant_name
            except Exception as e:
                print(f"[ERROR] Error reading {self.config_path}: {e}. Using default values.")
                return "es" if return_key.startswith("lang") else "jarvis"
        else:
            print(f"[INFO] File {self.config_path} not found. Creating a new one with default values...")
            try:
                default_config = {
                    "language": "es",
                    "assistant_name": "jarvis"
                }
                
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=4)
                
                if return_key.startswith("lang"):
                    return default_config["language"]
                else:
                    return default_config["assistant_name"]
                    
            except Exception as e:
                print(f"[ERROR] Could not create {self.config_path}: {e}")
                return "es" if return_key.startswith("lang") else "jarvis"

    def load_credentials(self):
        try:
            SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
            SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
            SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
            return SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

        except FileNotFoundError:
            print("[ERROR] '.env' file not found. Please create it with your Spotify keys.")
            return
    
    def load_intents(self):
        if not os.path.exists(self.intents_file):
            default_intents = {
                # --- OPEN PROGRAMS (open_program) ---
                r"abre (.*)": "open_program",
                r"open (.*)": "open_program",

                # --- WEB (web_search) ---
                r"busca en internet (.*)": "web_search",
                r"busca (.*)": "web_search",
                r"search the web for (.*)": "web_search",
                r"search (.*)": "web_search",
                r"pesquisa na internet (.*)": "web_search",
                r"pesquisa (.*)": "web_search",

                # --- SPOTIFY: REPRODUCIR (play_music) ---
                r"reproduce (.*)": "play_music",
                r"play (.*)": "play_music",
                r"toca (.*)": "play_music",

                # --- SPOTIFY: CONTROLES BÁSICOS ---
                r"pausa la musica": "pause_music",
                r"pause music": "pause_music",
                r"pausa a musica": "pause_music",
                
                r"reanuda la musica": "resume_music",
                r"resume music": "resume_music",
                r"retoma a musica": "resume_music",

                r"siguiente cancion": "next_song",
                r"next song": "next_song",
                r"proxima musica": "next_song",

                r"cancion anterior": "previous_song",
                r"previous song": "previous_song",
                r"musica anterior": "previous_song",

                # --- SPOTIFY: MODOS Y VOLUMEN ---
                r"modo aleatorio": "enable_shuffle",
                r"enable shuffle": "enable_shuffle",

                r"modo loop": "enable_loop",
                r"enable loop": "enable_loop",
                r"modo repeticao": "enable_loop",

                r"volumen (.*)": "set_volume",
                r"set volume to (.*)": "set_volume",
                r"volume (.*)": "set_volume",

                # --- TIME DATE (tell_time, tell_date) ---
                r"que hora es": "tell_time",
                r"what time is it": "tell_time",
                r"que horas sao": "tell_time",

                r"que dia es hoy": "tell_date",
                r"que fecha es hoy": "tell_date",
                r"what is the date": "tell_date",
                r"what day is today": "tell_date",
                r"que dia e hoje": "tell_date",

                # --- SYSTEM (turn_off_pc, close_assistant) ---
                r"apaga la computadora": "turn_off_pc",
                r"turn off the computer": "turn_off_pc",
                r"desliga o computador": "turn_off_pc",

                r"apagate": "close_assistant",
                r"cierrate": "close_assistant",
                r"close assistant": "close_assistant",
                r"desliga": "close_assistant",

                # --- INCÓGNITO (incognito_activate, incognito_deactivate) ---
                r"modo incognito activado": "incognito_activate",
                r"activar modo incognito": "incognito_activate",
                r"activate incognito mode": "incognito_activate",
                r"ativar modo incognito": "incognito_activate",

                r"modo incognito desactivado": "incognito_deactivate",
                r"desactivar modo incognito": "incognito_deactivate",
                r"deactivate incognito mode": "incognito_deactivate",
                r"desativar modo incognito": "incognito_deactivate"
            }

            with open(self.intents_file, 'w', encoding='utf-8') as f:
                json.dump(default_intents, f, indent=4, ensure_ascii=False)
            return default_intents
        
        with open(self.intents_file, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def save_intents(self, intents_data):
        with open(self.intents_file, 'w', encoding='utf-8') as f:
            json.dump(intents_data, f, indent=4, ensure_ascii=False)
            
        print("[JSON] Intents updated")
        
    def load_routes(self):
        if not os.path.exists(self.routes_file):
            
            routes = {
                # --- Discord ---
                "discord": os.path.expandvars(r"%LocalAppData%\Discord\Update.exe --processStart Discord.exe"),

                # --- Navegador / Browser ---
                "navegador": "start chrome",
                "browser": "start chrome",
                "navegador web": "start chrome",

                # --- WhatsApp ---
                "whatsapp": "start whatsapp:",

                # --- Spotify ---
                "spotify": "start spotify:",

                # --- Calculadora / Calculator (y sus variaciones) ---
                "calculadora": "calc",
                "calculator": "calc",
                "calculadoras": "calc",
            }

            with open(self.routes_file, 'w', encoding='utf-8') as f:
                json.dump(routes, f, indent=4, ensure_ascii=False)
            return routes
        
        with open(self.routes_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_routes(self, routes):
        with open(self.routes_file, 'w', encoding='utf-8') as f:
            json.dump(routes, f, indent=4, ensure_ascii=False)

        print("[JSON] Routes updated")

    def load_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins_library")
        # Ensure the directory exists to prevent FileNotFoundError
        os.makedirs(plugin_dir, exist_ok=True) 
        
        plugins = {}
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(plugin_dir, filename)
                
                # Load the module dynamically
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Register functions found in the plugin
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    # Ensure we only load functions explicitly defined in the plugin file
                    if func.__module__ == module_name:
                        plugins[name] = func
                        print(f"[INFO] Plugin loaded: {name}")
                        
        return plugins