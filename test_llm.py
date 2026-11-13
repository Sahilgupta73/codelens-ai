import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load .env from the same folder as this file.
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key or not model:
    raise ValueError(
        "Add GROQ_API_KEY and GROQ_MODEL to your .env file."
    )

llm = ChatGroq(
    api_key=api_key,
    model=model,
    temperature=0,
    max_tokens=500,
)

response = llm.invoke(
    "Explain what a Python function is in two simple sentences."
)

print("\nAI response:")
print(response.content)