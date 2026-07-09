from langgraph.graph import StateGraph, START, END

from state import NutritionState

from nodes import (
    intent_router_node,
    recipe_node,
    nutrition_node,
    healthy_node,
    meal_planner_node,
    route_intent,
    post_nutrition_router,
    meal_evaluator_node,
    meal_plan_router,
    meal_nutrition_node,
)


graph = StateGraph(state_schema=NutritionState)

graph.add_node("intent_router", intent_router_node)
graph.add_node("recipe", recipe_node)
graph.add_node("nutrition", nutrition_node)
graph.add_node("healthy", healthy_node)
graph.add_node("meal_plan", meal_planner_node)
graph.add_node("meal_nutrition", meal_nutrition_node)
graph.add_node("meal_evaluator", meal_evaluator_node)

# --- Entry ---
graph.add_edge(START, "intent_router")

# --- Route by intent ---
# "recipe" and "healthy" both need a recipe first; "nutrition" analyzes
# the query directly (nutrition_node falls back to user_query when there's
# no recipe yet); "meal_plan" goes down its own branch.
graph.add_conditional_edges(
    "intent_router",
    route_intent,
    {
        "recipe": "recipe",
        "nutrition": "nutrition",
        "healthy": "recipe",
        "meal_plan": "meal_plan",
    },
)

graph.add_edge("recipe", "nutrition")

# After nutrition analysis: only go on to "healthy alternative" if that's
# what was actually asked for. Otherwise stop here — a plain recipe or
# nutrition request shouldn't be forced through the healthy-swap step.
graph.add_conditional_edges(
    "nutrition",
    post_nutrition_router,
    {
        "healthy": "healthy",
        "end": END,
    },
)

graph.add_edge("healthy", END)

# --- Meal plan branch, with a working retry loop ---
graph.add_edge("meal_plan", "meal_nutrition")
graph.add_edge("meal_nutrition", "meal_evaluator")

graph.add_conditional_edges(
    "meal_evaluator",
    meal_plan_router,
    {
        "done": END,
        "retry": "meal_plan",
    },
)

app = graph.compile()
