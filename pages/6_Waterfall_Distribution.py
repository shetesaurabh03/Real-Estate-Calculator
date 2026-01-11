"""Page 5: Waterfall Distribution"""

import streamlit as st
import pandas as pd
from utils.session_state import initialize_session_state
from utils.calculations import (
    calculate_price_per_projection,
    calculate_total_annual_costs_dollar,
    calculate_noi,
    calculate_exit_price,
    calculate_10_year_cash_flow,
    calculate_waterfall_distribution,
    calculate_loan_metrics,
    calculate_remaining_principal
)
from utils.formatters import format_currency, format_percentage

# Initialize session state
initialize_session_state()

st.title("💧 Waterfall Distribution")
st.markdown("### Page 5: Profit Distribution & Returns")

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

# Waterfall Parameters
st.header("⚙️ Waterfall Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.gp_percent = st.number_input(
        "GP %",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.gp_percent,
        step=0.1,
        format="%.2f"
    )

with col2:
    st.session_state.lp_percent = st.number_input(
        "LP %",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.lp_percent,
        step=0.1,
        format="%.2f"
    )

with col3:
    st.session_state.hurdle_rate = st.number_input(
        "Hurdle Rate %",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.hurdle_rate,
        step=0.1,
        format="%.2f"
    )

if abs(st.session_state.gp_percent + st.session_state.lp_percent - 100.0) > 0.01:
    st.warning(f"⚠️ GP % ({st.session_state.gp_percent}%) + LP % ({st.session_state.lp_percent}%) ≠ 100%")

# Check if scenarios exist
if len(st.session_state.scenarios) == 0:
    st.warning("⚠️ Please create at least one scenario on Page 1 first.")
    st.stop()

# Get annual costs (dollar amounts)
total_annual_costs = calculate_total_annual_costs_dollar(st.session_state.annual_cost)

# Calculate Year 10 income and NOI
price_per_projection = calculate_price_per_projection(
    st.session_state.price_per,
    st.session_state.income_escalator,
    years=10
)
price_per_year_10 = price_per_projection.get(10, st.session_state.price_per)
year_10_income = price_per_year_10 * st.session_state.total_sqft
noi_year_10 = calculate_noi(year_10_income, total_annual_costs)
exit_price = calculate_exit_price(noi_year_10, st.session_state.exit_cap_rate)

# Display for each scenario
for idx, scenario in enumerate(st.session_state.scenarios):
    st.header(f"Scenario {idx + 1}")
    
    # Get cash flows
    df_cash_flow = calculate_10_year_cash_flow(
        scenario,
        price_per_projection,
        st.session_state.total_sqft,
        total_annual_costs,
        st.session_state.project_cost
    )
    
    # Calculate total cash flows from 10-year projection
    total_cash_flows = df_cash_flow['Adjusted %'].sum()
    
    # Get projected project equity from exit value calculation
    loan_metrics = calculate_loan_metrics(st.session_state.project_cost, scenario)
    remaining_principal_10yr = calculate_remaining_principal(
        loan_metrics['loan_amount'],
        scenario.get('rate', 0),
        scenario.get('term', 25),
        120  # 10 years * 12 months
    )
    
    exit_value_base = exit_price
    projected_project_equity = exit_value_base - remaining_principal_10yr
    
    # Calculate left to be distributed
    left_to_distribute = total_cash_flows + projected_project_equity
    
    # Amount raised (adjusted LP investment)
    adjusted_raise = scenario.get('adjusted_raise', 0)
    
    # Calculate waterfall distribution
    waterfall = calculate_waterfall_distribution(
        left_to_distribute,
        adjusted_raise,
        st.session_state.gp_percent,
        st.session_state.lp_percent,
        st.session_state.hurdle_rate,
        st.session_state.years_held
    )
    
    # Display summary metrics
    st.subheader("📊 Distribution Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Amount Raised", format_currency(adjusted_raise))
    with col2:
        st.metric("Left to Distribute", format_currency(left_to_distribute))
    with col3:
        st.metric("Total GP Return", format_currency(waterfall['gp_total']))
    with col4:
        lp_mult_display = f"{waterfall['lp_multiple']:.2f}x" if waterfall['lp_multiple'] else "N/A"
        st.metric("LP Multiple", lp_mult_display)
    
    st.divider()
    
    # Display tiered distribution table
    st.subheader("💧 Tiered Waterfall Distribution")
    
    waterfall_data = {
        'Tier': [],
        'Return %': [],
        'Amount Distributed': [],
        'GP Distribution': [],
        'LP Distribution': []
    }
    
    for tier_name, tier_info in waterfall['tier_distributions'].items():
        tier_label = tier_name.replace('_', ' ').title()
        waterfall_data['Tier'].append(tier_label)
        waterfall_data['Return %'].append(f"{tier_info['return_percent']}%")
        waterfall_data['Amount Distributed'].append(format_currency(tier_info['amount']))
        waterfall_data['GP Distribution'].append(format_currency(tier_info['gp']))
        waterfall_data['LP Distribution'].append(format_currency(tier_info['lp']))
    
    df_waterfall = pd.DataFrame(waterfall_data)
    st.dataframe(df_waterfall, hide_index=True, use_container_width=True)
    
    # Display totals
    st.subheader("📈 Final Distribution Totals")
    
    totals_data = {
        'Category': ['GP Total', 'LP Total', 'Total Distributed', 'Remaining/Left Over'],
        'Amount': [
            format_currency(waterfall['gp_total']),
            format_currency(waterfall['lp_total']),
            format_currency(waterfall['total_distributed']),
            format_currency(waterfall['left_over'])
        ]
    }
    
    df_totals = pd.DataFrame(totals_data)
    st.dataframe(df_totals, hide_index=True, use_container_width=True)
    
    st.divider()

st.info("💡 **Next Step**: Navigate to 'Final Comparison' page to see side-by-side comparison of all scenarios.")



