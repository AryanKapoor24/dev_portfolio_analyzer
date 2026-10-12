from backend.llm import ask_llm


reply = ask_llm(
    system="You are a friendly assistant.",
    prompt="Say hi in 5 words."
)

print(reply)
