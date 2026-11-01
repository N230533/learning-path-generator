import streamlit as st
from path_generator import generate_learning_path
from history import load_history, save_entry, clear_history

st.set_page_config(page_title="Learning Path Generator", page_icon="📚")

# Remember which path is currently shown, even after a rerun
if "current" not in st.session_state:
    st.session_state.current = None


def show_path(entry: dict):
    path = entry["path"]
    st.subheader(f"Your path to learn {entry['topic']}")
    st.caption(f"Saved {entry['time']} · {entry['level']} · {entry['hours']} hours per week")

    total = sum(s["duration_weeks"] for s in path)
    st.info(f"Estimated total: {total} weeks")

    cols = st.columns(len(path))
    for col, step in zip(cols, path):
        col.metric(f"Stage {step['stage']}", f"{step['duration_weeks']} wks")

    for step in path:
        with st.expander(
            f"Stage {step['stage']}: {step['title']}",
            expanded=(step["stage"] == 1),
        ):
            st.write(step["description"])
            st.markdown("**Resources and videos:**")
            for video in step["videos"]:
                st.markdown(f"- [{video['name']}]({video['url']}) 🎬")
            st.caption(f"Estimated time: {step['duration_weeks']} week(s)")
            st.checkbox(
                "Mark as completed",
                key=f"done_{entry['id']}_{step['stage']}",
            )

    plan_text = "\n".join(f"Stage {s['stage']}: {s['title']}" for s in path)
    st.download_button("Download my plan", plan_text, file_name="learning_path.txt")

# ---------- Light / dark mode toggle ----------
# ---------- Light / dark mode toggle ----------
with st.sidebar:
    dark_mode = st.toggle("🌙 Dark mode", key="dark_mode")

DARK = {
    "bg": "#0E1117", "side": "#1A1C24", "card": "#262730",
    "border": "#3A3D4A", "text": "#FAFAFA", "muted": "#A3A8B8",
}
LIGHT = {
    "bg": "#FFFFFF", "side": "#F5F5F7", "card": "#FFFFFF",
    "border": "#E0E0E5", "text": "#31333F", "muted": "#6B6F80",
}
c = DARK if dark_mode else LIGHT

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {c['bg']}; color: {c['text']}; }}
    [data-testid="stHeader"] {{ background-color: {c['bg']}; }}
    [data-testid="stSidebar"] {{ background-color: {c['side']}; }}

    /* Text */
    .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp li,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{ color: {c['text']} !important; }}
    [data-testid="stCaptionContainer"] {{ color: {c['muted']} !important; }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: {c['card']}; border-color: {c['border']};
    }}

    /* Buttons: sidebar history/clear buttons and the form submit button */
    [data-testid="stSidebar"] button,
    [data-testid="stFormSubmitButton"] button {{
        background-color: {c['card']} !important;
        color: {c['text']} !important;
        border: 1px solid {c['border']} !important;
    }}
    [data-testid="stSidebar"] button p,
    [data-testid="stSidebar"] button span,
    [data-testid="stSidebar"] button div {{
        color: {c['text']} !important;
    }}

    /* Hover tooltips (the help text on history buttons) */
    [data-baseweb="tooltip"] div,
    [data-baseweb="popover"] div {{
        background-color: {c['card']} !important;
        color: {c['text']} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar: past paths ----------
with st.sidebar:
    st.header("Past paths")
    history = load_history()

    if not history:
        st.caption("No saved paths yet. Generate one and it will appear here.")

    for entry in history:
        if st.button(
            f"{entry['topic']} · {entry['level']}",
            key=f"hist_{entry['id']}",
            help=entry["time"],
            use_container_width=True,
        ):
            st.session_state.current = entry

    # Bottom of the sidebar: icon-only clear button
    st.divider()
    if history:
        if st.button("🗑", help="Clear all history", key="clear_history"):
            clear_history()
            st.session_state.current = None
            st.rerun()

# ---------- Main page ----------
st.title("📚 Learning Path Generator")
st.write("Tell us what you want to learn, and we'll build a step-by-step plan for you.")

with st.form("path_form"):
    topic = st.text_input(
        "What do you want to learn?",
        placeholder="e.g., Python for data analysis",
    )
    level = st.selectbox("Your current level", ["Beginner", "Intermediate", "Advanced"])
    hours = st.slider("Hours you can study per week", min_value=1, max_value=40, value=5)
    submitted = st.form_submit_button("Generate my path")

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        try:
            with st.spinner("Building your learning path with Gemini..."):
                path = generate_learning_path(topic.strip(), level, hours)
            st.session_state.current = save_entry(topic.strip(), level, hours, path)
        except Exception as error:
            st.error(f"Something went wrong: {error}")

if st.session_state.current:
    show_path(st.session_state.current)