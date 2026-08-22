from services.gemini_client import invoke_gemini_with_retry, GeminiServiceException
from prompts.contextual_sous_chef import (
    SOUS_CHEF_SYSTEM_INSTRUCTION,
    build_sous_chef_prompt,
)

def ask_sous_chef(recipe: dict, preferences: dict, user_question: str) -> str:
    """
    Sends contextual user question about the active recipe to Gemini API.
    Returns the assistant's string answer.
    """
    if not user_question or not user_question.strip():
        return "Please ask a question about your recipe or ingredients."

    prompt_text = build_sous_chef_prompt(recipe, preferences, user_question)

    try:
        response_text = invoke_gemini_with_retry(
            contents=prompt_text,
            system_instruction=SOUS_CHEF_SYSTEM_INSTRUCTION,
            temperature=0.5,
            max_retries=3,
        )
        return response_text or "I recommend adjusting the heat and seasoning to taste."
    except GeminiServiceException as gse:
        return gse.user_message
    except Exception:
        return "✨ The AI Sous-Chef is currently busy. Please try asking again in a moment."
