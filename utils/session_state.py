"""Session state initialization for the real estate calculator"""

import streamlit as st
from datetime import date

def initialize_session_state():
    """Initialize all session state variables with default values"""
    
    # Project Details (Fixed across all scenarios)
    if 'project_name' not in st.session_state:
        st.session_state.project_name = "620 Glen Iris Unit 101"
    if 'anticipated_start' not in st.session_state:
        st.session_state.anticipated_start = date(2025, 12, 1)
    if 'asset_class' not in st.session_state:
        st.session_state.asset_class = "Mixed-Use"
    if 'project_cost' not in st.session_state:
        st.session_state.project_cost = 550000.0
    if 'total_sqft' not in st.session_state:
        st.session_state.total_sqft = 1500
    
    # Scenarios (up to 3)
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    if 'scenario_counter' not in st.session_state:
        st.session_state.scenario_counter = 0
    
    # Income & Costs (Price Per and Escalator)
    if 'income_escalator' not in st.session_state:
        st.session_state.income_escalator = 3.0
    if 'price_per' not in st.session_state:
        st.session_state.price_per = 35.0  # Price per square foot (default)
    
    # Annual Operating Costs ($ amounts)
    if 'hoa_fee' not in st.session_state:
        st.session_state.hoa_fee = 0.0
    if 'cam_fee' not in st.session_state:
        st.session_state.cam_fee = 0.0
    if 'property_taxes' not in st.session_state:
        st.session_state.property_taxes = 0.0
    if 'insurance' not in st.session_state:
        st.session_state.insurance = 0.0
    if 'misc' not in st.session_state:
        st.session_state.misc = 0.0
    if 'other' not in st.session_state:
        st.session_state.other = 0.0
    if 'annual_cost' not in st.session_state:
        st.session_state.annual_cost = 0.0
    
    # Exit Parameters
    if 'exit_cap_rate' not in st.session_state:
        st.session_state.exit_cap_rate = 6.50
    if 'years_held' not in st.session_state:
        st.session_state.years_held = 10
    if 'total_payments_made' not in st.session_state:
        st.session_state.total_payments_made = 120  # Default 10 years * 12 months
    
    # Waterfall Parameters
    if 'gp_percent' not in st.session_state:
        st.session_state.gp_percent = 20.0
    if 'lp_percent' not in st.session_state:
        st.session_state.lp_percent = 80.0
    if 'hurdle_rate' not in st.session_state:
        st.session_state.hurdle_rate = 8.0
    if 'distribution_tiers' not in st.session_state:
        st.session_state.distribution_tiers = {
            'tier1': {'lp': 80, 'gp': 20},
            'tier2': {'lp': 70, 'gp': 30},
            'tier3': {'lp': 50, 'gp': 50}
        }



