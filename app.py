import pandas as pd
import streamlit as st

from main import load, analyze

st.set_page_config(page_title="Student Attendance Analyzer", layout="wide")
st.title("Student Attendance Analyzer")

# ---- Sidebar settings ----
st.sidebar.header("Settings")
target = st.sidebar.number_input("Target attendance (%)", min_value=1, max_value=99, value=75)
future = st.sidebar.number_input("Upcoming classes", min_value=1, max_value=200, value=10)
custom = st.sidebar.slider("Classes you expect to attend", 0, int(future), min(8, int(future)))

uploaded = st.sidebar.file_uploader("Upload attendance CSV", type="csv")
source = uploaded if uploaded is not None else "attendance.csv"
st.caption("Using uploaded file" if uploaded is not None else "Using attendance.csv from the project folder")

# ---- Load and analyze (show clear errors instead of crashing) ----
try:
    df = analyze(load(source), int(target), int(future), int(custom))
except SystemExit as e:
    st.error(str(e))
    st.stop()

# ---- Summary numbers ----
total = len(df)
short = int((df["status"] == "Shortage").sum())
c1, c2, c3 = st.columns(3)
c1.metric("Students", total)
c2.metric("Below target", short)
c3.metric("Average attendance", f"{df['attendance_pct'].mean():.2f}%")

# ---- Filter ----
choice = st.radio("Show", ["All", "Shortage only", "Target met only"], horizontal=True)
view = df
if choice == "Shortage only":
    view = df[df["status"] == "Shortage"]
elif choice == "Target met only":
    view = df[df["status"] == "Target met"]


def highlight(row):
    color = "background-color: #5a1f1f; color: white" if row["status"] == "Shortage" else ""
    return [color] * len(row)


st.subheader("Student-wise results")
st.dataframe(view.style.apply(highlight, axis=1).format(precision=2), width="stretch")
# ---- Charts ----
st.subheader("Attendance percentage")
st.bar_chart(df.set_index("name")["attendance_pct"])

st.subheader("Projected attendance")
st.bar_chart(df.set_index("name")[["proj_attend_all", "proj_custom", "proj_miss_all"]])

# ---- Download ----
st.download_button(
    "Download report (CSV)",
    df.to_csv(index=False),
    file_name="attendance_report.csv",
    mime="text/csv",
)

try:
    df = analyze(
        load(source),
        int(target),
        int(future),
        int(custom),
    )
except (ValueError, TypeError) as e:
    st.error(str(e))
    st.stop()
