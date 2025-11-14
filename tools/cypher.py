from langchain.chains import GraphCypherQAChain

from llm import llm
from graph import graph

from tools.cypher import cypher_qa

from langchain.prompts.prompt import PromptTemplate

cypher_qa = GraphCypherQAChain.from_llm(
    llm,          # (1)
    graph=graph,  # (2)
)

tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True
        ),
    Tool.from_function(
        name="Vector Search Index",
        description="Provides information about movie plots using Vector Search",
        func = kg_qa,
        return_direct=True
    ),
    Tool.from_function(
        name="Graph Cypher QA Chain",  # (1)
        description="Provides information about Movies including their Actors, Directors and User reviews", # (2)
        func = cypher_qa, # (3)
        return_direct=True
    ),
]

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about movies and provide recommendations.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Fine Tuning:

For movie titles that begin with "The", move "the" to the end. For example "The 39 Steps" becomes "39 Steps, The" or "the matrix" becomes "Matrix, The".


Schema:
{schema}

Question:
{question}

Cypher Query:
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt
)