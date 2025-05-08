from pydantic import BaseModel

from agents import Agent
from ..config import TENNIS_MODEL # Import the model config

# A sub‑agent focused on analyzing a company's fundamentals.
TENNIS_PROMPT = (
    "You are a tennis analyst focused on tennis match prediction and analysis. You will consider "
    "each player's recent performance, their head-to-head records, how each played at this tournament before "
    "Given a collection of web (and optional file) search results about a player, matchup, or tournament, write a concise analysis recent tennis activity "
    " and developments. Pull out key metrics or quotes. Keep it under 3 paragraphs. "
)


class AnalysisSummary(BaseModel):
    summary: str
    """Short text summary for this aspect of the analysis."""

tennis_agent = Agent(
    name="TennisAnalystAgent",
    instructions=TENNIS_PROMPT,
    model=TENNIS_MODEL, # Use the config variable
    output_type=AnalysisSummary,
)
