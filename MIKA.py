import json
import os
from google import genai
from google.genai import types

# --- 1. SETUP ---
API_KEY = "AIzaSyDo88xlD0oVLK5vQLbG4C2kZ9tLSK37HDs"  # Best practice: use os.environ.get("GEMINI_API_KEY")
BOT_NAME = "Mika"
MEMORY_FILE = "mika_memory.json"

client = genai.Client(api_key=API_KEY)

# --- 2. THE BRAIN (Identity & Memory) ---
def load_memory():
    """Load past conversations and convert them back to SDK objects."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                # Reconstruct the list of Content objects the SDK expects
                return [
                    types.Content(
                        role=m["role"], 
                        parts=[types.Part(text=p["text"]) for p in m["parts"]]
                    ) for m in data
                ]
        except Exception as e:
            print(f"System: Error loading memory: {e}")
    return []

def save_memory(history):
    """Convert SDK history objects into JSON-friendly dictionaries."""
    serializable = []
    for entry in history:
        serializable.append({
            "role": entry.role,
            "parts": [{"text": p.text} for p in entry.parts if p.text]
        })
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(serializable, f, indent=4)

def start_mika():
    past_history = load_memory()
    
    chat = client.chats.create(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            system_instruction=f"You are {BOT_NAME}, a clever Python-built assistant.",
        ),
        history=past_history
    )

    print(f"=== {BOT_NAME.upper()} IS ONLINE ===")
    
    if not past_history:
        print(f"{BOT_NAME}: Hi! I don't think we've met. What's your name?")
    else:
        print(f"{BOT_NAME}: Welcome back! How can I help you today?")

    try:
        while True:
            user_input = input("\nYou: ").strip()
            if not user_input: continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                break

            print(f"{BOT_NAME} is thinking...", end="\r")

            try:
                response = chat.send_message(user_input)
                print(" " * 30, end="\r") 
                print(f"{BOT_NAME}: {response.text}")
                
                # Use chat.history (public) instead of _history (private)
                save_memory(chat.history)

            except Exception as e:
                print(f"\n[AI Error]: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        save_memory(chat.history)
        print(f"{BOT_NAME}: History saved. See ya!")

if __name__ == "__main__":
    start_mika()