"""Main entry point - Page 1: Project Setup & Financing"""

import streamlit as st
import pandas as pd
from datetime import date
from utils.session_state import initialize_session_state
from utils.calculations import calculate_loan_metrics
from utils.formatters import format_currency
from components.input_forms import render_scenario_inputs

# Page configuration
st.set_page_config(
    page_title="Real Estate Investment Calculator",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Main App
st.title("🏢 Real Estate Investment Calculator")
st.markdown("### Page 1: Project Setup & Financing")

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("""
- **Page 1**: Project Setup & Financing (Current)
- **Page 2**: 10-Year Cash Flow Analysis
- **Page 3**: Debt Service & DSCR
- **Page 4**: Exit & Returns
- **Page 5**: Waterfall Distribution
- **Page 6**: Final Comparison
""")

# Project Details Section
st.header("📋 Project Details")
st.markdown("_These details are fixed across all scenarios_")

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.project_name = st.text_input(
        "Project Name",
        value=st.session_state.project_name
    )
    st.session_state.asset_class = st.text_input(
        "Asset Class",
        value=st.session_state.asset_class
    )

with col2:
    st.session_state.anticipated_start = st.date_input(
        "Anticipated Start",
        value=st.session_state.anticipated_start
    )
    st.session_state.project_cost = st.number_input(
        "Project Cost ($)",
        min_value=0.0,
        value=st.session_state.project_cost,
        step=1000.0,
        format="%.2f"
    )

with col3:
    st.session_state.total_sqft = st.number_input(
        "Total Sqft",
        min_value=0,
        value=st.session_state.total_sqft,
        step=1
    )

st.divider()

# Annual Operating Costs Section
st.header("💸 Annual Operating Costs")
st.markdown("_Enter costs as dollar amounts_")

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.hoa_fee = st.number_input(
        "HOA Fee ($)",
        min_value=0.0,
        value=st.session_state.hoa_fee,
        step=1.0,
        format="%.2f"
    )
    st.session_state.property_taxes = st.number_input(
        "Property Taxes ($)",
        min_value=0.0,
        value=st.session_state.property_taxes,
        step=1.0,
        format="%.2f"
    )

with col2:
    st.session_state.cam_fee = st.number_input(
        "CAM Fee ($)",
        min_value=0.0,
        value=st.session_state.cam_fee,
        step=1.0,
        format="%.2f"
    )
    st.session_state.insurance = st.number_input(
        "Insurance ($)",
        min_value=0.0,
        value=st.session_state.insurance,
        step=1.0,
        format="%.2f"
    )

with col3:
    st.session_state.misc = st.number_input(
        "Misc ($)",
        min_value=0.0,
        value=st.session_state.misc,
        step=1.0,
        format="%.2f"
    )
    st.session_state.other = st.number_input(
        "Other ($)",
        min_value=0.0,
        value=st.session_state.other,
        step=1.0,
        format="%.2f"
    )

# Calculate Annual Cost (sum of all costs)
st.session_state.annual_cost = (
    st.session_state.hoa_fee +
    st.session_state.cam_fee +
    st.session_state.property_taxes +
    st.session_state.insurance +
    st.session_state.misc +
    st.session_state.other
)

st.markdown("#### 📊 Cost Summary")
st.metric("Annual Cost", format_currency(st.session_state.annual_cost))

st.divider()

# Scenarios Section
st.header("💰 Financing Scenarios")
st.markdown("_Create up to 3 scenarios for comparison_")

# Add scenario button
if len(st.session_state.scenarios) < 3:
    if st.button("➕ Add Scenario", type="primary"):
        st.session_state.scenario_counter += 1
        new_scenario = {
            'id': st.session_state.scenario_counter,
            'type': 'Loan',
            'rate': 7.0,
            'term': 25,
            'loan_percent': 75.0,
            'down_payment_percent': 25.0,
            'additional_startup': 5000.0,
            'adjusted_raise': 175000.0
        }
        st.session_state.scenarios.append(new_scenario)
        st.rerun()

# Display existing scenarios
if len(st.session_state.scenarios) == 0:
    st.info("👆 Click 'Add Scenario' to create your first financing scenario")
else:
    for idx, scenario in enumerate(st.session_state.scenarios):
        with st.expander(f"Scenario {idx + 1}", expanded=True):
            col_header, col_remove = st.columns([6, 1])
            with col_header:
                st.subheader(f"Scenario {idx + 1} Financing Details")
            with col_remove:
                if len(st.session_state.scenarios) > 1:
                    if st.button("🗑️ Remove", key=f"remove_{scenario.get('id')}"):
                        st.session_state.scenarios = [s for s in st.session_state.scenarios if s.get('id') != scenario.get('id')]
                        st.rerun()
            
            # Render scenario inputs
            scenario = render_scenario_inputs(scenario, idx + 1, st.session_state.project_cost)
            
            # Calculate and display metrics
            metrics = calculate_loan_metrics(st.session_state.project_cost, scenario)
            
            st.markdown("#### 📊 Quick Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Loan Amount", format_currency(metrics['loan_amount']))
            with col2:
                st.metric("Down Payment", format_currency(metrics['down_payment']))
            with col3:
                st.metric("Raise", format_currency(metrics['raise_amount']))
            with col4:
                st.metric("Reserve Cash", format_currency(metrics['difference_reserve_cash']))

st.divider()

# Next steps
st.info("💡 **Next Step**: Navigate to '10-Year Cash Flow Analysis' page (Page 3) to set up price per square foot and escalator.")

# Save scenarios back to session state
# (scenarios are already updated in place via render_scenario_inputs)



