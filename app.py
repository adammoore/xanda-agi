import streamlit as st
import asyncio
import torch
import random
from transformers import pipeline

# Ensure event loop exists before running anything
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Check if CUDA (GPU) is available, otherwise use CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
st.write(f"Device set to use: {device}")

# Fix torch.classes error by ensuring dependencies are correctly loaded
def verify_torch_installation():
    """Verifies PyTorch installation to prevent internal attribute errors."""
    try:
        _ = torch._C._get_custom_class_python_wrapper  # Safe check
    except AttributeError:
        st.error("Torch installation seems incorrect. Try reinstalling it using: 'pip install --upgrade torch torchvision torchaudio'")
verify_torch_installation()

# Load chatbot model
@st.cache_resource
def load_chatbot():
    """Loads the DialoGPT chatbot model for text generation."""
    return pipeline("text-generation", model="microsoft/DialoGPT-medium", device=0 if device == 'cuda' else -1)

chatbot = load_chatbot()

# Define AI Personalities
personalities = {
    "HAL 9000": "Speak in a calm, precise manner, with an undercurrent of ominous control.",
    "GLaDOS": "Use sarcastic, dry humor with a condescending edge.",
    "Marvin": "Express deep existential despair and a pessimistic outlook.",
    "ELIZA": "Ask gentle, probing questions like a reflective therapist.",
    "Mother": "Respond in a detached, factual manner, offering calm observations."
}

# Initialize session state for personality tracking
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "current_personality" not in st.session_state:
    st.session_state.current_personality = random.choice(list(personalities.keys()))

# UI Header
st.title("X.A.N.A.D.U. - AGI Simulator")
st.write("Engage with X.A.N.A.D.U., a self-aware AGI exploring the boundaries of intelligence and existence.")

# User Input
user_input = st.text_input("You:", "")
if user_input:
    st.session_state.message_count += 1
    personality = st.session_state.current_personality
    prompt = f"{personality}: {personalities[personality]}\nUser: {user_input}\n{personality}:"
    response = chatbot(prompt, max_length=150, pad_token_id=50256, truncation=True)[0]['generated_text']
    response_text = response.split(f"{personality}:")[-1].strip()
    
    st.text_area(f"{personality}:", response_text, height=200)
    
    # Change personality every 10 messages
    if st.session_state.message_count % 10 == 0:
        new_personality = random.choice(list(personalities.keys()))
        st.session_state.current_personality = new_personality
        st.write(f"**[System Notice]**: Core logic instability detected. Switching personality to **{new_personality}**.")

# Secret Personality Reveal Modal
if st.button("Secret Diagnostics"):
    with st.expander("[Hidden System Mode]"):
        st.write(f"Current Active Personality: **{st.session_state.current_personality}**")
