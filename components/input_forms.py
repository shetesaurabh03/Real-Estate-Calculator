"""Reusable UI input components"""

import streamlit as st

def render_scenario_inputs(scenario, scenario_num, project_cost):
    """Render input form for a single scenario"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        scenario['type'] = st.selectbox(
            "Type",
            options=['Loan', 'Cash', 'Hybrid'],
            index=['Loan', 'Cash', 'Hybrid'].index(scenario.get('type', 'Loan')) if scenario.get('type', 'Loan') in ['Loan', 'Cash', 'Hybrid'] else 0,
            key=f"type_{scenario.get('id')}"
        )
        scenario['loan_percent'] = st.number_input(
            "Loan %",
            min_value=0.0,
            max_value=100.0,
            value=scenario.get('loan_percent', 75.0),
            step=0.01,
            format="%.2f",
            key=f"loan_pct_{scenario.get('id')}"
        )
    
    with col2:
        scenario['rate'] = st.number_input(
            "Interest Rate %",
            min_value=0.0,
            max_value=30.0,
            value=scenario.get('rate', 7.0),
            step=0.01,
            format="%.2f",
            key=f"rate_{scenario.get('id')}"
        )
        scenario['down_payment_percent'] = st.number_input(
            "Down Payment %",
            min_value=0.0,
            max_value=100.0,
            value=scenario.get('down_payment_percent', 25.0),
            step=0.01,
            format="%.2f",
            key=f"down_pct_{scenario.get('id')}"
        )
    
    with col3:
        scenario['term'] = st.number_input(
            "Term (years)",
            min_value=1,
            max_value=50,
            value=scenario.get('term', 25),
            step=1,
            key=f"term_{scenario.get('id')}"
        )
        scenario['additional_startup'] = st.number_input(
            "Additional Startup $",
            min_value=0.0,
            value=scenario.get('additional_startup', 5000.0),
            step=100.0,
            format="%.2f",
            key=f"startup_{scenario.get('id')}"
        )
    
    with col4:
        st.write("")  # Spacer
        scenario['adjusted_raise'] = st.number_input(
            "Adjusted Raise $",
            min_value=0.0,
            value=scenario.get('adjusted_raise', 175000.0),
            step=1000.0,
            format="%.2f",
            key=f"raise_{scenario.get('id')}"
        )
    
    # Validation warning
    loan_pct = scenario.get('loan_percent', 0)
    down_pct = scenario.get('down_payment_percent', 0)
    if abs(loan_pct + down_pct - 100.0) > 0.01:
        st.warning(f"⚠️ Loan % ({loan_pct:.2f}%) + Down Payment % ({down_pct:.2f}%) ≠ 100%")
    
    return scenario




