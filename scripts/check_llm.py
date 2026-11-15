# Manual check against the REAL Groq API (not run by pytest/CI; uses quota).
# Run from the project root:  python -m scripts.check_llm
from backend.llm import ask_llm


reply = ask_llm(
    system="You are a friendly assistant.",
    prompt="Say hi in 5 words."
)

print(reply)
