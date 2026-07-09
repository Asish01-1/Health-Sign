from pydantic import BaseModel, Field


class MealEvaluation(BaseModel):
    """Structured evaluation of a meal plan, produced by structured_llm."""

    score: int = Field(description="Score out of 100 for how well the meal plan meets the user's goal")
    achieved: bool = Field(description="True if the meal plan satisfies the user's goal")
    suggestions: str = Field(description="Concrete suggestions to improve the meal plan if the goal isn't achieved")
