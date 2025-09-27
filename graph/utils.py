from graph.state import State

def all_info_provided(state:State):
        required_keys = ["destination", "people_number", "interests", "travel_dates", "budget", "activities"]
        return all(key in state for key in required_keys)
        # return True

def inject_current_information(state: State) -> str:
    """Inject current information from the state into the prompt."""
    current_info = ""
    # Appends all key features inside State as a string to be provided to the LLM

    if state.get("destination"):
        current_info += f"Travel destination: {state['destination']}\n"
    if state.get("people_number"):
        current_info += f"Number of people traveling: {state['people_number']}\n"
    if state.get("interests"):
        current_info += f"User's interests: {state['interests']}\n"
    if state.get("travel_dates"):
        current_info += f"Preferred travel dates: {state['travel_dates']}\n"
    if state.get("budget"):
        current_info += f"User's budget: {state['budget']}\n"
    if state.get("activities"):
        current_info += f"User's preferred activities: {state['activities']}\n"
    return current_info