import streamlit as st
from openai import OpenAI
import re
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Initialize the speech recognizer
recognizer = sr.Recognizer()


def record_audio():
    """Record audio from microphone and return the audio data"""
    try:
        with sr.Microphone() as source:
            st.write("🎤 Listening... Speak now!")
            # Adjust the ambient noise level
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return audio
    except Exception as e:
        st.error(f"Error recording audio: {str(e)}")
        return None


def speech_to_text(audio_data):
    """Convert speech to text using Google Speech Recognition"""
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio. Please try again.")
        return None
    except sr.RequestError as e:
        st.error(f"❌ Could not request results from speech recognition service: {e}")
        return None


def text_to_speech(text):
    """Convert text to speech using gTTS"""
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts = gTTS(text=text, lang='en')
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")
        return None


# Streamlit application
st.title("🎙️ BOLNA - Voice-Enabled Assistant")

# Session state for storing the audio file path
if 'audio_file_path' not in st.session_state:
    st.session_state.audio_file_path = None

# Add a radio button for input method selection
input_method = st.radio(
    "Choose input method:",
    ("Text Input", "Voice Input")
)

user_input = ""

if input_method == "Text Input":
    user_input = st.text_input("Enter your question:", "What is my laptop not turning on?")
else:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Start Recording"):
            with st.spinner("🎙️ Recording..."):
                audio_data = record_audio()
                if audio_data:
                    user_input = speech_to_text(audio_data)
                    if user_input:
                        st.success("🎉 Recording successful!")
                        st.write("You said:", user_input)
                    else:
                        st.error("Please try speaking again")

# Process input and generate response
if user_input:
    prompt = (
        f"Answer the following question related to Lenovo Laptop in a very specific manner, "
        f"providing the exact cause and the solution of the customer's problems; Do not elaborate a lot "
        f"unless specifically asked in the user query. Provide nearby locations for Service centres respectively as the user might deem necessary, "
        f"included with links. Act as a complete helpful assistant:\n\n{user_input}"
    )

    if st.button("Get Response"):
        # Show spinner while processing
        with st.spinner("🤔 Processing your request..."):
            try:
                completion = client.chat.completions.create(
                    model="meta/llama-3.1-405b-instruct",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=1024,
                    stream=True
                )

                response = ""
                response_placeholder = st.empty()

                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        response += chunk.choices[0].delta.content
                        response_placeholder.markdown(response)

                # Convert response to speech
                st.write("🔊 Audio Response:")
                if st.session_state.audio_file_path:
                    try:
                        os.unlink(st.session_state.audio_file_path)
                    except:
                        pass

                st.session_state.audio_file_path = text_to_speech(response)
                if st.session_state.audio_file_path:
                    with open(st.session_state.audio_file_path, 'rb') as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/mp3')

                # # Extract and format citations
                # citations = re.findall(r'\[(.*?)\]\((.*?)\)', response)
                # if citations:
                #     st.write("📚 Citations:")
                #     for text, link in citations:
                #         st.write(f"[{text}]({link})")

            except Exception as e:
                st.error(f"Error processing request: {str(e)}")

# Add setup instructions in the sidebar
st.sidebar.title("📋 Setup Instructions")
st.sidebar.markdown("""
1. Install required packages:
```bash
pip install streamlit openai SpeechRecognition gtts pyaudio
```

2. Ensure your microphone is connected and working
3. Allow microphone access when prompted
""")

# Cleanup on session end
if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
    try:
        os.unlink(st.session_state.audio_file_path)
    except:
        pass