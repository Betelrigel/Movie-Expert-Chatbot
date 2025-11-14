import streamlit as st

# tag::write_message[]
def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)
# end::write_message[]


def get_session_id():
    """Return a stable session id for the current Streamlit session.

    Stores a UUID in `st.session_state['session_id']` if missing.
    """
    if "session_id" not in st.session_state:
        try:
            import uuid
            st.session_state["session_id"] = str(uuid.uuid4())
        except Exception:
            # Fallback to a simple counter if uuid isn't available
            st.session_state.setdefault("_sid_counter", 0)
            st.session_state["_sid_counter"] += 1
            st.session_state["session_id"] = f"session-{st.session_state['_sid_counter']}"
    return st.session_state["session_id"]
