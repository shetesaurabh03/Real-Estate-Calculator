"""Page 4: Exit & Returns"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.session_state import initialize_session_state
from utils.calculations import (
    calculate_price_per_projection,
    calculate_total_annual_costs_dollar,
    calculate_noi,
    calculate_loan_metrics,
    calculate_monthly_payment,
    calculate_fv
)
from utils.formatters import format_currency, format_percentage

# Initialize session state
initialize_session_state()

st.title("🚪 Exit & Returns")
st.markdown("### Page 4: Exit Price & Return Calculations")

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

# Exit Parameters
st.header("📋 Exit Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.exit_cap_rate = st.number_input(
        "Exit Cap Rate %",
        min_value=0.0,
        max_value=20.0,
        value=st.session_state.exit_cap_rate,
        step=0.1,
        format="%.2f"
    )

with col2:
    st.session_state.years_held = st.number_input(
        "Years Held",
        min_value=1,
        max_value=30,
        value=st.session_state.years_held,
        step=1
    )

with col3:
    st.session_state.total_payments_made = st.number_input(
        "Total Payments Made (months)",
        min_value=1,
        max_value=360,
        value=st.session_state.total_payments_made,
        step=1,
        help="Number of monthly payments made"
    )

# Check if scenarios exist
if len(st.session_state.scenarios) == 0:
    st.warning("⚠️ Please create at least one scenario on Page 1 first.")
    st.stop()

# Get annual costs (dollar amounts)
total_annual_costs = calculate_total_annual_costs_dollar(st.session_state.annual_cost)

# Calculate Target Y10 Income: price_per (Year 10) * total_sqft
price_per_projection = calculate_price_per_projection(
    st.session_state.price_per,
    st.session_state.income_escalator,
    years=10
)
price_per_year_10 = price_per_projection.get(10, st.session_state.price_per)
target_y10_income = price_per_year_10 * st.session_state.total_sqft
noi_year_10 = calculate_noi(target_y10_income, total_annual_costs)

# Display for each scenario
for idx, scenario in enumerate(st.session_state.scenarios):
    st.header(f"Scenario {idx + 1}")
    
    # Get scenario values
    interest_rate = scenario.get('rate', 0)
    
    # Calculate loan metrics
    loan_metrics = calculate_loan_metrics(st.session_state.project_cost, scenario)
    loan_amount = loan_metrics['loan_amount']
    
    # Calculate monthly payment (from debt service page)
    payment_monthly = 0
    if scenario.get('type', 'Loan') == 'Loan' and loan_amount > 0:
        payment_monthly = calculate_monthly_payment(loan_amount, interest_rate, scenario.get('term', 25))
    
    # Calculate Remaining Principal 10 Yr using FV
    # FV(interest/12, Total Payments Made, Monthly Payment, -Loan)
    remaining_principal_10yr = 0
    if scenario.get('type', 'Loan') == 'Loan' and loan_amount > 0 and payment_monthly > 0:
        monthly_rate = interest_rate / 12 / 100
        remaining_principal_10yr = calculate_fv(
            monthly_rate,
            st.session_state.total_payments_made,
            payment_monthly,
            loan_amount
        )
    
    # Calculate Exit Values at different cap rates
    # Base: Target Y10 Income / Exit Cap Rate %
    exit_value_base = target_y10_income / (st.session_state.exit_cap_rate / 100) if st.session_state.exit_cap_rate > 0 else 0
    
    # Exit Cap Rate % + 0.005
    exit_cap_rate_plus = st.session_state.exit_cap_rate + 0.5
    exit_value_plus = target_y10_income / (exit_cap_rate_plus / 100) if exit_cap_rate_plus > 0 else 0
    
    # Exit Cap Rate % - 0.005 (one more based on previous row)
    exit_cap_rate_minus = st.session_state.exit_cap_rate - 0.5
    exit_value_minus = target_y10_income / (exit_cap_rate_minus / 100) if exit_cap_rate_minus > 0 else 0
    
    # Projected Project Equity = 2nd row (Exit Cap Rate % + 0.005) exit value - Remaining Principal
    projected_project_equity = exit_value_base - remaining_principal_10yr
    
    # Display Loan Parameters
    st.subheader("📋 Loan Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Loan Amount:** {format_currency(loan_amount)}")
        st.write(f"**Monthly Payment:** {format_currency(-payment_monthly)}")
        st.write(f"**Total Payments Made:** {st.session_state.total_payments_made} months")
        st.write(f"**Remaining Principal 10 Yr:** {format_currency(remaining_principal_10yr)}")
    
    with col2:
        st.write(f"**Target Y10 Income:** {format_currency(target_y10_income)}")
        #st.write(f"**NOI Year 10:** {format_currency(noi_year_10)}")
    
    st.divider()
    
    # Display Exit Value Calculations
    st.subheader("📊 Exit Value Calculations")
    
    # Create table for exit values
    exit_data = {
        'Exit Cap Rate %': [
            format_percentage(st.session_state.exit_cap_rate),
            format_percentage(exit_cap_rate_plus, 2),
            format_percentage(exit_cap_rate_minus, 2)
        ],
        'Exit Value': [
            format_currency(exit_value_base),
            format_currency(exit_value_plus),
            format_currency(exit_value_minus)
        ]
    }
    
    df_exit = pd.DataFrame(exit_data)
    st.dataframe(df_exit, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Display Projected Project Equity
    st.subheader("📈 Projected Project Equity")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Projected Project Equity",
            format_currency(projected_project_equity),
            help="Exit Value (at Exit Cap Rate % + 0.5) - Remaining Principal 10 Yr"
        )
    
    with col2:
        st.write(f"**Calculation:**")
        st.write(f"{format_currency(exit_value_base)} - {format_currency(remaining_principal_10yr)}")
        st.write(f"= **{format_currency(projected_project_equity)}**")
    
    st.divider()

st.info("💡 **Next Step**: Navigate to 'Waterfall Distribution' page to see profit splits.")

