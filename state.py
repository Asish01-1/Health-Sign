from typing import TypedDict


class NutritionState(TypedDict):
    # -----------------------------
    # User Input
    # -----------------------------
    user_query: str

    # Who the plan is for: e.g. "child", "senior", "athlete",
    # "gym / muscle gain", "general adult". Optional — used to
    # tailor every recipe / meal plan / nutrition tip.
    user_profile: str | None

    # -----------------------------
    # Intent
    # -----------------------------
    intent: str | None

    # -----------------------------
    # Recipe
    # -----------------------------
    recipe: str | None

    # -----------------------------
    # Nutrition Report
    # -----------------------------
    nutrition: str | None

    # -----------------------------
    # Healthy Alternative
    # -----------------------------
    healthy_recipe: str | None

    # -----------------------------
    # Meal Planner
    # -----------------------------
    meal_plan: str | None

    # -----------------------------
    # Meal Evaluation
    # -----------------------------
    meal_plan_score: int | None

    is_goal_achieved: bool | None

    improvement_suggestions: str | None

    # -----------------------------
    # Retry
    # -----------------------------
    retry_count: int

    max_retry: int

    # -----------------------------
    # Output
    # -----------------------------
    final_response: str | None

    # -----------------------------
    # Error
    # -----------------------------
    error: str | None
