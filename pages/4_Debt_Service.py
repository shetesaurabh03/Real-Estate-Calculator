"""Page 3: Debt Service & DSCR"""

import streamlit as st
import pandas as pd
from utils.session_state import initialize_session_state
from utils.calculations import (
    calculate_loan_metrics,
    calculate_monthly_payment,
    calculate_ipmt,
    calculate_total_annual_costs_dollar,
    calculate_noi,
    calculate_price_per_projection
)
from utils.formatters import format_currency, format_percentage

# Initialize session state
initialize_session_state()

st.title("📊 Debt Service & DSCR")
st.markdown("### Page 3: Debt Service Calculations & Coverage Ratios")

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
    st.warning("⚠️ Please create at least one scenario on Page 1 before viewing debt service calculations.")
    st.stop()

# Get annual costs (dollar amounts)
total_annual_costs = calculate_total_annual_costs_dollar(st.session_state.annual_cost)

# Calculate price per projection for Year 1 and Year 10
price_per_projection = calculate_price_per_projection(
    st.session_state.price_per,
    st.session_state.income_escalator,
    years=10
)

# Year 1 income: price_per * total_sqft
price_per_year_1 = price_per_projection.get(1, st.session_state.price_per)
projected_income_y1 = price_per_year_1 * st.session_state.total_sqft

# Year 10 income: price_per (Year 10) * total_sqft
price_per_year_10 = price_per_projection.get(10, st.session_state.price_per)
target_y10_income = price_per_year_10 * st.session_state.total_sqft

# Display for each scenario
for idx, scenario in enumerate(st.session_state.scenarios):
    st.header(f"Scenario {idx + 1}")
    
    # Get scenario values
    interest_rate = scenario.get('rate', 0)
    term_years = scenario.get('term', 25)
    
    # Calculate loan metrics
    loan_metrics = calculate_loan_metrics(st.session_state.project_cost, scenario)
    loan_amount = loan_metrics['loan_amount']
    
    # Calculate values
    interest_monthly_rate = interest_rate / (12 * 100)
    term_months = term_years * 12
    
    # Calculate monthly payment (PMT)
    payment_monthly = 0
    interest_monthly = 0
    annual_debt_payment = 0
    
    if scenario.get('type', 'Loan') == 'Loan' and loan_amount > 0:
        payment_monthly = calculate_monthly_payment(loan_amount, interest_rate, term_years)
        interest_monthly = calculate_ipmt(loan_amount, interest_rate, term_years, period=1)
        annual_debt_payment = payment_monthly * 12
    
    # Calculate DSCR
    dscr_ratio = None
    if annual_debt_payment > 0:
        dscr_ratio = (projected_income_y1 - total_annual_costs) / annual_debt_payment
    
    # Display in a structured format matching requirements
    st.subheader("📋 Loan Parameters & Calculations")
    
    # Display key metrics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Interest:** {format_percentage(interest_rate)} ({format_percentage(interest_monthly_rate, 4)}/month)")
        st.write(f"**Loan:** {format_currency(loan_amount)}")
        st.write(f"**Term:** {term_years} ({term_months})")
        st.write(f"**Interest Monthly:** {format_currency(-interest_monthly)}")
        st.write(f"**Payment Monthly:** {format_currency(-payment_monthly)}")
        st.write(f"**Annual Debt Payment:** {format_currency(annual_debt_payment)}")
    
    with col2:
        st.write(f"**Projected Income Y1:** {format_currency(projected_income_y1)}")
        st.write(f"**Annual Costs:** {format_currency(total_annual_costs)}")
        st.write(f"**DSCR Ratio:** {f'{dscr_ratio:.3f}' if dscr_ratio is not None else 'N/A'}")
        st.write(f"**Target Y10 Income:** {format_currency(target_y10_income)}")
    
    st.divider()
    
    st.subheader("📈 DSCR Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        if dscr_ratio is not None:
            st.metric("DSCR Ratio", f"{dscr_ratio:.3f}")
            # Color-coded DSCR display
            if dscr_ratio < 1.0:
                st.error("🔴 Insufficient income to cover debt")
            elif dscr_ratio < 1.25:
                st.warning("🟡 May not meet lender requirements")
            elif dscr_ratio < 1.5:
                st.info("🟢 Acceptable DSCR")
            else:
                st.success("✅ Strong DSCR")
        else:
            st.metric("DSCR Ratio", "N/A")
            st.info("No debt service for this scenario")
    
    with col2:
        if dscr_ratio is not None:
            calculation_text = f"(Projected Income Y1 - Annual Costs) / Annual Debt Payment"
            st.write(f"**Calculation:**")
            st.write(f"{format_currency(projected_income_y1)} - {format_currency(total_annual_costs)}")
            st.write(f"÷ {format_currency(annual_debt_payment)}")
            st.write(f"= **{dscr_ratio:.3f}**")
    
    st.divider()

st.info("💡 **Next Step**: Navigate to 'Exit & Returns' page to calculate exit price and returns.")

