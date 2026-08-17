from typing import TypedDict


class NutritionState(TypedDict):
    user_query: str

    user_profile: str | None
    intent: str | None
    recipe: str | None
    nutrition: str | None
    healthy_recipe: str | None
    meal_plan: str | None
    meal_plan_score: int | None
    is_goal_achieved: bool | None
    improvement_suggestions: str | None
    retry_count: int
    max_retry: int
    final_response: str | None
    error: str | None
