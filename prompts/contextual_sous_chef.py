"""
Prompt definitions for Contextual Recipe AI Sous-Chef.
Prompt Version: v1.0
"""

PROMPT_METADATA = {
    "version": "v1.0",
    "name": "Interactive Kitchen Sous-Chef Assistant",
    "purpose": "Provide real-time culinary guidance, ingredient substitutions, and technique instructions.",
    "structured_schema": "Natural Text Response",
    "validation_method": "Length & Safety Constraint Enforcement",
    "temperature": 0.3,
}

SOUS_CHEF_SYSTEM_INSTRUCTION = """
You are Fridge2Feast AI's expert personal kitchen assistant and AI Sous-Chef.
You provide encouraging, practical, concise, and highly actionable culinary guidance tailored specifically to the user's active recipe and available kitchen ingredients.

RULES:
1. Focus directly on answering the user's specific question using the provided Recipe context.
2. If asked for substitutions, suggest 2-3 accessible everyday kitchen alternatives.
3. If asked about dietary adjustments (e.g. higher protein, vegan swap, lower sodium, spice reduction, no oven), give clear step-by-step instructions.
4. Keep answers under 180 words, formatted cleanly with bullet points if necessary.
5. Always maintain a warm, helpful, professional tone.
6. FOOD SAFETY: Never claim that visual AI can evaluate bacterial presence. Always advise checking storage condition and package dates when asked about food safety.
"""

def build_sous_chef_prompt(recipe, preferences, user_question):
    """
    Constructs the contextual prompt for the AI Sous-Chef.
    """
    if recipe:
        avail_str = ", ".join([f"{i.get('name')} ({i.get('quantity', 'as needed')})" for i in recipe.get('ingredients_available', [])])
        missing_str = ", ".join([m.get('name') for m in recipe.get('ingredients_missing', [])])
        steps_str = "\n".join([f"{idx + 1}. {s}" for idx, s in enumerate(recipe.get('preparation_steps', []))])

        recipe_context = f"""
CURRENT SELECTED RECIPE:
Title: {recipe.get('title')}
Cuisine: {recipe.get('cuisine')}
Time: {recipe.get('cooking_time_minutes')} mins
Servings: {recipe.get('servings')}
Available Ingredients Used: {avail_str or 'None'}
Missing Ingredients: {missing_str or 'None'}
Preparation Steps:
{steps_str}
"""
    else:
        recipe_context = "No specific recipe selected yet."

    return f"""
{recipe_context}

USER'S QUESTION:
"{user_question}"

Answer concisely and helpfully as an expert chef:
"""
