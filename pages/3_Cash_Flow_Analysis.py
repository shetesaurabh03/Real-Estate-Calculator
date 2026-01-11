"""Page 2: 10-Year Cash Flow Analysis"""

import streamlit as st
import pandas as pd
from utils.session_state import initialize_session_state
from utils.calculations import (
    calculate_price_per_projection,
    calculate_total_annual_costs_dollar,
    calculate_10_year_cash_flow
)
from utils.formatters import format_currency, format_percentage

# Initialize session state
initialize_session_state()

st.title("📈 10-Year Cash Flow Analysis")
st.markdown("### Page 2: Detailed Cash Flow Projections")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("""
- **Page 1**: Project Setup & Financing (Current)
- **Page 2**: 10-Year Cash Flow Analysis
- **Page 3**: Debt Service & DSCR
- **Page 4**: Exit & Returns
- **Page 5**: Waterfall Distribution
- **Page 6**: Final Comparison
""")

# Check if scenarios exist
if len(st.session_state.scenarios) == 0:
    st.warning("⚠️ Please create at least one scenario on Page 1 first.")
    st.stop()

# Inputs Section
st.header("📋 Input Parameters")

col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)
with col1:
    st.session_state.price_per = st.number_input(
        "Price Per ($)",
        min_value=0.0,
        value=st.session_state.price_per,
        step=1.0,
        format="%.2f",
        help="Price per square foot"
    )

with col2:
    st.session_state.income_escalator = st.number_input(
        "Annual Escalator %",
        min_value=0.0,
        max_value=20.0,
        value=st.session_state.income_escalator,
        step=0.1,
        format="%.2f",
        help="Annual percentage increase in price per square foot"
    )

with col3:
    if 'adjusted_percent' not in st.session_state:
        st.session_state.adjusted_percent = 85.0
    st.session_state.adjusted_percent = st.number_input(
        "Adjusted %",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.adjusted_percent,
        step=0.1,
        format="%.2f",
        help="Percentage of income adjusted (e.g., 85%)"
    )

with col4:
    if 'gp_percent_cash_flow' not in st.session_state:
        st.session_state.gp_percent_cash_flow = 20.0
    st.session_state.gp_percent_cash_flow = st.number_input(
        "GP %",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.gp_percent_cash_flow,
        step=0.1,
        format="%.2f",
        help="General Partner percentage"
    )
with col5:
    if 'lp_percent_cash_flow' not in st.session_state:
        st.session_state.lp_percent_cash_flow = 80.0
    st.session_state.lp_percent_cash_flow = st.number_input(
        "LP %",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.lp_percent_cash_flow,
        step=0.1,
        format="%.2f",
        help="Limited Partner percentage"
    )

st.divider()

# Get price per projection
price_per_projection = calculate_price_per_projection(
    st.session_state.price_per,
    st.session_state.income_escalator,
    years=10
)

# Get annual costs (dollar amounts)
total_annual_costs = calculate_total_annual_costs_dollar(st.session_state.annual_cost)

# Display for each scenario
for idx, scenario in enumerate(st.session_state.scenarios):
    st.header(f"Scenario {idx + 1}")
    
    # Calculate 10-year cash flow
    df_cash_flow = calculate_10_year_cash_flow(
        scenario,
        price_per_projection,
        st.session_state.total_sqft,
        total_annual_costs,
        st.session_state.project_cost,
        adjusted_percent=st.session_state.adjusted_percent / 100,
        gp_percent=st.session_state.gp_percent_cash_flow / 100,
        lp_percent=st.session_state.lp_percent_cash_flow / 100
    )

    # Add escalator and price per columns
    # Escalator is 0 in Year 1 and equals the configured escalator from Year 2 onward
    df_cash_flow["Escalator %"] = df_cash_flow["Year"].apply(
        lambda y: 0.0 if y == 1 else st.session_state.income_escalator
    )
    df_cash_flow["Price Per"] = df_cash_flow["Year"].apply(lambda y: price_per_projection.get(y, 0))

    # Reorder columns for display
    column_order = [
        "Year",
        "Escalator %",
        "Price Per",
        "Rent",
        "Cash Flow",
        "Adjusted %",
        "GP %",
        "LP %",
        "LP CoC",
    ]
    df_cash_flow = df_cash_flow[column_order]
    
    # Format the dataframe for display
    df_display = df_cash_flow.copy()
    # Format currency columns
    for col in ['Price Per', 'Rent', 'Cash Flow', 'Adjusted %', 'GP %', 'LP %']:
        df_display[col] = df_display[col].apply(lambda x: format_currency(x))
    # Format percentage column (LP CoC)
    df_display['LP CoC'] = df_display['LP CoC'].apply(lambda x: format_percentage(x, 2))
    df_display['Escalator %'] = df_display['Escalator %'].apply(lambda x: format_percentage(x, 2))
    
    st.dataframe(df_display, hide_index=True, use_container_width=True)
    
    # Download button
    csv = df_cash_flow.to_csv(index=False)
    st.download_button(
        label=f"📥 Download Scenario {idx + 1} Cash Flow (CSV)",
        data=csv,
        file_name=f"scenario_{idx + 1}_cash_flow.csv",
        mime="text/csv",
        key=f"download_{idx}"
    )
    
    st.divider()

st.info("💡 **Next Step**: Navigate to 'Debt Service & DSCR' page (Page 4) to view debt service calculations.")



