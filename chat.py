import asyncio
import streamlit as st
from langgraph.graph import StateGraph

from graph.graph import GraphBuilder
from graph.state import State
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
import os
openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Travelerly Voice Assistant", page_icon="🧭")
st.title("Travelerly Voice Assistant")
st.write("Click 'Start interaction' to hear the greeting and speak your response.")

# Initialize session state
if "user_transcription" not in st.session_state:
    st.session_state.user_transcription = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False


def _init_graph():
    gb = GraphBuilder()
    # Ensure there is an underlying StateGraph
    if gb.builder is None:
        gb.builder = StateGraph(State)
    workflow = gb.build()
    return gb, workflow


def _extract_last_user_message(state_dict):
    msgs = state_dict.get("messages", []) or []
    for m in reversed(msgs):
        if isinstance(m, HumanMessage):
            return m.content
    return ""


async def _run_voice_interaction():
    gb, workflow = _init_graph()
    compiled = workflow.compile()
    # Because greeting_node is async, just use ainvoke for final state.
    placeholder = st.empty()
    placeholder.markdown("Running graph (async node)...")
    final_state = await compiled.ainvoke({"messages": []})
    user_text = _extract_last_user_message(final_state)
    return user_text


def run_interaction():
    try:
        # Manage event loop safely inside Streamlit
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            return asyncio.ensure_future(_run_voice_interaction())
        return loop.run_until_complete(_run_voice_interaction())
    except Exception as e:
        st.error(f"Interaction failed: {e}")
        return None


start = st.button("Start interaction", type="primary", disabled=st.session_state.is_running)
if start and not st.session_state.is_running:
    st.session_state.is_running = True
    st.info("Playing greeting... then speak after the tone / greeting finishes. Recording stops automatically after silence.")
    user_text = run_interaction()
    if asyncio.isfuture(user_text):
        st.warning("Background task started (event loop already running). Transcription will appear when done.")
    else:
        st.session_state.user_transcription = user_text
    st.session_state.is_running = False

if st.session_state.user_transcription:
    st.subheader("Your transcribed input:")
    st.write(st.session_state.user_transcription or "(empty)")

st.caption("Ensure your microphone is enabled and environment variable OPENAI_API_KEY is set before starting.")
