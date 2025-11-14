import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

llm = ChatGroq(
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name=st.secrets["GROQ_MODEL"],
    temperature=0.7
)

# Using HuggingFace embeddings as a free alternative
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)