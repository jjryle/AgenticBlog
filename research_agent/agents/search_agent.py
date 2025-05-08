#from agents import Agent, Tool # Assuming Tool and potentially a specific WebSearchTool exist
from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings
from ..config import SEARCH_MODEL





# Updated prompt to enforce strict adherence to the expected format
SEARCH_PROMPT = (
    "You are a research assistant specializing in tennis topics. "
    "Given a search term, use the available web search tool to retrieve up‑to‑date context. "
    "Produce a short summary of at most 300 words, focusing on key numbers, events, "
    "or quotes useful to a tennis analyst. For matchups, consider head-to-head performance."
)

# Optionally, add validation logic to ensure the output matches the expected format

search_agent = Agent(
    name="SearchAgent",
    instructions=SEARCH_PROMPT,
    tools=[WebSearchTool()],
    model_settings=ModelSettings(tool_choice="required"),
)

# Example usage of validation logic (if applicable in the framework)
# response = search_agent.run("Carlos Alcaraz vs Arthur Fils match preview headlines 2023")
# if not validate_response_format(response):
#     print("Response format is invalid.")
