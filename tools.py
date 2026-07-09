from langchain_core.tools import tool

from agent import llm


def _profile_line(user_profile: str | None) -> str:
    """Turn the optional profile into an instruction the LLM can use."""
    if not user_profile:
        return "No specific profile given — assume a healthy general adult."
    return (
        f"This is for: {user_profile}. Adjust portion sizes, ingredients, "
        f"texture, and nutrition targets appropriately (e.g. smaller/softer "
        f"portions and no choking hazards for young children; easy-to-chew, "
        f"lower-sodium options for seniors; higher protein and calorie "
        f"density for athletes/gym-goers; balanced, moderate portions for "
        f"general adults)."
    )


# ==========================================================
# Recipe Generator
# ==========================================================

@tool
def generate_recipe(user_query: str, user_profile: str | None = None) -> str:
    """
    Generate a recipe based on the user's request, personalized for the
    given user_profile (e.g. child, senior, athlete, gym-goer, general adult).
    """

    prompt = f"""
    You are an expert chef and nutrition-aware recipe writer.

    {_profile_line(user_profile)}

    The user may provide:
    - Dish name
    - Ingredients
    - Cuisine
    - Dietary preference
    - Fitness goal

    Generate a complete recipe including:

    1. Recipe Name
    2. Ingredients
    3. Ingredient Quantity
    4. Step-by-Step Instructions
    5. Preparation Time
    6. Cooking Time
    7. Servings
    8. Cooking Tips

    User Request:
    {user_query}
    """

    response = llm.invoke(prompt)
    return response.content


# ==========================================================
# Nutrition Analyzer
# ==========================================================

@tool
def analyze_nutrition(recipe: str) -> str:
    """
    Analyze the nutrition of a recipe or food description.
    """

    prompt = f"""
    You are a certified nutritionist.

    Analyze the following food/recipe.

    Return:

    - Calories
    - Protein
    - Carbohydrates
    - Fat
    - Fiber
    - Vitamins
    - Minerals

    Food / Recipe:

    {recipe}
    """

    response = llm.invoke(prompt)
    return response.content


# ==========================================================
# Healthy Alternative
# ==========================================================

@tool
def healthy_alternative(
    user_query: str,
    recipe: str,
    nutrition: str,
    user_profile: str | None = None,
) -> str:
    """
    Suggest healthier alternatives for a recipe, personalized for the
    given user_profile.
    """

    prompt = f"""
    {_profile_line(user_profile)}

    User Goal:

    {user_query}

    Recipe:

    {recipe}

    Nutrition Report:

    {nutrition}

    Suggest healthier alternatives.

    Explain WHY each alternative is healthier, and note anything specific
    to the profile above (e.g. kid-friendly swaps, senior-friendly textures,
    higher-protein athlete swaps).
    """

    response = llm.invoke(prompt)
    return response.content


# ==========================================================
# Meal Planner
# ==========================================================

@tool
def meal_planner(
    user_goal: str,
    improvement_suggestions: str | None,
    user_profile: str | None = None,
) -> str:
    """
    Generate a personalized 7-day meal plan for the given user_goal,
    optionally incorporating improvement_suggestions from a prior
    evaluation, and tailored to user_profile.
    """

    if not improvement_suggestions:
        improvement_suggestions = "No previous suggestions."

    prompt = f"""
    {_profile_line(user_profile)}

    Create a personalized 7-day meal plan.

    User Goal:

    {user_goal}

    Previous Suggestions To Incorporate:

    {improvement_suggestions}

    Include for each day:

    Breakfast
    Lunch
    Dinner
    Snacks

    Keep portions and choices consistent with the profile above.
    """

    response = llm.invoke(prompt)
    return response.content


# ==========================================================
# Meal Evaluator
# ==========================================================

@tool
def evaluate_meal_plan(
    meal_plan: str,
    nutrition: str,
    user_goal: str,
) -> str:
    """
    Give a free-text evaluation of whether the meal plan satisfies the
    user's goal. (Used for a human-readable summary; the structured
    score/achieved/suggestions used for routing comes from
    agent.structured_llm in meal_evaluator_node.)
    """

    prompt = f"""
    User Goal:

    {user_goal}

    Meal Plan:

    {meal_plan}

    Nutrition:

    {nutrition}

    Evaluate:

    1. Goal Achievement (Yes/No)
    2. Score out of 100
    3. Improvements Needed
    """

    response = llm.invoke(prompt)
    return response.content
