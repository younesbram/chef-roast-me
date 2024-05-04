import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO
import random
import urllib.parse
import os
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
    
    if st.button("Roast/Rate my meal, Chef!"):
        # Display processing GIF
        processing_gif = 'chefgifs/gif3.gif'
        st.image(processing_gif, use_column_width=True)
        
        # Convert image to base64 for API usage
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # OpenAI API key
        api_key = st.secrets["OPENAI_API_KEY"]  # 

        # Setup headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Define the mood of the roast based on the anger level
        mood = "not that angry" if anger_level < 50 else "very angry and swearing"
        prompt = f"Generate a roast in the style of Gordon Ramsay. Mood: {mood}."

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
            roast = response.json()['choices'][0]['message']['content']
            st.write(f"**Roast Generated:** {roast}")
            
            # Share link for Twitter
            twitter_text = f"{roast} @didntdrinkwater"
            encoded_twitter_text = urllib.parse.quote(twitter_text)
            url = f"https://twitter.com/intent/tweet?text={twitter_text}"
            st.markdown(f"[Share on Twitter](https://twitter.com/intent/tweet?text={encoded_twitter_text}) 🐦", unsafe_allow_html=True)
        else:
            st.error(f"Failed to process the image. Status code: {response.status_code}, response: {response.text}")
else:
    st.write("Upload an image to get started.")
