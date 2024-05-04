import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO
import subprocess
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Roast Me Chef!!",
    page_icon="👨‍🍳",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.x.com/didntdrinkwater',
        'Report a bug': "https://github.com/younesbram",
        'About': "# This is a fun project that generates roasts in the style of Gordon Ramsay!"
    }
)

# Initialize session state variables
if 'roast' not in st.session_state:
    st.session_state['roast'] = None
if 'audio' not in st.session_state:
    st.session_state['audio'] = None
if 'audio_played' not in st.session_state:
    st.session_state['audio_played'] = False

def twitter_link(roast_text):
    twitter_text = f"{roast_text} @didntdrinkwater"
    encoded_twitter_text = urllib.parse.quote(twitter_text)
    st.markdown(f"[Share on Twitter](https://twitter.com/intent/tweet?text={encoded_twitter_text}) 🐦", unsafe_allow_html=True)

def media_options(uploaded_file):
    display_choice = st.selectbox("Choose display option:", ["Text", "Audio", "Video"])
    
    if display_choice == "Audio" and st.button('Play Roast Audio'):
        play_audio()

    elif display_choice == "Video" and st.button('Generate Video'):
        generate_video(uploaded_file)

def play_audio():
    if not st.session_state['audio']:
        # ElevenLabs API key
        xi_api_key = st.secrets["EV_API_KEY"]

        # Setup headers for ElevenLabs API
        headers_elevenlabs = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": xi_api_key
        }

        # Data for ElevenLabs API
        data_elevenlabs = {
            "text": st.session_state['roast'],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.8
            }
        }

        # API URL for ElevenLabs
        url_elevenlabs = "https://api.elevenlabs.io/v1/text-to-speech/xzE8ttx3TerLWjBcTn5v"

        # Making the API request to ElevenLabs
        response_elevenlabs = requests.post(url_elevenlabs, json=data_elevenlabs, headers=headers_elevenlabs)
        if response_elevenlabs.status_code == 200:
            st.session_state['audio'] = response_elevenlabs.content
            st.audio(st.session_state['audio'], format='audio/mp3')
        else:
            st.error("Failed to synthesize speech.")
    else:
        st.audio(st.session_state['audio'], format='audio/mp3')

def generate_video(uploaded_file):
    # Check if roast text is available and audio has not been generated yet
    if 'roast' in st.session_state and not st.session_state.get('audio'):
        # ElevenLabs API key
        xi_api_key = st.secrets["EV_API_KEY"]

        # Setup headers for ElevenLabs API
        headers_elevenlabs = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": xi_api_key
        }

        # Data for ElevenLabs API
        data_elevenlabs = {
            "text": st.session_state['roast'],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.6
            }
        }

        # API URL for ElevenLabs
        url_elevenlabs = "https://api.elevenlabs.io/v1/text-to-speech/xzE8ttx3TerLWjBcTn5v"

        # Making the API request to ElevenLabs
        response_elevenlabs = requests.post(url_elevenlabs, json=data_elevenlabs, headers=headers_elevenlabs)
        if response_elevenlabs.status_code == 200:
            st.session_state['audio'] = response_elevenlabs.content
        else:
            st.error("Failed to synthesize speech. Unable to generate video.")
            return  # Exit if audio cannot be generated

    # Check again if audio is available
    if st.session_state.get('audio'):
        # Prepare to generate video
        audio_file = 'output.mp3'
        video_file = 'output_video.mp4'
        with open(audio_file, 'wb') as f:
            f.write(st.session_state['audio'])
        subprocess.run([
            'ffmpeg', '-loop', '1', '-i', uploaded_file.name, '-i', audio_file,
            '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
            '-b:a', '192k', '-shortest', video_file
        ])
        st.video(video_file)
    else:
        st.error("Audio data is not available. Please try generating the audio first.")

def generate_roast(uploaded_file, anger_level):
    # Display processing GIF
    processing_gif = 'chefgifs/gif3.gif'
    st.image(processing_gif, use_column_width=True)

    # Convert image to base64 for API usage
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # OpenAI API key and headers
    api_key = st.secrets["OPENAI_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Define the mood of the roast based on the anger level
    mood = "not that angry" if anger_level < 50 else "very angry and lots of swearing"
    prompt = f"Generate a short roast about the food in the style of Gordon Ramsay. Mood: {mood}."

    # Payload for OpenAI API
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_str}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # API URL
    api_url = "https://api.openai.com/v1/chat/completions"

    # Making the API request
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        st.session_state['roast'] = response.json()['choices'][0]['message']['content']
        st.write(f"**Roast Generated:** {st.session_state['roast']}")
        # Share link for Twitter
        twitter_link(st.session_state['roast'])
    else:
        st.error(f"Failed to process the image. Status code: {response.status_code}, response: {response.text}")


# Title of the application
st.title('Roast Me Chef!!')

# Sidebar instructions
st.sidebar.header("Instructions")
st.sidebar.info("Upload an image, set the anger level, and get roasted in the style similar to Gordon Ramsay's roast!")
st.sidebar.markdown("Connect with me on Twitter [X.com/didntdrinkwater](https://www.x.com/didntdrinkwater) or on [GitHub/younesbram](https://github.com/younesbram) for more cool projects!")

# Display initial GIF
initial_gif = 'chefgifs/gif1.gif'
st.image(initial_gif, caption='Think yous a top chef innit?! Get ready to be roasted!', use_column_width=True)

# Image uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
anger_level = st.slider("Select the anger level:", 0, 100, 50)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    uploaded_gif = 'chefgifs/gif2.gif'
    st.image(uploaded_gif, caption='Click the button... Dont be scared..', use_column_width=True)

    if st.button("Roast/Rate my meal, Chef!") or st.session_state['roast']:
        if not st.session_state['roast']:
            # Process the roast generation
            generate_roast(uploaded_file, anger_level)
        else:
            # Display the existing roast and share link
            st.write(f"**Roast Generated:** {st.session_state['roast']}")
            twitter_link(st.session_state['roast'])

        # Option to play audio or generate video
        media_options(uploaded_file)
else:
    st.write("Upload an image to get started.")



