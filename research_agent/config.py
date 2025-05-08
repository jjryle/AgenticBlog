# Central configuration for agent models

# Default model for most agents
DEFAULT_MODEL = "gpt-4o"
# You can specify different models for specific agents if needed
PLANNER_MODEL = "o3-mini"#DEFAULT_MODEL
SEARCH_MODEL = "gpt-4o-2024-08-06" #DEFAULT_MODEL # Or maybe a cheaper/faster model?
WRITER_MODEL = "gpt-4o" #DEFAULT_MODEL # Or maybe a more powerful model?
VERIFIER_MODEL = "gpt-4o" #DEFAULT_MODEL
TENNIS_MODEL = DEFAULT_MODEL # Assuming this is the fundamentals agent
RISK_MODEL = DEFAULT_MODEL