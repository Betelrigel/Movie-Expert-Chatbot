
import streamlit as st
import logging

logger = logging.getLogger(__name__)

try:
    from langchain_community.graphs import Neo4jGraph
except Exception:
    Neo4jGraph = None

# Read Neo4j credentials from Streamlit secrets using the expected keys.
NEO4J_URI = st.secrets.get("NEO4J_URI", "").strip()
NEO4J_USERNAME = st.secrets.get("NEO4J_USERNAME", "").strip()
NEO4J_PASSWORD = st.secrets.get("NEO4J_PASSWORD", "").strip()

# If the values look like placeholders (contain braces or the word "instance"),
# treat them as missing so we don't attempt to connect and raise confusing errors.
def _looks_placeholder(value: str) -> bool:
    if not value:
        return True
    if "{" in value or "}" in value:
        return True
    if "instance" in value.lower():
        return True
    return False

if _looks_placeholder(NEO4J_URI) or _looks_placeholder(NEO4J_USERNAME) or _looks_placeholder(NEO4J_PASSWORD):
    logger.info("Neo4j credentials appear to be placeholders or missing; Neo4j graph will be disabled.")
    graph = None
else:
    if Neo4jGraph is None:
        logger.info("langchain_community.graphs.Neo4jGraph not available; Neo4j graph will be disabled.")
        graph = None
    else:
        try:
            graph = Neo4jGraph(
                url=NEO4J_URI,
                username=NEO4J_USERNAME,
                password=NEO4J_PASSWORD,
            )
        except Exception as e:
            logger.warning("Could not initialize Neo4jGraph (will continue without graph): %s", e)
            graph = None