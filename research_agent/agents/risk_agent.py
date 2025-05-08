from pydantic import BaseModel

from agents import Agent
from ..config import RISK_MODEL # Import the model config

# A sub‑agent specializing in identifying risk factors or concerns.
RISK_PROMPT = (
    "You are a risk analyst looking for potential red flags in a tennis player's upcoming performance. "
    "Given background research, produce a short analysis of risks such as opponent's advantages, "
    "health issues, ranking issues, or coaching concerns. Keep it under 3 paragraphs."
)


class AnalysisSummary(BaseModel):
    summary: str
    """Text summary for this aspect of the analysis. Keep it under 6 paragraphs."""


risk_agent = Agent(
    name="RiskAnalystAgent",
    instructions=RISK_PROMPT,
    model=RISK_MODEL, # Use the config variable
    output_type=AnalysisSummary,
)
