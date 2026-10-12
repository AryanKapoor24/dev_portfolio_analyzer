import os
import tomllib

import groq
from groq import Groq


SECRETS_FILE = ".streamlit/secrets.toml"


def get_setting(name, default=None):
    # 1. Environment variable (how most hosting platforms provide secrets)
    if name in os.environ:
        return os.environ[name]

    # 2. .streamlit/secrets.toml (local development)
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, "rb") as file:
            secrets = tomllib.load(file)

        if name in secrets:
            return secrets[name]

    return default


def ask_llm(system, prompt, json_mode=False):
    """
    The ONLY function that talks to the AI.

    system:    how the AI should behave  (e.g. "You are a tech recruiter.")
    prompt:    what you are asking       (e.g. the developer data)
    json_mode: True = Groq forces the reply to be valid JSON

    Returns the AI's reply as text.
    """

    api_key = get_setting("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from your secrets.")

    client = Groq(
        api_key=api_key,
        timeout=60,      # give up if no reply within 60 seconds
        max_retries=2    # retry automatically if Groq is busy
    )

    options = {}

    if json_mode:
        options["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=get_setting("LLM_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        **options
    )

    return response.choices[0].message.content


def describe_ai_error(error):
    # Turn an exception into a message that makes sense to a user
    if isinstance(error, groq.RateLimitError):
        return "The AI is getting too many requests right now. Please wait a minute and try again."

    if isinstance(error, groq.AuthenticationError):
        return "The AI service rejected the API key. Check GROQ_API_KEY in your secrets."

    if isinstance(error, (groq.APIConnectionError, groq.APITimeoutError)):
        return "Couldn't reach the AI service. Check your internet connection and try again."

    if isinstance(error, groq.APIStatusError):
        return f"The AI service returned an error ({error.status_code}). Please try again later."

    return f"AI insights couldn't be generated: {error}"
