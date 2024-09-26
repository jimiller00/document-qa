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

# Function to read PDF
def read_pdf(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()
        return extracted_text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Function to create embeddings
def create_embedding(text, openai_client):
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small")
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Error creating embedding: {e}")
        return None

# Function to create the ChromaDB collection
def create_chromaDB_collection(collection, text, filename, openai_client):
    embedding = create_embedding(text, openai_client)
    if embedding:
        try:
            collection.add(
                documents=[text],
                ids=[filename],
                embeddings=[embedding]
            )
            return True
        except Exception as e:
            st.error(f"Error adding to ChromaDB collection: {e}")
    return False

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Main application
def main():
    st.title("PDF Search Application")

    # Initialize OpenAI client
    if 'openai_client' not in st.session_state:
        api_key = st.secrets["openai_key"]
        st.session_state.openai_client = OpenAI(api_key=api_key)

    # Initialize ChromaDB client and collection
    if 'chroma_client' not in st.session_state:
        st.session_state.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        st.session_state.collection = st.session_state.chroma_client.create_collection(name="pdf_collection")

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            # Save uploaded file temporarily
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read PDF
            pdf_text = read_pdf("temp.pdf")
            if pdf_text:
                # Add to ChromaDB collection
                if create_chromaDB_collection(st.session_state.collection, pdf_text, uploaded_file.name, st.session_state.openai_client):
                    st.success(f"Successfully processed and added {uploaded_file.name} to the collection.")
                else:
                    st.error(f"Failed to add {uploaded_file.name} to the collection.")
            
            # Remove temporary file
            os.remove("temp.pdf")

    # Topic selection
    topic = st.sidebar.selectbox("Topic", ('Generative AI', 'Text Mining', 'Data Science Overview'))

    # Search button
    if st.sidebar.button("Search"):
        with st.spinner("Searching..."):
            # Create embedding for the selected topic
            query_embedding = create_embedding(topic, st.session_state.openai_client)
            if query_embedding:
                # Query ChromaDB
                results = st.session_state.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3
                )

                # Display results
                st.subheader("Search Results")
                if results['documents'][0]:
                    for i in range(len(results['documents'][0])):
                        doc = results['documents'][0][i]
                        doc_id = results['ids'][0][i]
                        st.write(f"The following file/syllabus might be helpful: {doc_id}")
                        with st.expander("Show excerpt"):
                            st.write(doc[:500] + "...")  # Show first 500 characters
                else:
                    st.info("No relevant documents found.")

if __name__ == "__main__":
    main()