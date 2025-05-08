from pydantic import BaseModel

from agents import Agent
from ..config import PLANNER_MODEL # Import the model config

# Generate a plan of searches to ground the tennis analysis.
# For a given tennis question or company, we want to search for
# recent news, official filings, analyst commentary, and other
# relevant background.
PLANNER_PROMPT = (
    "You are a tennis research planner. Given a request for tennis analysis, "
    "produce a set of web searches to gather the context needed. Aim for recent "
    "headlines, match results, analyst commentary, and press conference quotes. "
    "Output between 5 and 14 search terms to query for. "
)

class TennisSearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web (or file) search."""


class TennisSearchPlan(BaseModel):
    searches: list[TennisSearchItem]
    """A list of searches to perform."""


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PLANNER_PROMPT,
    model=PLANNER_MODEL, # Use the config variable
    output_type=TennisSearchPlan,
)
