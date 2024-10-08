import streamlit as st
import os
import openai
from PyPDF2 import PdfReader
from openai import OpenAI


__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb
from chromadb.config import Settings

def read_pdf(pdf_file_path):
    # Create a PDF reader object
    reader = PdfReader(pdf_file_path)
    # Initialize an empty string to store the extracted text
    extracted_text = ""
    # Loop through all pages in the PDF and extract text
    for page in reader.pages:
        extracted_text += page.extract_text()
    return extracted_text

# Function to create the ChromaDB collection
def create_chromaDB_collection(collection, text, filename):
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small")
    
    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding]
    )


# Initialize OpenAI client
if 'openai_client' not in st.session_state:
    api_key = st.secrets["openai_key"]
    st.session_state.openai_client = OpenAI(api_key=api_key)

if 'chroma_client' not in st.session_state:
    chroma_settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_db"
    )
# Create or get the collection and store it in st.session_state.Lab4_vectorDB
    chroma_client = chromadb.Client(settings=chroma_settings)
    st.session_state.Lab4_vectorDB = st.session_state.chroma_client.get_or_create_collection(name="pdf_collection")
    st.session_state.chroma_client = chromadb.Client()

else:
    # Retrieve the existing collection from session state
    chroma_client = st.session_state.chroma_client




topic = st.sidebar.selectbox("Topic",('Generative AI', 'Text Mining', 'Data ScienceOverview'))

openai_client = st.session_state.client
response = openai_client.embeddings.create(
    input = topic,
    model = "text-embedding-3-small"
)

query_embedding = response.data[0].embedding

collection = st.session_state.Lab4_vectorDB
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

for i in range(len(results['documents'][0])):
    doc = results['documents'][0][i]
    doc_id = results['ids'][0][i]
    st.write(f"The following file/syllabus might be helpful: {doc_id} ") 