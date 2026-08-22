import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Dynamic TRY vs USD Investment Model", layout="wide"
)
st.title("USD Equivalent Portfolio Value Curve")

# Sidebar Controls
st.sidebar.header("1. Core Inputs")
initial_usd = st.sidebar.number_input(
    "Initial USD Capital (USD)", value=10000, step=1000
)
monthly_contrib_usd = st.sidebar.number_input(
    "Monthly USD Contribution (USD)", value=500, step=100
)
years = st.sidebar.slider(
    "Time Horizon (Years)", min_value=1, max_value=5, value=3
)

st.sidebar.header("2. Rates & Mode")
compound_mode = st.sidebar.radio(
    "Interest Type", ["Compound Interest", "Simple Interest"]
)
try_gross = st.sidebar.slider(
    "TRY Gross Interest Rate (%)", min_value=10.0, max_value=60.0, value=45.0
)
tax_rate = st.sidebar.slider(
    "Withholding Tax / Stopaj (%)", min_value=0.0, max_value=25.0, value=17.5
)
depreciation = st.sidebar.slider(
    "Annual TRY Depreciation (%)", min_value=0.0, max_value=50.0, value=18.0
)
usd_rate = st.sidebar.slider(
    "USD Yield Rate (%)", min_value=0.0, max_value=10.0, value=4.5
)

# Monthly Parameters
total_months = years * 12
r_m_try = (try_gross * (1 - tax_rate / 100) / 100) / 12
d_m = (depreciation / 100) / 12
r_m_usd = (usd_rate / 100) / 12

months = np.arange(0, total_months + 1)
try_val = np.zeros(total_months + 1)
usd_val = np.zeros(total_months + 1)
total_contributions = np.zeros(total_months + 1)

try_val[0] = initial_usd
usd_val[0] = initial_usd
total_contributions[0] = initial_usd

# Iterative Monthly Simulation
for m in range(1, total_months + 1):
  if compound_mode == "Compound Interest":
    # Compound: Balance earns net monthly interest, devalues by monthly FX drop, plus end-of-month deposit
    try_val[m] = (try_val[m - 1] * (1 + r_m_try) / (1 + d_m)) + (
        monthly_contrib_usd
    )
    usd_val[m] = (usd_val[m - 1] * (1 + r_m_usd)) + monthly_contrib_usd
  else:
    # Simple Interest: Interest calculated on accumulated principal
    cumulative_capital = initial_usd + (m - 1) * monthly_contrib_usd
    interest_earned_m = cumulative_capital * r_m_try

    try_val[m] = (
        (try_val[m - 1] + interest_earned_m) / (1 + d_m)
    ) + monthly_contrib_usd
    usd_val[m] = (usd_val[m - 1] * (1 + r_m_usd)) + monthly_contrib_usd

  total_contributions[m] = total_contributions[m - 1] + monthly_contrib_usd

years_axis = months / 12.0

# Plotly Chart
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=years_axis,
        y=try_val,
        mode="lines",
        name=f"TRY Strategy ({compound_mode})",
        line=dict(color="#1a73e8", width=3),
    )
)
fig.add_trace(
    go.Scatter(
        x=years_axis,
        y=usd_val,
        mode="lines",
        name="USD Cash / Money Market",
        line=dict(color="#34a853", width=3, dash="dash"),
    )
)
fig.add_trace(
    go.Scatter(
        x=years_axis,
        y=total_contributions,
        mode="lines",
        name="Total USD Deposited (Cost Basis)",
        line=dict(color="#80868b", width=1.5, dash="dot"),
    )
)

fig.update_layout(
    title=f"Portfolio Growth ({compound_mode})",
    xaxis_title="Years",
    yaxis_title="USD Value ($)",
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Principal Deposited", "${:,.2f}".format(total_contributions[-1]))
col2.metric("Final TRY Strategy USD Value", "${:,.2f}".format(try_val[-1]))
col3.metric("Final USD Holding Value", "${:,.2f}".format(usd_val[-1]))