"""Page 6: Final Comparison"""

import streamlit as st
import pandas as pd
from utils.session_state import initialize_session_state
from utils.calculations import (
    calculate_loan_metrics,
    calculate_annual_debt_service,
    calculate_noi,
    calculate_dscr,
    calculate_total_annual_costs_dollar,
    calculate_price_per_projection,
    calculate_10_year_cash_flow,
    calculate_exit_price,
    calculate_irr,
    calculate_cash_on_cash,
    calculate_waterfall_distribution
)
from utils.formatters import format_currency, format_percentage

# Initialize session state
initialize_session_state()

st.title("📊 Final Comparison")
st.markdown("### Page 6: Side-by-Side Scenario Comparison")

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

# Get all necessary data
total_annual_costs = calculate_total_annual_costs_dollar(st.session_state.annual_cost)

# Calculate Year 1 income: price_per * total_sqft
year_1_income = st.session_state.price_per * st.session_state.total_sqft
noi = calculate_noi(year_1_income, total_annual_costs)

price_per_projection = calculate_price_per_projection(
    st.session_state.price_per,
    st.session_state.income_escalator,
    years=10
)

price_per_year_10 = price_per_projection.get(10, st.session_state.price_per)
year_10_income = price_per_year_10 * st.session_state.total_sqft
noi_year_10 = calculate_noi(year_10_income, total_annual_costs)
exit_price = calculate_exit_price(noi_year_10, st.session_state.exit_cap_rate)

# Build comparison table
comparison_data = {
    'Metric': []
}

# Initialize scenario columns
for idx in range(len(st.session_state.scenarios)):
    comparison_data[f'Scenario {idx + 1}'] = []

def add_metric_row(metric_name, values):
    """Helper to add a row to comparison table"""
    comparison_data['Metric'].append(metric_name)
    for idx, value in enumerate(values):
        comparison_data[f'Scenario {idx + 1}'].append(value)

# Project Details
add_metric_row('--- Project Details ---', [''] * len(st.session_state.scenarios))
add_metric_row('Project Name', [st.session_state.project_name] * len(st.session_state.scenarios))
add_metric_row('Project Cost', [format_currency(st.session_state.project_cost)] * len(st.session_state.scenarios))
add_metric_row('', [''] * len(st.session_state.scenarios))

# Financing Details
add_metric_row('--- Financing Details ---', [''] * len(st.session_state.scenarios))

financing_values = []
for scenario in st.session_state.scenarios:
    metrics = calculate_loan_metrics(st.session_state.project_cost, scenario)
    financing_values.append({
        'type': scenario.get('type', 'N/A'),
        'loan_amount': format_currency(metrics['loan_amount']),
        'down_payment': format_currency(metrics['down_payment']),
        'raise': format_currency(metrics['raise_amount']),
        'reserve_cash': format_currency(metrics['difference_reserve_cash']),
        'rate': format_percentage(scenario.get('rate', 0)),
        'term': str(scenario.get('term', 0)),
        'loan_pct': format_percentage(scenario.get('loan_percent', 0)),
        'down_pct': format_percentage(scenario.get('down_payment_percent', 0)),
        'adjusted_raise': format_currency(scenario.get('adjusted_raise', 0))
    })

for key in ['type', 'loan_amount', 'down_payment', 'raise', 'reserve_cash', 'rate', 'term', 'loan_pct', 'down_pct', 'adjusted_raise']:
    add_metric_row(key.replace('_', ' ').title(), [v[key] for v in financing_values])

add_metric_row('', [''] * len(st.session_state.scenarios))

# Year 1 Performance
add_metric_row('--- Year 1 Performance ---', [''] * len(st.session_state.scenarios))

year1_values = []
for scenario in st.session_state.scenarios:
    metrics = calculate_loan_metrics(st.session_state.project_cost, scenario)
    loan_amount = metrics['loan_amount']
    
    annual_debt_service = 0
    if scenario.get('type', 'Loan') == 'Loan' and loan_amount > 0:
        annual_debt_service = calculate_annual_debt_service(
            loan_amount,
            scenario.get('rate', 0),
            scenario.get('term', 25)
        )
    
    dscr = calculate_dscr(noi, annual_debt_service) if annual_debt_service > 0 else None
    
    year1_values.append({
        'gross_income': format_currency(year_1_income),
        'noi': format_currency(noi),
        'dscr': f"{dscr:.3f}" if dscr else "N/A",
        'debt_service': format_currency(annual_debt_service)
    })

