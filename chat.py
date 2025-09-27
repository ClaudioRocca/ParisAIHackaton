import asyncio
from fpdf import FPDF
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

# ---- New user input controls ----
st.subheader("Trip Preferences")
# Number of people
st.number_input("How many people are traveling?", min_value=1, max_value=50, value=1, step=1, key="ui_people_number")
# Travel context (as requested: family, girlfriend, work, alone)
st.radio("Travel context", ["Family", "Girlfriend", "Work", "Alone"], horizontal=True, key="ui_travel_context")
# Budget per person per night
st.slider("Max budget per person per night (USD)", min_value=50, max_value=2000, value=200, step=10, key="ui_budget_pppn")
# ---------------------------------

# Initialize session state
if "user_transcription" not in st.session_state:
    st.session_state.user_transcription = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "final_state" not in st.session_state:
    st.session_state.final_state = None


def _init_graph():
    gb = GraphBuilder()
    # Ensure there is an underlying StateGraph
    if gb.builder is None:
        gb.builder = StateGraph(State)
    workflow = gb.build()
    return gb, workflow


def _extract_last_user_message(state_obj):
    # state_obj can be a State instance or dict
    try:
        messages = None
        if hasattr(state_obj, "get"):
            messages = state_obj.get("messages", [])
        elif hasattr(state_obj, "messages"):
            messages = getattr(state_obj, "messages")
        messages = messages or []
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                return m.content
    except Exception:
        pass
    return ""


async def _run_voice_interaction():
    gb, workflow = _init_graph()
    compiled = workflow.compile()
    placeholder = st.empty()
    placeholder.markdown("Running graph (async node)...")
    final_state = await compiled.ainvoke({"messages": []})
    return final_state


def run_interaction():
    try:
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
    result = run_interaction()
    if asyncio.isfuture(result):
        st.warning("Background task started (event loop already running). Transcription will appear when done.")
    else:
        st.session_state.final_state = result
        st.session_state.user_transcription = _extract_last_user_message(result)
    st.session_state.is_running = False

if st.session_state.user_transcription:
    st.subheader("Your transcribed input:")
    st.write(st.session_state.user_transcription or "(empty)")

# Display extracted structured state fields
if st.session_state.final_state:
    st.subheader("Extracted Travel Plan State")
    state_obj = st.session_state.final_state
    # Convert to dict
    if hasattr(state_obj, "dict"):
        data = state_obj.dict()
    elif isinstance(state_obj, dict):
        data = state_obj
    else:
        data = {}
    key_fields = ["destination", "people_number", "interests", "travel_dates", "budget", "activities"]
    cols = st.columns(2)
    for i, field in enumerate(key_fields):
        val = data.get(field)
        if val not in (None, "", []):
            with cols[i % 2]:
                st.markdown(f"**{field.replace('_',' ').title()}:** {val}")

    # Show user UI inputs explicitly (overrides / supplements extracted state)
    with st.expander("Your UI Inputs", expanded=False):
        st.write(f"People (UI): {st.session_state.ui_people_number}")
        st.write(f"Context: {st.session_state.ui_travel_context}")
        st.write(f"Max Budget PPPN: ${st.session_state.ui_budget_pppn}")

    # Show messages (last few)
    msgs = data.get("messages") or []
    if msgs:
        st.markdown("**Conversation Messages (last 5):**")
        for m in msgs[-5:]:
            role = getattr(m, "type", getattr(m, "role", "message"))
            content = getattr(m, "content", str(m))
            st.write(f"{role}: {content}")


if st.button("Generate PDF Report"):
        # Build the PDF
        state_obj = st.session_state.final_state
        if hasattr(state_obj, "dict"):
            data = state_obj.dict()
        elif isinstance(state_obj, dict):
            data = state_obj
        else:
            data = {}

        # Provide defaults if missing
        dest = data.get("destination", "Unknown Destination")
        # Override with UI inputs if present
        people = st.session_state.get("ui_people_number") or data.get("people_number", "N/A")
        dates = data.get("travel_dates", "")
        interests = data.get("interests", "")
        budget = data.get("budget", "")  # original budget (if extracted)
        activities = data.get("activities", "")
        travel_context = st.session_state.get("ui_travel_context", "")
        budget_pppn = st.session_state.get("ui_budget_pppn", None)

        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        header_text = f"{dest}"
        pdf.cell(0, 10, header_text, ln=True, align="C")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 12)
        subtitle = f"Dates: {dates}   |   Number of people: {people}"
        pdf.cell(0, 8, subtitle, ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Travel Plan Details", ln=True)
        pdf.ln(4)

        pdf.set_font("Helvetica", "", 12)
        if travel_context:
            pdf.cell(0, 6, f"Context: {travel_context}", ln=True)
        if interests:
            pdf.multi_cell(0, 6, f"Interests: {interests}")
            pdf.ln(2)
        if budget:
            pdf.cell(0, 6, f"Overall Budget: {budget}", ln=True)
        if budget_pppn is not None:
            pdf.cell(0, 6, f"Max Budget / Person / Night: ${budget_pppn}", ln=True)
        pdf.ln(4)

        if activities:
            pdf.multi_cell(0, 6, f"Planned Activities:\n{activities}")
            pdf.ln(4)

        # Output to a bytes buffer (handle both str and bytes/bytearray from fpdf versions)
        pdf_out = pdf.output(dest="S")
        if isinstance(pdf_out, (bytes, bytearray)):
            pdf_bytes = bytes(pdf_out)
        else:  # str
            pdf_bytes = pdf_out.encode("latin1")

        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"TravelPlan_{dest.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        st.success("PDF Report is ready! Use the button above to download it.")

st.caption("Ensure your microphone is enabled and environment variable OPENAI_API_KEY is set before starting.")
