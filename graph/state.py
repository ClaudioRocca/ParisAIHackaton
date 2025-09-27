import sys, os
from typing import List, Optional 
from pydantic import Field
from langgraph.graph import MessagesState

class State(MessagesState):
    """Represents the state of the Graph, including iterative retrieval context.

    Args:
    - destination: The destination the user wants to visit.
    - people_number: Number of people traveling.
    - interests: User's interests related to the trip.
    - travel_dates: User's preferred travel dates.
    - budget: User's budget for the trip.
    - activities: User's preferred activities during the trip.

    """
    destination: Optional[str] = Field(default=None, description="The destination the user wants to visit.")
    people_number: Optional[int] = Field(default=1, description="Number of people traveling.")
    interests: List[str] = Field(default_factory=list, description="User's interests related to the trip.")
    travel_dates: Optional[List[str]] = Field(default=None, description="User's preferred travel dates.")
    budget: Optional[float] = Field(default=None, description="User's budget for the trip.")
    activities: Optional[List[str]] = Field(default=None, description="User's preferred activities during the trip.")
