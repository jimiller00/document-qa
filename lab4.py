import streamlit as st
import openai
import chromadb
from openai import OpenAI

# Function to limit message history
def trim_message_history(messages, max_memory):
    if len(messages) > max_memory:
        return messages[-max_memory:]  # Keep only the most recent messages
    return messages

def add_to_collection(collection, text, filename):
    openai_client = st.session_state.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding]
    )

add_to_collection()




 # Show title and description.
st.title("John's Chat Bot")    

OpenAI_model = st.sidebar.selectbox("Which model?", ("Mini", "Regular"))

if OpenAI_model == "Mini":
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = "gpt-4o"

# Create an OpenAI client.
if 'client' not in st.session_state:
    api_key = st.secrets["openai_key"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state["waiting_for_more_info"] = False  # Track if the bot is waiting for more info answer

# Set up a separate list for behavior modification
bot_behavior_messages = {
    "role": "system", 
    "content": (
        "Answer the question simply for a 10-year-old."
        "After answering, ask 'DO YOU WANT MORE INFO?' If the user says 'yes' or any other affirmative, provide more information. "
        "If they say 'no' or any other form of denial, ask them what other question they have."
        "Be sure to do this for every single question the user asks."
    )
}

# Define the maximum number of messages the bot can remember
MAX_MEMORY_MESSAGES = 5

# display conversation
for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

# user inputs prompt
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create a new message list combining user history and bot behavior
    message_history_for_bot = st.session_state.messages

    # Trim message history to keep it within memory limits
    message_history_for_bot = [bot_behavior_messages] + trim_message_history(message_history_for_bot, MAX_MEMORY_MESSAGES)

    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages = message_history_for_bot,
        stream=True)
    
    # display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    # add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})