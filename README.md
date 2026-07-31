# Jarvis Voice Assistant

A smart, fast, and modular voice assistant built in Python. Designed to run in the background with a minimalist floating interface, Jarvis doesn't just obey pre-programmed commands—it **learns and writes its own code** for new skills using Artificial Intelligence.

---

## Platform Compatibility

*   **Windows:** Fully supported (Windows 10 / 11). The current release and its native commands are optimized for the Windows environment.
*   **Linux/macOS:** Coming soon. A cross-platform update is planned for future releases to replace Windows-specific shell commands with OS-agnostic alternatives.

## Key Features

* **Total Spotify Control:** Play songs, playlists, adjust volume, and control playback hands-free.
* **Navigation & System:** Open local programs, search the web, and control your PC's state.
* **Non-Intrusive Interface:** A transparent floating widget that lights up upon hearing its name, featuring an "Incognito Mode" to hide completely.
* **Local Voice Processing:** Uses the Vosk model for ultra-fast, offline, and privacy-respecting speech recognition.
* **Multilingual Support:** Configurable to run natively in English, Spanish, and Portuguese.

---

## How does Jarvis learn? (Learning Protocol)

Jarvis features a self-expansion system powered by Large Language Models (LLMs). 

1. **Detection:** If you ask for something not in its basic dictionary (e.g., *"Flip a coin"*).
2. **Reasoning:** It sends the request to Groq (Llama 3.3). 
3. **Code Generation:** The AI writes a native Python function to solve the problem.
4. **Hot Implementation:** It saves the new code in the `plugins_library` folder and executes it immediately without needing to restart the program.

If the internet connection fails, the assistant will automatically wake up your local **Ollama** server to process the request and continue learning without relying on the cloud.

---

## Installation and Usage (Standalone Version)

Forget about installing Python or configuring virtual environments. Jarvis is now available as a portable Windows executable.

1. **Download the app:** Go to the [Releases] section of this repository and download the `jarvis_v1.0.zip` file.
2. **Extract:** Unzip the folder anywhere on your PC.
3. **Configure your keys:** 
   * Open the extracted folder and look for the `.env.example` file.
   * Rename it to `.env` (removing the `.example` extension).
   * Open it with Notepad and paste your Spotify and Groq credentials.
4. **Run!** Double-click on `Jarvis.exe`. 

> **Note:** The first time you ask it to play music, your web browser will open requesting authorization to connect with your Spotify account.

---

## How to get your credentials (API Keys)?

### Spotify Requirements
**Strict Requirement:** You need a **Spotify Premium** account. The official Spotify API does not allow free accounts to modify the playback state (play, pause, change volume).

