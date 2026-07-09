# What was broken, and what changed

1. **`meal_plan_router` always returned `"done"`.**
   Both branches of the `if` returned the same value, so a low-scoring meal
   plan could never trigger a retry. Fixed to actually return `"retry"`
   when the goal isn't achieved and retries remain.

2. **The meal-plan evaluation was thrown away.**
   `evaluate_meal_plan` (a plain string tool) was called, but its output
   was dumped into `meal_plan_score` and `is_goal_achieved` /
   `improvement_suggestions` were never set — so the router had nothing to
   check. `meal_evaluator_node` now uses `agent.structured_llm` (built on
   your existing `schemas.MealEvaluation`) to get a real
   `score / achieved / suggestions` object, and increments `retry_count`.

3. **`nutrition_node` read `state["recipe"]`, which is `None` for
   "nutrition" and "meal_plan" intents.** It now falls back to
   `state["user_query"]` when no recipe exists yet, so "what are the
   calories in a bowl of dal?" works without generating a recipe first.

4. **Every intent was forced through `recipe → nutrition → healthy → END`.**
   A plain recipe or nutrition request got dragged through the "healthy
   alternative" step regardless. Added `post_nutrition_router` so only the
   `healthy` intent continues to the `healthy` node; `recipe` and
   `nutrition` requests end right after nutrition analysis.

5. **No way to personalize for different people.**
   Added an optional `user_profile` field (e.g. `"child"`, `"senior"`,
   `"athlete"`, `"gym / muscle gain"`) that flows into every prompt in
   `tools.py`, so recipes, meal plans, and swaps are adjusted for the
   person eating them — from kids to seniors to athletes.

6. **`app.py` ran once and exited.** Restored a proper chat loop, asks
   once for the user's profile, and prints `final_response` cleanly
   instead of the raw state dict. Wrapped `app.invoke` in try/except so a
   bad LLM response doesn't crash the whole session.

7. **`agent.py` would raise a cryptic error if `.env` was missing/wrong.**
   Now checks `GROQ_API_KEY` / `MODEL_NAME` up front with a clear message,
   and exposes `structured_llm` for the evaluator.

## To run it

```bash
pip install langgraph langchain-groq python-dotenv pydantic
cp .env.example .env   # then put your real Groq API key in .env
python app.py
```
