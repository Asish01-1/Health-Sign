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

graph.add_edge(START, "intent_router")

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

graph.add_conditional_edges(
    "nutrition",
    post_nutrition_router,
    {
        "healthy": "healthy",
        "end": END,
    },
)

graph.add_edge("healthy", END)

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
