import os
from dotenv import load_dotenv

# Load .env from custom path
load_dotenv("C:/Users/johnj/secure_configs/AgenticResearch/.env")

# Access variables
api_key = os.environ.get("OPENAI_API_KEY")

from google.generativeai import palm

# Load Google API Key
google_api_key = os.environ.get("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

# Initialize Google LLM client
palm.configure(api_key=google_api_key)

import asyncio

from .manager import TennisResearchManager # Import manager after loading env vars

async def main() -> None:
    # Make sure ResearchManager() correctly uses the env var
    # or allows passing the key if needed.
    query = input("Enter a tennis research query: ")

    # Example usage of Google LLM
    response = palm.generate_text(prompt=query, model="text-bison-001")
    print("Google LLM Response:", response["output"])  # Adjust based on actual SDK response structure

    mgr = TennisResearchManager()  # Check its __init__ method
    await mgr.run(query)

if __name__ == "__main__":
    asyncio.run(main())
