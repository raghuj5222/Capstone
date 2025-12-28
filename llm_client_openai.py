# llm_client_openai.py
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# -----------------------------
# Configure OpenAI client
# -----------------------------
# Make sure you set:
# export OPENAI_API_KEY="your-key"
#
# Or on Windows PowerShell:
# setx OPENAI_API_KEY "your-key"

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. "
        "Set it before running the Streamlit app."
    )

client = OpenAI(api_key=API_KEY)


# -----------------------------
# LLM call wrapper
# -----------------------------
def call_llm(system_prompt: str, user_message: str) -> str:
    """
    Sends a structured prompt to OpenAI and returns the model's text output.

    Parameters
    ----------
    system_prompt : str
        High-level instructions (safety, constraints, tone).
    user_message : str
        The actual question + retrieved context.

    Returns
    -------
    str
        The model's generated text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",   # You can change to gpt-4o, gpt-4.1-mini, etc.
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return (
            "The language model encountered an error while generating a response. "
            f"Technical details: {e}"
        )
