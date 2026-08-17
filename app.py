# Simply use streamlit run app.py
import streamlit as st
from graph import app  # your existing compiled LangGraph pipeline


st.set_page_config(
    page_title="Healthy Food Organizer",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .sub-dialogue{
            color: yellow;
        }
        .stApp {
            background: yellowgreen;
        }
        

        .st-emotion-cache-lsgwmo p{
            color:black !important;
        }
        /* Hero header */
        .hfo-hero {
            text-align: center;
            padding: 1.2rem 0 0.6rem 0;
        }
        .hfo-hero h1 {
            font-size: 2.1rem;
            margin-bottom: 0.15rem;
            color: #1b5e20;
        }
        .hfo-hero p {
            color: white;
            font-size: 0.98rem;
            margin-top: 0;
        }

        /* Profile chip shown once locked in */
        .profile-chip {
            display: inline-block;
            background: black;
            color: #2e7d32;
            border: 1px solid #a5d6a7;
            border-radius: 999px;
            padding: 0.3rem 0.9rem;
            font-size: 0.85rem;
            font-weight: 600;
        }

        /* Suggestion chips row */
        div[data-testid="stButton"] button {
            border-radius: 999px !important;
            border: 1px solid #c8e6c9 !important;
            background: #ffffff !important;
            color: #2e7d32 !important;
            font-size: 0.82rem !important;
            padding: 0.35rem 0.9rem !important;
        }
        div[data-testid="stButton"] button:hover {
            background: #e8f5e9 !important;
            border-color: #66bb6a !important;
        }

        /* Chat bubbles */
        div[data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 0.4rem 0.2rem;
        }

        section[data-testid="stSidebar"] {
            background: red;
            text-color: white;
            texxt-weight: 800;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

PROFILES = {
    "🧒 Child": "child",
    "🧑 General Adult": None,
    "🧓 Senior": "senior",
    "🏃 Athlete": "athlete",
    "🏋️ Gym / Muscle Gain": "gym / muscle gain",
    "✍️ Custom...": "__custom__",
}

SUGGESTIONS = [
    "How many calories in Chicken Biryani?",
    "Give me a healthier alternative to Biryani",
    "Plan a 7-day meal plan for me",
    "I want to lose 10kg, help me plan meals",
]

if "profile_locked" not in st.session_state:
    st.session_state.profile_locked = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "messages" not in st.session_state:
    st.session_state.messages = []  


def lock_profile(label: str, custom_text: str = ""):
    value = PROFILES[label]
    if value == "__custom__":
        value = custom_text.strip() or None
    st.session_state.user_profile = value
    st.session_state.profile_locked = True


def reset_session():
    st.session_state.profile_locked = False
    st.session_state.user_profile = None
    st.session_state.messages = []


with st.sidebar:
    st.markdown("### 🥗 Healthy Food Organizer")
    st.caption("Recipes, nutrition facts, healthier swaps, and full meal plans — tailored to you.")
    st.divider()

    if st.session_state.profile_locked:
        display_label = st.session_state.user_profile or "General Adult"
        st.markdown("**Your profile for this session:**")
        st.markdown(f"<span class='profile-chip'>{display_label}</span>", unsafe_allow_html=True)
        st.write("")
        if st.button("🔄 Change profile / Start over", use_container_width=True):
            reset_session()
            st.rerun()
    else:
        st.info("Pick a profile to get started. You'll only be asked once — every answer after that will match this profile automatically.")

    st.divider()
    st.caption("Type 'exit' isn't needed here — just close the tab, or hit **Start over** anytime.")


st.markdown(
    """
    <div class="hfo-hero">
        <h1>🥗 Healthy Food Organizer</h1>
        <p id="sub-dialogue">From kids to seniors, athletes to gym-goers — healthy eating made for you.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.profile_locked:
    st.markdown("#### Who is this for?")
    cols = st.columns(3)
    labels = list(PROFILES.keys())

    chosen_label = st.radio(
        "Select a profile",
        labels,
        index=1,
        horizontal=False,
        label_visibility="collapsed",
    )

    custom_text = ""
    if PROFILES[chosen_label] == "__custom__":
        custom_text = st.text_input(
            "Describe who this is for (e.g. 'pregnant', 'diabetic', 'teenager')"
        )

    if st.button("✅ Continue to chat", type="primary", use_container_width=True):
        lock_profile(chosen_label, custom_text)
        st.rerun()

    st.stop()  


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.markdown("##### Try asking:")
    chip_cols = st.columns(2)
    clicked_suggestion = None
    for i, s in enumerate(SUGGESTIONS):
        with chip_cols[i % 2]:
            if st.button(s, key=f"chip_{i}", use_container_width=True):
                clicked_suggestion = s
else:
    clicked_suggestion = None


def run_pipeline(user_query: str) -> str:
    """Call the LangGraph pipeline with the locked-in profile."""
    initial_state = {
        "user_query": user_query,
        "user_profile": st.session_state.user_profile,
        "intent": None,
        "recipe": None,
        "nutrition": None,
        "healthy_recipe": None,
        "meal_plan": None,
        "meal_plan_score": None,
        "is_goal_achieved": None,
        "improvement_suggestions": None,
        "retry_count": 0,
        "max_retry": 3,
        "final_response": None,
        "error": None,
    }
    try:
        result = app.invoke(initial_state)
    except Exception as e:
        return f"⚠️ Something went wrong: {e}"

    return result.get("final_response") or "Sorry, I couldn't generate a response."


def handle_user_message(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.markdown(text)

    with st.chat_message("assistant"):
        with st.spinner("Cooking up your answer... 🍳"):
            answer = run_pipeline(text)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})


if clicked_suggestion:
    handle_user_message(clicked_suggestion)
    st.rerun()

user_input = st.chat_input("Ask for a recipe, nutrition facts, a healthier swap, or a meal plan...")
if user_input:
    handle_user_message(user_input)
    st.rerun()
