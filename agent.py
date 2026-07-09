import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas import MealEvaluation

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Create a .env file with:\n"
        "GROQ_API_KEY=your_key_here\n"
        "MODEL_NAME=llama-3.3-70b-versatile  # or any Groq model you have access to"
    )

if not MODEL_NAME:
    raise RuntimeError(
        "MODEL_NAME is not set. Add MODEL_NAME=<groq_model_id> to your .env file."
    )

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=0.2,
)

# Used by meal_evaluator_node to get a clean, reliable
# {score, achieved, suggestions} object instead of parsing free text.
structured_llm = llm.with_structured_output(MealEvaluation)
