import streamlit as st
from groq import Groq
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Groq Chat",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- ADVANCED CUSTOM CSS (DARK THEME) ---
st.markdown("""
<style>
    /* 1. Main Background & Text */
    .stApp {
        background-color: #0E1117; /* Very dark grey */
        color: #FAFAFA;
    }

    /* 2. Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111111; /* Black sidebar */
        border-right: 1px solid #333;
    }
    
    /* Sidebar text and inputs */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {
        color: #E0E0E0 !important;
    }

    /* 3. Chat Message Containers */
    .stChatMessage {
        background-color: #1E1E1E; /* Dark grey bubbles */
        border: 1px solid #333;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }

    /* 4. User Message Specific Styling */
    /* Target the user message content specifically */
    [data-testid="stChatMessageContentUser"] {
        background: linear-gradient(135deg, #F55036 0%, #F58536 100%); /* Groq Orange/Red Gradient */
        color: white;
        border-radius: 15px;
        padding: 10px 15px;
    }
    /* Hide the default user avatar border */
    [data-testid="stChatMessageAvatarUser"] {
        background-color: transparent;
    }

    /* 5. Assistant Message Styling */
    [data-testid="stChatMessageContentAssistant"] {
        color: #E0E0E0;
    }

    /* 6. Input Box Styling */
    .stChatInput {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 12px;
    }
    /* Input text color */
    .stChatInput textarea {
        color: #FFFFFF !important;
    }
    
    /* 7. Buttons and Selectors in Sidebar */
    .stButton button {
        background-color: #333;
        color: white;
        border: 1px solid #555;
    }
    .stButton button:hover {
        background-color: #444;
        border-color: #F55036; /* Groq orange hover */
    }
    
    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        background-color: #222;
        border-color: #444;
        color: white;
    }

    /* 8. Titles */
    h1 {
        color: #FAFAFA;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0E1117; 
    }
    ::-webkit-scrollbar-thumb {
        background: #555; 
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    # Using markdown for the logo to ensure it fits the dark theme if external
    st.markdown("<h2 style='color: #F55036; font-weight: bold;'>⚡ Groq Chat</h2>", unsafe_allow_html=True)
    
    # API Key Input
    api_key = st.text_input("Enter your Groq API Key:", type="password", key="api_key_input")
    
    st.divider()
    
    # Model Selection
    model_options = {
        "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
        "Llama 3.1 70B (Smart)": "llama-3.1-70b-versatile",
        "Llama 3.2 11B Vision": "llama-3.2-11b-vision-preview"
    }
    selected_model_display = st.selectbox("Select Model", options=list(model_options.keys()))
    selected_model_id = model_options[selected_model_display]
    
    # System Prompt
    system_prompt = st.text_area(
        "System Instructions", 
        value="You are a helpful assistant.", 
        height=100
    )
    
    # Controls
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.rerun()
    
    st.divider()
    st.caption("Powered by Llama 3.1")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# --- Helper Function for Streaming ---
def stream_groq_response(client, messages, model):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"\n\n**Error:** {str(e)}"

# --- Main Chat Logic ---

# 1. Check for API Key
if not api_key:
    st.info("👈 Please enter your Groq API Key in the sidebar to start chatting.")
    st.stop()

# Initialize Client
try:
    client = Groq(api_key=api_key)
except Exception:
    st.error("Invalid API Key.")
    st.stop()

# Update system prompt in history if changed in sidebar
if st.session_state.messages[0]["role"] == "system":
    st.session_state.messages[0]["content"] = system_prompt

# 2. Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. Handle User Input
if prompt := st.chat_input("Type your message..."):
    # Display user message immediately
    st.chat_message("user").markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate and display assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        for chunk in stream_groq_response(client, st.session_state.messages, selected_model_id):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})