for key in ['gross_income', 'noi', 'dscr', 'debt_service']:
    add_metric_row(key.replace('_', ' ').title(), [v[key] for v in year1_values])

add_metric_row('', [''] * len(st.session_state.scenarios))

# 10-Year Performance
add_metric_row('--- 10-Year Performance ---', [''] * len(st.session_state.scenarios))

tenyear_values = []
for scenario in st.session_state.scenarios:
    df_cash_flow = calculate_10_year_cash_flow(
        scenario,
        price_per_projection,
        st.session_state.total_sqft,
        total_annual_costs,
        st.session_state.project_cost
    )
    
    total_cash_flow = df_cash_flow['Cash Flow'].sum()
    avg_annual_cash_flow = df_cash_flow['Cash Flow'].mean()
    
    tenyear_values.append({
        'total_cash_flow': format_currency(total_cash_flow),
        'avg_annual_cash_flow': format_currency(avg_annual_cash_flow)
    })

for key in ['total_cash_flow', 'avg_annual_cash_flow']:
    add_metric_row(key.replace('_', ' ').title(), [v[key] for v in tenyear_values])

add_metric_row('', [''] * len(st.session_state.scenarios))

# Exit & Returns
add_metric_row('--- Exit & Returns ---', [''] * len(st.session_state.scenarios))

exit_values = []
for scenario in st.session_state.scenarios:
    df_cash_flow = calculate_10_year_cash_flow(
        scenario,
        price_per_projection,
        st.session_state.total_sqft,
        total_annual_costs,
        st.session_state.project_cost
    )
    
    cash_flows = df_cash_flow['Adjusted %'].tolist()
    initial_investment = scenario.get('adjusted_raise', 0)
    irr = calculate_irr(initial_investment, cash_flows + [exit_price])
    total_cash_returned = sum(cash_flows) + exit_price
    coc_mult = calculate_cash_on_cash(total_cash_returned, initial_investment)
    
    exit_values.append({
        'exit_price': format_currency(exit_price) if exit_price else "N/A",
        'project_irr': format_percentage(irr, 2) if irr else "N/A",
        'cash_on_cash': f"{coc_mult:.2f}x" if coc_mult else "N/A"
    })

for key in ['exit_price', 'project_irr', 'cash_on_cash']:
    add_metric_row(key.replace('_', ' ').title(), [v[key] for v in exit_values])

add_metric_row('', [''] * len(st.session_state.scenarios))

# Waterfall
add_metric_row('--- Waterfall Distribution ---', [''] * len(st.session_state.scenarios))

waterfall_values = []
for scenario in st.session_state.scenarios:
    df_cash_flow = calculate_10_year_cash_flow(
        scenario,
        price_per_projection,
        st.session_state.total_sqft,
        total_annual_costs,
        st.session_state.project_cost
    )
    
    total_cash_flows = df_cash_flow['Adjusted %'].sum()
    total_proceeds = total_cash_flows + exit_price
    amount_raised = scenario.get('adjusted_raise', 0)
    
    waterfall = calculate_waterfall_distribution(
        total_proceeds,
        amount_raised,
        st.session_state.gp_percent,
        st.session_state.lp_percent,
        st.session_state.hurdle_rate,
        st.session_state.years_held
    )
    
    waterfall_values.append({
        'gp_return': format_currency(waterfall.get('gp_total', 0)),
        'lp_return': format_currency(waterfall.get('lp_total', 0)),
        'lp_multiple': f"{waterfall.get('lp_multiple', 0):.2f}x" if waterfall.get('lp_multiple') else "N/A"
    })

for key in ['gp_return', 'lp_return', 'lp_multiple']:
    add_metric_row(key.replace('_', ' ').title(), [v[key] for v in waterfall_values])

# Create and display DataFrame
df_comparison = pd.DataFrame(comparison_data)

st.header("📊 Side-by-Side Comparison")
st.dataframe(df_comparison, hide_index=True, use_container_width=True, height=800)

# Download button
csv = df_comparison.to_csv(index=False)
st.download_button(
    label="📥 Download Comparison as CSV",
    data=csv,
    file_name=f"{st.session_state.project_name.replace(' ', '_')}_comparison.csv",
    mime="text/csv",
    use_container_width=True,
    type="primary"
)

st.success("✅ Comparison complete! Review all scenarios side-by-side above.")



