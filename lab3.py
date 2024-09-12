import streamlit as st
import openai
from openai import OpenAI

 # Show title and description.
st.title("John's Chat Bot")    

OpenAI_model = st.sidebar.selectbox("Which model?", "Mini", "Regular")

if OpenAI_model == "Mini":
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = "gpt-4o"
# Create an OpenAI client.
if 'client' not in st.session_state:
    api_key = st.secrets["openai_key"]
    st.session_state.client = OpenAI(api_key=api_key)
if "messages" not in st.session_state:
    st.session_state["messages"] = \
        [{"role": "assistant", "content": "How can I help you?"}]
    
#
for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

#
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
    
    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages = st.session_state.messsages,
        stream=True)
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.append({"role": "assistant", "content": response})