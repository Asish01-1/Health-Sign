from langchain_core.messages import HumanMessage

from state import NutritionState
from agent import llm, structured_llm

from tools import (
    generate_recipe,
    analyze_nutrition,
    healthy_alternative,
    meal_planner,
    evaluate_meal_plan,
)

VALID_INTENTS = {"recipe", "nutrition", "healthy", "meal_plan"}



def intent_router_node(state: NutritionState):

    user_query = state["user_query"]

    prompt = f"""
    You are an intent classifier.

    Classify the user query into ONLY ONE category.

    Categories:

    recipe
    nutrition
    healthy
    meal_plan

    Rules:

    - If the user asks for a recipe, return recipe.
    - If the user asks only for nutrition facts of a food/recipe, return nutrition.
    - If the user asks for a healthier version of a recipe, return healthy.
    - If the user asks for a meal plan / diet plan / weekly plan, return meal_plan.

    Return ONLY one word, nothing else.

    User:
    {user_query}
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    intent = response.content.strip().lower()
    intent = intent.replace(" ", "_").replace("-", "_")
    if intent not in VALID_INTENTS:
        intent = "recipe"

    state["intent"] = intent

    return state


def route_intent(state: NutritionState):
    return state["intent"]


def post_nutrition_router(state: NutritionState):
    """
    After nutrition analysis, only continue to the 'healthy alternative'
    step if the user actually asked for one. Recipe/nutrition-only
    requests end here instead of always being forced through it.
    """
    if state["intent"] == "healthy":
        return "healthy"
    return "end"



def recipe_node(state: NutritionState):

    recipe = generate_recipe.invoke(
        {
            "user_query": state["user_query"],
            "user_profile": state.get("user_profile"),
        }
    )

    state["recipe"] = recipe
    state["final_response"] = recipe

    return state


def nutrition_node(state: NutritionState):

   
    subject = state.get("recipe") or state["user_query"]

    nutrition = analyze_nutrition.invoke({"recipe": subject})

    state["nutrition"] = nutrition
    state["final_response"] = nutrition

    return state



def healthy_node(state: NutritionState):

    healthy_recipe = healthy_alternative.invoke(
        {
            "user_query": state["user_query"],
            "recipe": state["recipe"],
            "nutrition": state["nutrition"],
            "user_profile": state.get("user_profile"),
        }
    )

    state["healthy_recipe"] = healthy_recipe
    state["final_response"] = healthy_recipe

    return state



def meal_planner_node(state: NutritionState):

    meal_plan = meal_planner.invoke(
        {
            "user_goal": state["user_query"],
            "improvement_suggestions": state["improvement_suggestions"],
            "user_profile": state.get("user_profile"),
        }
    )

    state["meal_plan"] = meal_plan
    state["final_response"] = meal_plan

    return state



def meal_nutrition_node(state: NutritionState):

    nutrition = analyze_nutrition.invoke({"recipe": state["meal_plan"]})

    state["nutrition"] = nutrition

    return state



def meal_evaluator_node(state: NutritionState):

    eval_prompt = f"""
    Evaluate this meal plan against the user's goal.

    User Goal:
    {state["user_query"]}

    Meal Plan:
    {state["meal_plan"]}

    Nutrition:
    {state["nutrition"]}
    """
    result = structured_llm.invoke(eval_prompt)

    state["meal_plan_score"] = result.score
    state["is_goal_achieved"] = result.achieved
    state["improvement_suggestions"] = result.suggestions
    state["retry_count"] = state["retry_count"] + 1

    if result.achieved:
        state["final_response"] = state["meal_plan"]
    else:
        state["final_response"] = (
            f"{state['meal_plan']}\n\n"
            f"(Score: {result.score}/100 — refining based on: {result.suggestions})"
        )

    return state


def meal_plan_router(state: NutritionState):

    if state["is_goal_achieved"]:
        return "done"

    if state["retry_count"] >= state["max_retry"]:
        return "done"

    return "retry"