**Steps to get the keys:**
1. Go to [Spotify for Developers](https://developer.spotify.com/) and log in with your account.
2. Go to your *Dashboard* and click on **"Create App"**.
3. Fill in the name (e.g., "Jarvis Assistant") and description.
4. Under **Redirect URIs**, it is CRITICAL that you type exactly this: `http://localhost:8080`
5. Save changes and go to the *Settings* of your new App.
6. Copy the **Client ID** and **Client Secret** and paste them into your `.env` file.

### Groq Requirements (The AI Engine)
**Requirement:** A free Groq account.

**Steps to get the key:**
1. Go to the [Groq Console](https://console.groq.com/keys) and log in.
2. Click the **"Create API Key"** button.
3. Give it a name to identify it (e.g., "Jarvis").
4. Copy the key (it starts with `gsk_`) and paste it into your `.env` file under the `GROQ_API_KEY` variable.

### Ollama Requirements (Local Backup)
Ollama acts as a Plan B if the Groq connection fails.
1. Download and install the engine from [ollama.com](https://ollama.com/).
2. Open a terminal on your PC and run: `ollama run gemma2`.
3. This will download the local model (takes a few GBs). Once it finishes, you can close it.

---

## Customization (config.json)

When starting the program for the first time, a `config.json` file will be generated automatically. You can edit it to change the base behavior:

    {
        "language": "en",
        "assistant_name": "jarvis"
    }

* **language:** Changes the number conversion language (`en`, `es`, `pt`, `other`). Ensure you have the corresponding Vosk voice model downloaded.
* **assistant_name:** Changes the wake-word to whatever you prefer (e.g., "friday", "computer").

---

## Built-in Commands & Natural Language

You don't need to memorize strict robotic commands to talk to Jarvis. Thanks to its LLM integration and intent mapping system, the assistant understands natural language. If you say something similar to a known command, Jarvis is smart enough to understand the intent and link it to the correct action. 

Below is the list of native functions, what they do, and the default phrases you can say to trigger them in English, Spanish, or Portuguese:

### System & Utilities

*   **Open Programs (`open_program`):** Launches local applications. If Windows doesn't recognize the app natively, Jarvis triggers a learning protocol to find the correct command and saves it.
    *   *What to say:* "open [app]", "abre [app]".
*   **Web Searching (`web_search`):** Performs a direct Google search in your default web browser.
    *   *What to say:* "search the web for [query]", "search [query]", "busca en internet [query]", "busca [query]", "pesquisa na internet [query]".
*   **Time & Date (`tell_time`, `tell_date`):** Retrieves the current local time or date.
    *   *What to say:* "what time is it", "what is the date", "what day is today", "que hora es", "que dia es hoy", "que horas sao", "que dia e hoje".
*   **Power Management (`turn_off_pc`):** Initiates a safe 10-second shutdown sequence for your computer.
    *   *What to say:* "turn off the computer", "apaga la computadora", "desliga o computador".
*   **System Control (`close_assistant`):** Safely terminates the assistant's processes and threads.
    *   *What to say:* "close assistant", "cierrate", "apagate", "desliga".
*   **Incognito Mode (`incognito_activate`, `incognito_deactivate`):** Emits a signal to hide or show the floating user interface.
    *   *What to say:* "activate incognito mode", "deactivate incognito mode", "activar modo incognito", "desativar modo incognito".

### Spotify Control

*   **Smart Playback (`play_music`):** Searches and plays specific songs or playlists. It uses an accuracy scoring mechanism to ensure the best track or artist match is played. **Important:** By default, Jarvis searches for individual tracks. If you want to play a playlist, you *must* include the word "playlist" in your command.
    *   *What to say for songs:* "play [song]", "reproduce [song]", "toca [song]".
    *   *What to say for playlists:* "play playlist [name]", "reproduce playlist [name]", "toca playlist [name]".
*   **Media Controls:** Controls the current playback state.
    *   *Pause (`pause_music`):* "pause music", "pausa la musica", "pausa a musica".
    *   *Resume (`resume_music`):* "resume music", "reanuda la musica", "retoma a musica".
    *   *Skip (`next_song`):* "next song", "siguiente cancion", "proxima musica".
    *   *Go Back (`previous_song`):* "previous song", "cancion anterior", "musica anterior".
*   **Playback Modes:** Toggles special playback states.
    *   *Shuffle (`enable_shuffle`):* "enable shuffle", "modo aleatorio".
    *   *Loop (`enable_loop`):* "enable loop", "modo loop", "modo repeticao".
*   **Volume Adjustment (`set_volume`):** Sets precise volume levels (0-100). The system uses the `word2numberi18n` library to automatically convert spoken words into integer values.
    *   *What to say:* "set volume to [number]", "volume [number]", "volumen [number]". (e.g., "set volume to fifty").

*Note: If you request an action that is completely missing from this list, Jarvis will automatically trigger its learning protocol (`is_known=False`), write the Python code for that new capability, and save it as a hot-reloaded plugin to execute it instantly.*

---

## Developer Installation (Source Code)

If you want to modify the code or contribute to the project:

### 1. Clone the repository and set up the environment
Open your terminal and run the following commands:

    git clone https://github.com/LuisDF04/jarvisProject.git
    cd YOUR_REPOSITORY
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

### 2. Configure Environment Variables
Create a `.env` file in the root folder of the project using the same structure mentioned in the general installation guide.
