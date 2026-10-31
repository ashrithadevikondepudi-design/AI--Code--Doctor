import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def local_explanation(code: str):

    if "max(" in code:
        explanation = (
            "This code uses Python's built-in max() function "
            "to find the largest value in the given collection."
        )

        suggestion = (
            "The use of max() is already simple and efficient "
            "for finding the maximum value."
        )

    elif "for " in code:
        explanation = (
            "This code contains a loop that processes values "
            "one by one."
        )

        suggestion = (
            "Check whether a Python built-in function or a "
            "more efficient algorithm can replace the loop."
        )

    else:
        explanation = (
            "This Python code can be analyzed based on its "
            "functions, operations and data structures."
        )

        suggestion = (
            "Consider adding clear function names, docstrings "
            "and appropriate error handling."
        )

    return {
        "status": "success",
        "source": "local",
        "explanation": explanation,
        "suggestion": suggestion
    }


def explain_code(code: str):

    api_key = os.getenv("OPENAI_API_KEY")

    # --------------------------------
    # Try AI API
    # --------------------------------

    if api_key:

        try:

            client = OpenAI(api_key=api_key)

            prompt = f"""
You are an expert programming assistant.

Analyze this Python code:

{code}

Explain:

1. What the code does
2. Important problems
3. How it can be improved
4. Time complexity
5. Space complexity

Use simple language.
"""

            response = client.responses.create(
                model="gpt-5-mini",
                input=prompt
            )

            return {
                "status": "success",
                "source": "AI",
                "explanation": response.output_text
            }

        except Exception as e:

            # If API has no credits or another API error,
            # use local explanation instead.

            print("AI API unavailable:", e)

    # --------------------------------
    # Local fallback
    # --------------------------------

    return local_explanation(code)