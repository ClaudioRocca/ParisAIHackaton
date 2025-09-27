"""
Streamlit UI to run the DataGatherer graph and visualize the resulting state.
Run with:  streamlit run data_gather_interface.py
"""
import streamlit as st
from datetime import date
from graph.state import State
from graph.data_gatherer import DataGatherer
from langgraph.graph import StateGraph
import json
import time

st.set_page_config(page_title="Data Gatherer", page_icon="🧭", layout="wide")

st.title("🧭 Travel Data Gatherer")
st.write("Fill in (or leave blank) the initial information and run the data gatherer graph to visualize the resulting state.")

@st.cache_resource(show_spinner=False)
def get_workflow():
    dg = DataGatherer()
    if dg.builder is None:
        dg.builder = StateGraph(State)
    workflow = dg.build()
    return dg, workflow.compile()

def build_initial_state_form():
    st.subheader("Initial User Inputs")
    with st.form("initial_state_form"):
        destination = st.text_input("Destination", value="Paris")
        people_number = st.number_input("Number of People", min_value=1, value=2)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2025, 12, 10))
        with col2:
            end_date = st.date_input("End Date", value=date(2025, 12, 15))
        budget = st.number_input("Budget (total per person)", min_value=0.0, value=2000.0, step=100.0)
        interests = st.multiselect(
            "Interests", 
            ["culture", "food", "sport", "art", "history", "nature", "nightlife"], 
            default=["culture", "food", "sport"]
        )
        activities_text = st.text_area(
            "Specific Activities (comma separated)", 
            value="fine dining, museum tours"
        )
        submitted = st.form_submit_button("🚀 Run Data Gatherer Graph", type="primary")
    if submitted:
        activities = [a.strip() for a in activities_text.split(',') if a.strip()]
        travel_dates = [start_date.isoformat(), end_date.isoformat()]
        return {
            "destination": destination or None,
            "people_number": int(people_number),
            "interests": interests,
            "travel_dates": travel_dates,
            "budget": float(budget) if budget else None,
            "activities": activities,
            "messages": []  # required by MessagesState
        }
    return None

initial_state_input = build_initial_state_form()

st.divider()

if initial_state_input is not None:
    st.subheader("Graph Execution")
    placeholder = st.empty()
    with st.spinner("Running data gatherer graph..."):
        dg, compiled = get_workflow()
        start_t = time.time()
        # Invoke the graph with the initial state fields
        try:
            final_state: State = compiled.invoke(initial_state_input)
            elapsed = time.time() - start_t
            placeholder.success(f"Graph completed in {elapsed:.2f}s")
        except Exception as e:
            placeholder.error(f"Graph failed: {e}")
            st.stop()

    st.subheader("Resulting State")
    # Convert to dict (pydantic's model_dump if available)
    try:
        state_dict = final_state.model_dump()
    except Exception:
        # Fallback manual extraction
        state_dict = {
            "destination": getattr(final_state, "destination", None),
            "people_number": getattr(final_state, "people_number", None),
            "interests": getattr(final_state, "interests", None),
            "travel_dates": getattr(final_state, "travel_dates", None),
            "budget": getattr(final_state, "budget", None),
            "activities": getattr(final_state, "activities", None),
            "messages_count": len(getattr(final_state, "messages", [])),
        }

    cols = st.columns(3)
    with cols[0]:
        st.metric("Destination", state_dict.get("destination") or "—")
        st.metric("People", state_dict.get("people_number") or 0)
        st.metric("Budget", state_dict.get("budget") if state_dict.get("budget") is not None else 0)
    with cols[1]:
        st.write("**Interests**")
        st.write(", ".join(state_dict.get("interests", []) ) or "—")
        st.write("**Activities**")
        st.write(", ".join(state_dict.get("activities", []) ) or "—")
    with cols[2]:
        st.write("**Travel Dates**")
        if state_dict.get("travel_dates"):
            st.write(" → ".join(state_dict.get("travel_dates")))
        else:
            st.write("—")
        st.write("**Messages in State**")
        st.write(state_dict.get("messages_count", 0))

    with st.expander("Raw State JSON"):
        st.code(json.dumps(state_dict, indent=2), language="json")

    st.info("Currently the data_gatherer node does not modify the state. Integrate tool calls and state updates inside graph nodes to see changes here.")
else:
    st.info("Submit the form above to run the data gatherer graph.")
