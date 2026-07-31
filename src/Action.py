import subprocess
import webbrowser
import datetime
import time
import os
import re

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from word2numberi18n import w2n

from Helper import Helper
from LLM import LLM
from Plugin import Plugin
from Notifications import Notifications

class Action:
    def __init__(self, output):
        # Request permission to read and modify playback
        scope = "user-modify-playback-state user-read-playback-state"
        self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET, self.SPOTIPY_REDIRECT_URI = Helper().load_credentials()
        self.routes = Helper().load_routes()
        self.llm = LLM()
        self.output = output
        self.plugins = Helper().load_plugins()
        self.lang = Helper().load_config("lang")
        self.notification = Notifications()

        # Initialize API control
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.SPOTIPY_CLIENT_ID,
            client_secret=self.SPOTIPY_CLIENT_SECRET,
            redirect_uri=self.SPOTIPY_REDIRECT_URI,
            scope=scope
        ))

    def execute(self, intention, parameter, description, is_known):
        if is_known:
            # Try to fetch a native method
            method = getattr(self, intention, None)
            
            # If not native, try to fetch from plugins
            if not method:
                method = self.plugins.get(intention)
            
            # Execute
            if callable(method):
                try:
                    result = method(parameter)
                    if result:
                        print(f"[JARVIS] {result}")
                        self.output.speak(result)
                        
                except Exception as e:
                    print(f"[ERROR] Failed to execute action '{intention}': {e}")
            else:
                print(f"[ERROR] The action '{intention}' was not found anywhere.")
        else:
            # Gather all native methods
            valid_actions = [
                func for func in dir(self) 
                if callable(getattr(self, func)) and not func.startswith("__") and func != "execute"
            ]
            # Add all existing plugin functions
            valid_actions.extend(list(self.plugins.keys()))

            # Learning protocol
            learning_result = self.llm.get_intention(description, valid_actions)
            
            if learning_result and "|" in learning_result:
                pattern, new_intent = Helper().clean_patern_and_intention(learning_result)
                print(f"[INFO] Learned new intent structure -> Pattern: '{pattern}' | Action: '{new_intent}'")
                
                intents_cache = Helper().load_intents()
                intents_cache[pattern] = new_intent
                Helper().save_intents(intents_cache)

                match = re.search(pattern, description)
                new_parameter = match.group(1) if match and match.groups() else None
                
                # If the LLM returned a completely new intent, generate the plugin first
                if new_intent not in valid_actions:
                    print(f"[PLUGIN] Capability missing. Generating code for '{new_intent}'...\n")
                    self.llm.generate_plugin(new_intent, description)
                    
                    # Hot-reload the plugins so the new function becomes executable immediately
                    self.plugins = Helper().load_plugins()
                
                # Execute recursively
                self.execute(new_intent, new_parameter, description, is_known=True)
            else:
                print("[ERROR] Failed to learn the intention or the LLM format was invalid.")

    def open_program(self, program):
        print(f"[INFO] Opening {program}...")
        program = program.lower().strip()

        cmd_json = self.routes.get(program)

        try:
            if cmd_json:
                if not cmd_json.startswith("start "):
                    subprocess.Popen(cmd_json, shell=True)
                else:
                    os.system(cmd_json)

            else:
                print(f"[INFO] Learning how to open {program}")
                result = subprocess.run(["cmd", "/c", f"start {program}"], capture_output=True, text=True)
                new_cmd = f"start {program}"

                if result.returncode != 0:
                    print(f"[WARNING] Windows does not recognize '{program}'. Initiating learning protocol...")
                    new_cmd = self.llm.get_program_command(program)
                    
                if new_cmd:
                    print(f"[INFO] Learned, saving command: {new_cmd}")
                    self.routes[program] = new_cmd
                    Helper().save_routes(self.routes)
                    
                    if new_cmd.startswith("start "):
                        os.system(new_cmd)
                    else:
                        subprocess.Popen(new_cmd, shell=True)
                else:
                    print(f"[ERROR] Could not learn how to open {program}.")
            
            return
                        
        except Exception as e:
            print(f"[ERROR] Failed trying to open {program}: {e}")

    def incognito_activate(self, parameter=None):
        self.notification.emit_incognito_activate()

    def incognito_deactivate(self, parameter=None):
            self.notification.emit_incognito_deactivate()

    def web_search(self, query):
        if query:
            print(f"[INFO] Searching for '{query}' on the web...")
            formatted_query = query.replace(' ', '+')
            url = f"https://google.com/search?q={formatted_query}"
            webbrowser.open(url)
        else:
            print("[WARNING] What do you want me to search for?")

        return

    def tell_time(self, parameter=None):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        # print(f"[INFO] It is exactly {current_time}.")
        # self.output.speak(current_time)
        return current_time

    def tell_date(self, parameter=None):
        now = datetime.datetime.now()
        # Formats the date as "YYYY-MM-DD" or you can use "%A, %B %d, %Y" for a full string
        current_date = now.strftime("%Y-%m-%d")
        return current_date

    def turn_off_pc(self, parameter=None):
        print("[INFO] Shutting down the computer...")
        os.system("shutdown /s /t 10")
        return

    def close_assistant(self, parameter=None):
        import os
        print("[INFO] Apagando el sistema...")
        # os._exit(0) > sys.exit(), por causa de los hilos (threads) (mata todo de golpe sin dejar procesos fantasma)
        os._exit(0)

    def pause_music(self, parameter=None):
        try:
            self.sp.pause_playback()
            print("[INFO] Music paused.")
        except Exception as e:
            print(f"[WARNING] Could not pause: {e}")

    def resume_music(self, parameter=None):
        try:
            self.sp.start_playback()
            print("[INFO] Music resumed.")
        except Exception as e:
            print(f"[WARNING] Could not resume: {e}")

    def next_song(self, parameter=None):
        try:
            self.sp.next_track()
            print("[INFO] Skipped to next song.")
        except Exception as e:
            print(f"[WARNING] Could not skip song: {e}")

    def previous_song(self, parameter=None):
        try:
            self.sp.previous_track()
            print("[INFO] Playing previous song.")
        except Exception as e:
            print(f"[WARNING] Could not play previous song: {e}")

    def enable_shuffle(self, parameter=None):
        try:
            self.sp.shuffle(True)
            print("[INFO] Shuffle mode enabled.")
        except Exception as e:
            print(f"[WARNING] Could not enable shuffle: {e}")

    def enable_loop(self, parameter=None):
        try:
            # You can change 'context' to 'track' if you prefer looping a single song
            self.sp.repeat('context')
            print("[INFO] Loop mode enabled.")
        except Exception as e:
            print(f"[WARNING] Could not enable loop: {e}")

    def set_volume(self, parameter=None):
        if not parameter:
            print("[WARNING] I need a specific volume level.")
            return

        parameter = parameter.lower().strip()
        volume_level = None

        # 1. If it is already a digit (e.g., from text input)
        if parameter.isdigit():
            volume_level = int(parameter)
        else:
            # 2. Use the library to parse spoken words into integers (Spanish context)
            try:
                # Initialize the converter for Spanish ('es')
                sp_converter = w2n.W2N(self.lang)
                volume_level = sp_converter.word_to_num(parameter)
            except ValueError:
                # ValueError is raised by w2n if it cannot find any valid numbers in the string
                print(f"[WARNING] Could not extract a valid number from '{parameter}'.")
                return

        if volume_level is not None:
            # Make sure it stays within Spotify limits (0-100)
            volume_level = max(0, min(volume_level, 100))
            
            try:
                self.sp.volume(volume_level)
                print(f"[INFO] Volume set to {volume_level}%.")
            except Exception as e:
                print(f"[WARNING] Could not change volume: {e}")

    def play_music(self, query):
        if not query:
            print("[INFO] Opening Spotify...")
            os.system("start spotify:")
            return

        print(f"[INFO] Searching for '{query}' on Spotify silently...")
        
        # Check if the Spotify process is currently running
        is_open = False
        try:
            output = subprocess.check_output('tasklist', shell=True, text=True).lower()
            if "spotify.exe" in output:
                is_open = True
        except Exception:
            pass

        # If closed, launch Spotify minimized and wait for it to initialize
        if not is_open:
            print("[INFO] Spotify was closed. Opening application...")
            # If Spotify is completely closed, Windows will always open it visible
            # the first time, since the 'spotify:' protocol ignores '/min'
            os.system("start /min spotify:")
            time.sleep(5)

        try:
            # Determine if the user explicitly requested a playlist
            is_playlist = "playlist" in query.lower()
            
            # Clean the word "playlist" from the query to avoid confusing the Spotify search engine
            clean_query = query.lower().replace("playlist", "").strip()
            if not clean_query:
                clean_query = query

            # Adjust the search type based on what was detected
            search_type = 'playlist' if is_playlist else 'track'
            print(search_type)
            results = self.sp.search(q=clean_query, limit=10, type=search_type)
            
            item_to_play = None

            ###########################
            ### LOGIC FOR PLAYLISTS ###
            ###########################
            if is_playlist:
                item_to_play = results['playlists']['items'][0]
                # Clean the name for the Windows console
                safe_name = item_to_play['name'].encode('ascii', 'ignore').decode('ascii')
                print(f"[INFO] Playlist found: {safe_name}")

            #######################################################    
            ### LOGIC FOR TRACKS (With accuracy scoring system) ###
            #######################################################
            elif not is_playlist:
                tracks = results['tracks']['items']
                best_track = tracks[0]
                best_score = -1
                query_words = set(clean_query.split())
                
                for track in tracks:
                    track_name = track['name'].lower()
                    artist_name = track['artists'][0]['name'].lower()
                    combined_text = f"{track_name} {artist_name}"
                    
                    # Score: +1 for every query word found in the track or artist name
                    score = sum(1 for word in query_words if word in combined_text)
                    
                    # Perfect match breaks the loop immediately
                    if score == len(query_words):
                        best_track = track
                        break
                    
                    # Update best score and track if a better match is found
                    if score > best_score:
                        best_score = score
                        best_track = track
                        
                item_to_play = best_track
                # Clean the name and artist for the Windows console
                safe_name = item_to_play['name'].encode('ascii', 'ignore').decode('ascii')
                safe_artist = item_to_play['artists'][0]['name'].encode('ascii', 'ignore').decode('ascii')
                print(f"[INFO] Best match found: {safe_name} by {safe_artist}")

            ######################    
            ### PLAYBACK LOGIC ###
            ######################
            if item_to_play:
                # Request the list of active devices connected to the account
                devices_response = self.sp.devices()
                device_list = devices_response.get('devices', [])

                # If no device is detected immediately (slow startup), wait 3 seconds and retry
                if not device_list:
                    time.sleep(3)
                    devices_response = self.sp.devices()
                    device_list = devices_response.get('devices', [])

                if device_list:
                    # Take the internal ID of the local PC (usually the first device)
                    computer_id = device_list[0]['id']
                    
                    # Use the correct API parameter depending on whether it's a playlist or a track
                    if search_type.startswith("playlist"):
                        self.sp.start_playback(device_id=computer_id, context_uri=item_to_play['uri'])
                    else:
                        self.sp.start_playback(device_id=computer_id, uris=[item_to_play['uri']])
                        
                    print("[INFO] Playing...")
                else:
                    print("[WARNING] Spotify took too long to connect to the internet. Try again.")
            else:
                print(f"[WARNING] No results found for '{query}'.")

            return
                
        except spotipy.exceptions.SpotifyException:
            print("[WARNING] Spotify needs an 'active device'. Play any song manually for a second, pause it, and ask again.")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")