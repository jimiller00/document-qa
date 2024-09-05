import streamlit as st
import openai
from openai import OpenAI

def check_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True

# Show title and description.
st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

        # Create an OpenAI client.
# Fetch the API key from Streamlit's secrets
openai.api_key = st.secrets["openai_key"]

client = OpenAI(api_key=st.secrets["openai_key"])
        # Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
            "Upload a document (.txt or .md)", type=("txt", "md")
        )

        # Ask the user for a question via `st.text_area`.
question = st.text_area(
            "Now ask a question about the document!",
            placeholder="Can you give me a short summary?",
            disabled=not uploaded_file,
        )

if uploaded_file and question:
            
            # Process the uploaded file and question.
            document = uploaded_file.read().decode()
            messages = [
                    {
                    "role": "user",
                    "content": f"Here's a document: {document} \n\n---\n\n {question}",
                }               
                ]

            # Generate an answer using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                temperature=1
            )

            # Stream the response to the app using `st.write_stream`.
            st.write_stream(stream)