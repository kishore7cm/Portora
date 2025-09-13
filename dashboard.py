# dashboard.py (enhanced UI/UX version)
import streamlit as st
import pandas as pd
import plotly.express as px
from portora_main import run_analysis, run_sp500_analysis

st.set_page_config(page_title="Portora Advisor", layout="wide")
st.title("📊 Portora Portfolio Rebalancer")

# Custom CSS for styling
st.markdown("""
    <style>
        .stDataFrame tbody tr:hover {background-color: #f0f0f0;}
        .metric-box {padding: 10px; background-color: #f9f9f9; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# Tabs for navigation
tabs = st.tabs(["Portfolio Overview", "S&P 500 Pulse"])

# === TAB 1: Portfolio Overview ===
with tabs[0]:
    st.header("📌 Portfolio Health Summary")

    # Fetch data
    portfolio_df, summary_df = run_analysis()

    # Category Summary
    st.subheader("📊 Category-Level Allocation Summary")
    st.dataframe(summary_df.style.background_gradient(cmap="Blues"), use_container_width=True)

    # Allocation health alert
    biggest_drift = summary_df.loc[summary_df["Drift"].abs().idxmax()]
    if abs(biggest_drift["Drift"]) > 5:
        st.warning(f"⚠️ Your {biggest_drift['Category']} allocation is off by {biggest_drift['Drift']}% from target.")
    else:
        st.success("✅ Your allocations are close to target. Well done!")

    # Filter by Action (optional UX control)
    actions = portfolio_df["Action"].unique().tolist()
    selected_action = st.selectbox("Filter by Recommendation:", ["All"] + actions)
    if selected_action != "All":
        filtered_df = portfolio_df[portfolio_df["Action"] == selected_action]
    else:
        filtered_df = portfolio_df

    # Stock-Level View
    st.subheader("🔍 Stock-Level Recommendation")
    simple_cols = ["Category", "Ticker", "Curr %", "Tgt %", "Drift %", "RSI", "MACD", "Trend", "Score", "Action"]
    styled_table = filtered_df[simple_cols].style.applymap(
        lambda v: 'color: green' if v == 'BUY' else ('color: red' if v == 'SELL' else None), subset=["Action"]
    )
    st.dataframe(styled_table, use_container_width=True)

    # Full View
    with st.expander("🔬 Expand for Full View"):
        st.dataframe(filtered_df, use_container_width=True)


# === TAB 2: S&P 500 Pulse ===
with tabs[1]:
    st.header("📈 S&P 500 Market Overview")
    with st.spinner("Analyzing S&P 500 stocks..."):
        df_sp = run_sp500_analysis()

    st.success("S&P 500 Insights Loaded")

    # Score Distribution Chart
    st.subheader("📊 Market Sentiment Snapshot")
    fig = px.histogram(df_sp, x="Score", nbins=20, title="Distribution of Scores in S&P 500")
    st.plotly_chart(fig, use_container_width=True)

    # Filter by Action
    selected_sp_action = st.selectbox("Filter S&P 500 by Action:", ["All"] + df_sp["Action"].unique().tolist())
    if selected_sp_action != "All":
        df_sp = df_sp[df_sp["Action"] == selected_sp_action]

    # Simple View for S&P
    st.subheader("🔍 Simple View: Leaders")
    simple_sp_cols = ["Ticker", "RSI", "MACD", "Trend", "Score", "Action"]
    st.dataframe(df_sp[simple_sp_cols].style.applymap(
        lambda v: 'color: green' if v == 'BUY' else ('color: red' if v == 'SELL' else None), subset=["Action"]
    ), use_container_width=True)

    # Expanded table
    with st.expander("🧪 Full S&P 500 Details"):
        st.dataframe(df_sp, use_container_width=True)
