import streamlit as st
from datetime import date
import json
import time
from graph.state import State
from graph.data_gatherer import DataGatherer
from langgraph.graph import StateGraph
# --- Graph / Workflow helpers -------------------------------------------------

def _build_compiled_workflow():
    """Create (and cache) the compiled workflow for the DataGatherer graph."""
    dg = DataGatherer()
    if dg.builder is None:
        dg.builder = StateGraph(State)
    workflow = dg.build()
    return dg, workflow.compile()

# Streamlit resource cache so we don't rebuild on every interaction
@st.cache_resource(show_spinner=False)
def get_compiled():
    return _build_compiled_workflow()

# --- UI: Initial State Form ---------------------------------------------------

def initial_state_form():
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
            default=["culture", "food", "sport"],
        )
        activities_text = st.text_area(
            "Specific Activities (comma separated)",
            value="fine dining, museum tours",
        )
        submitted = st.form_submit_button("🚀 Run Data Gatherer Graph", type="primary")
    if not submitted:
        return None
    activities = [a.strip() for a in activities_text.split(',') if a.strip()]
    travel_dates = [start_date.isoformat(), end_date.isoformat()]
    return {
        "destination": destination or None,
        "people_number": int(people_number),
        "interests": interests,
        "travel_dates": travel_dates,
        "budget": float(budget) if budget else None,
        "activities": activities,
        "messages": [],  # MessagesState requirement
    }

# --- Main Run / Visualization -------------------------------------------------

def main():
    st.set_page_config(page_title="Data Gatherer", page_icon="🧭", layout="wide")
    st.title("🧭 Travel Data Gatherer")
    st.write("Configure initial trip info, run the graph, and inspect the resulting state.")
    
    # Add LightPanda testing section
    with st.expander("🔧 LightPanda API Testing", expanded=False):
        st.write("Test your LightPanda API configuration before running the data gatherer.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Test LightPanda Connection"):
                with st.spinner("Testing LightPanda API..."):
                    dg = DataGatherer()
                    success = dg.test_lightpanda_setup()
                    if success:
                        st.success("✅ LightPanda API is working correctly!")
                    else:
                        st.error("❌ LightPanda API connection failed. Check logs for details.")
        
        with col2:
            if st.button("🔍 Run Network Diagnostics"):
                with st.spinner("Running network diagnostics..."):
                    from tools import scraper
                    scraper.diagnose_network_issues()
                    st.info("📊 Network diagnostics completed. Check the console/logs for detailed results.")

    initial_state = initial_state_form()
    st.divider()

    if initial_state is None:
        st.info("Submit the form above to execute the data gatherer graph.")
        return

    st.subheader("Graph Execution")
    status_box = st.empty()

    with st.spinner("Running graph..."):
        dg, compiled = get_compiled()
        t0 = time.time()
        try:
            final_state: State = compiled.invoke(initial_state)
            elapsed = time.time() - t0
            status_box.success(f"Graph completed in {elapsed:.2f}s")
        except Exception as e:
            status_box.error(f"Graph failed: {e}")
            st.stop()

    st.subheader("Resulting State")
    try:
        state_dict = final_state.model_dump()
    except Exception:
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
        st.write(", ".join(state_dict.get("interests", [])) or "—")
        st.write("**Activities**")
        acts = state_dict.get("activities") or []
        st.write(", ".join(acts) or "—")
    with cols[2]:
        st.write("**Travel Dates**")
        if state_dict.get("travel_dates"):
            st.write(" → ".join(state_dict.get("travel_dates")))
        else:
            st.write("—")
        st.write("**Messages in State**")
        st.write(len(state_dict.get("messages", [])) if "messages" in state_dict else state_dict.get("messages_count", 0))

    with st.expander("Raw State JSON"):
        st.code(json.dumps(state_dict, indent=2), language="json")

    st.info("Note: The current data_gatherer node does not yet update fields dynamically. Add state mutations inside the node to see changes reflected here.")

if __name__ == "__main__":
    main()





