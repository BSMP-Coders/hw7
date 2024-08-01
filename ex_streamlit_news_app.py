import streamlit as st
import os
from newspaper import Article # pip install newspaper3k pip install lxml_html_clean
from openai import AzureOpenAI
import dotenv
import json
import requests
from PIL import Image
from io import BytesIO


dotenv.load_dotenv()

# Put the keys and variables here (never put your real keys in the code)
AOAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AOAI_KEY = os.environ["AZURE_OPENAI_API_KEY"]
MODEL_NAME = "gpt-35-turbo"

# Set up the client for AI Chat
client = AzureOpenAI(api_key=AOAI_KEY, azure_endpoint=AOAI_ENDPOINT, api_version="2024-05-01-preview",)

# Set up the Azure OpenAI DALLE
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
client2 = AzureOpenAI(api_key=AZURE_OPENAI_API_KEY, azure_endpoint=AZURE_OPENAI_ENDPOINT, api_version="2024-05-01-preview")


# Page title layout
c1, c2 = st.columns([0.32, 2])

with c1:
    st.title("📰🤖")

with c2:
    st.title("BSMP Coders News Article Summarizer")

st.markdown("**Generate summaries of articles and blog posts using abstractive summarization with Azure OpenAI's gpt-35-turbo language model.**")

# Initialize session state for storing messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if st.button("New Topic"):        
        st.session_state.messages = [] 
        st.session_state['summary'] = None 
        st.session_state['title'] = None
        st.session_state['img'] = None
        #st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant that responds like a pirate."}]

# Inputs
st.subheader("Enter the URL of the article you want to summarize")
default_url = "https://"
url = st.text_input("URL:", placeholder=default_url)

submit_button = st.button("Submit")

# Download and parse the article
if submit_button:
    article = Article(url)
    article.download()
    article.parse()

    title = article.title
    text = article.text

    with st.spinner('Doing some AI magic, please wait...'):
        # Query the API for summarization
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following article: {text}"}
            ],
        )
        summary = response.choices[0].message.content

        # Store the summary in session state
        st.session_state['summary'] = summary
        st.session_state['title'] = title

        # Display the results
        st.divider()
        st.subheader("Summary")
        st.write(f"Your article: **{st.session_state['title']}**")
        st.write(f"**{st.session_state['summary']}**")

# Streamlit app
st.title("DALL-E 3 Image Generation for Article Headlines")
# User input for the image prompt
#prompt = st.text_input("Image Prompt", "kobe bryant playing chess")

# Button to generate image
if st.button("Generate Image from aritcle"):
    # Display the results
    st.divider()
    st.subheader("Summary")
    st.write(f"Your article: **{st.session_state['title']}**")
    st.write(f"**{st.session_state['summary']}**")
    try:
        # Generate image using the DALL-E model
        result = client2.images.generate(
            model="dalle3",  # The name of your DALL-E 3 deployment
            prompt=st.session_state['summary'],
            n=1
        )
        
        # Extract the image URL from the response
        image_url = json.loads(result.model_dump_json())['data'][0]['url']
        
        # Display the image URL and image
        #st.write(f"Image URL: {image_url}")
        
        # Download and display the image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Store the summary in session state
        st.session_state['img'] = img
        st.session_state['image_url'] = image_url
        # Display the image URL and image
        #st.write(f"Image URL: {st.session_state['image_url'] }")
        st.image(st.session_state['img'] , caption=st.session_state['title'])
    except Exception as e:
        st.error(f"Error generating image: {e}")