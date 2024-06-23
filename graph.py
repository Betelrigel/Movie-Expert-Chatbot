
import streamlit as st
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(
    url=st.secrets["your secret"],
    username=st.secrets["your username here"],
    password=st.secrets["your password here"],
    
)