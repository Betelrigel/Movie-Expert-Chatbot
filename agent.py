
"""Agent implementation for the chatbot.

This module creates a movie-chat tool, initializes an agent with
conversation memory (Neo4j-backed if available), and exposes
`generate_response(user_input)` which the Streamlit UI calls.

The implementation is defensive: if optional packages (Neo4j
history, LangChain hub prompt, etc.) are missing or a model is
unavailable, it will fall back to a simpler direct-LLM call and
return helpful error messages.
"""

from typing import Optional
import logging

from langchain_core.prompts import ChatPromptTemplate

# Import Tool defensively because its location changed across langchain versions
try:
    from langchain_core.tools import Tool
except Exception:
    try:
        from langchain.tools.base import Tool  # newer/older layouts
    except Exception:
        # Fallback shim: minimal Tool replacement so module can import.
        class Tool:
            def __init__(self, name, description, func):
                self.name = name
                self.description = description
                self.func = func

            @classmethod
            def from_function(cls, name: str, description: str, func, return_direct: bool = False):
                return cls(name=name, description=description, func=func)

from llm import llm, embeddings
from graph import graph
from utils import get_session_id
import streamlit as st

logger = logging.getLogger(__name__)


# Build a movie chat prompt + chain
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a movie expert providing information about movies."),
        ("human", "{input}"),
    ]
)

movie_chat = chat_prompt | llm


# Expose as a Tool for the agent to call
tools = [
    Tool.from_function(
        name="General Chat",
        description="For general movie chat not covered by other tools",
        func=movie_chat.invoke,
    )
]


def get_memory(session_id: str):
    """Return a conversation-memory object for the given session_id.

    Prefer Neo4j-backed history when available; otherwise return None.
    The agent runner will handle None by not persisting history.
    """
    try:
        from langchain_neo4j import Neo4jChatMessageHistory

        return Neo4jChatMessageHistory(session_id=session_id, graph=graph)
    except Exception as e:
        logger.info("Neo4jChatMessageHistory unavailable, continuing without persistent history: %s", e)
        return None


# Initialize agent and runnable with history when possible
chat_agent = None

try:
    # Pull a reusable agent prompt from the hub (optional)
    try:
        from langchain import hub
        agent_prompt = hub.pull("hwchase17/react-chat")
    except Exception:
        agent_prompt = None

    # Create ReAct agent and executor
    try:
        from langchain_core.agents import create_react_agent
        from langchain.agents import AgentExecutor
        from langchain_core.runnables.history import RunnableWithMessageHistory

        if agent_prompt is None:
            # If hub prompt not available, use a simple instruction prompt
            agent_prompt = chat_prompt

        agent = create_react_agent(llm, tools, agent_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Wrap with history if possible
        chat_agent = RunnableWithMessageHistory(
            agent_executor,
            get_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
    except Exception as e:
        logger.info("Could not create full AgentExecutor+RunnableWithMessageHistory: %s", e)
        # Fall back to using the LLM directly via the movie_chat tool
        chat_agent = None
except Exception as e:
    logger.exception("Unexpected error initializing agent: %s", e)
    chat_agent = None


def generate_response(user_input: str) -> str:
    """Handler called by Streamlit UI to get a response for `user_input`.

    This will invoke the chat_agent with conversation history when
    available. If chat_agent couldn't be initialized, it falls back
    to calling the `movie_chat` chain directly.
    """
    session_id = get_session_id()

    # If we have a full agent runnable and Neo4j-backed memory is configured, call it with session_id.
    # If Neo4j is not configured (graph is None) the RunnableWithMessageHistory won't persist, so
    # we prefer to use a Streamlit session-backed history fallback below.
    if chat_agent is not None and graph is not None:
        try:
            response = chat_agent.invoke(
                {"input": user_input}, {"configurable": {"session_id": session_id}}
            )
            # AgentExecutor/RunnableWithMessageHistory returns a dict-like result
            if isinstance(response, dict) and "output" in response:
                return response["output"]
            # Otherwise, string-ish
            return str(response)
        except Exception as e:
            logger.exception("Agent invocation failed: %s", e)
            err = str(e)
            if "model_decommissioned" in err or "model_not_found" in err:
                return (
                    "The configured Groq model is not available (decommissioned or no access). "
                    "Please update `GROQ_MODEL` in `.streamlit/secrets.toml` to a supported model and restart.\n\n"
                    f"Error details: {err}"
                )
            return f"Agent error: {err}"

    # Fallback: use Streamlit session_state as conversation memory and call the movie_chat chain.
    try:
        # Build a conversation history string from recent messages in session state
        history_lines = []
        msgs = st.session_state.get("messages", [])
        # Include up to the last 10 messages to keep prompt size reasonable
        for m in msgs[-10:]:
            role = m.get("role", "user")
            content = m.get("content", "")
            # Normalize role names
            if role == "assistant":
                speaker = "Assistant"
            else:
                speaker = "User"
            history_lines.append(f"{speaker}: {content}")

        history_text = "\n".join(history_lines)

        if history_text:
            combined_input = f"Conversation so far:\n{history_text}\n\nUser: {user_input}"
        else:
            combined_input = user_input

        formatted = chat_prompt.format(input=combined_input)
        response = movie_chat.invoke(formatted)
        # movie_chat invocation usually returns a string or object with `content`
        if hasattr(response, "content"):
            return response.content
        return str(response)
    except Exception as e:
        logger.exception("Fallback LLM call failed: %s", e)
        return f"An error occurred while calling the language model: {e}"