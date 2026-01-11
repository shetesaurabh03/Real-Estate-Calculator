# AI Coding Agent Instructions for Real Estate Calculator

## Project Overview
This is a **multi-page Streamlit application** for real estate investment analysis. Users create financing scenarios (Loan, Cash, or Hybrid), configure income/costs, and analyze 10-year projections with exit returns and waterfall distributions.

## Architecture & Data Flow

### Page Structure (Streamlit Multi-Page Apps)
- **`app.py`** (Page 1): Project setup, scenario creation, and financing parameters
- **`pages/2_Income_Costs.py`**: Income projections and operating cost configuration
- **`pages/3_Cash_Flow_Analysis.py`**: 10-year year-by-year cash flow display
- **`pages/4_Debt_Service.py`**: DSCR and debt service calculations
- **`pages/5_Exit_Returns.py`**: Exit price, IRR, cash-on-cash return analysis
- **`pages/6_Waterfall_Distribution.py`**: GP/LP profit distribution tiers
- **`pages/7_Final_Comparison.py`**: Side-by-side scenario comparison

### Key Data Flow
1. **Session State** (`utils/session_state.py`): Persists project details and up to 3 scenarios across all pages
2. **Scenarios** stored as list in `st.session_state.scenarios` - each scenario is a dict with `id`, `type`, `loan_percent`, `rate`, `term`, etc.
3. **Calculations** (`utils/calculations.py`): All math functions take project_cost and scenario dict, return numbers or DataFrames
4. **Formatting** (`utils/formatters.py`): Format output (currency, percentages) before display

## Critical Conventions

### Scenario Structure (Dict Keys)
```python
scenario = {
    'id': int,                      # Unique identifier
    'type': 'Loan'|'Cash'|'Hybrid',  # Financing type
    'loan_percent': float,           # % of project cost financed
    'down_payment_percent': float,   # % down payment
    'rate': float,                   # Annual interest rate %
    'term': int,                     # Loan term in years
    'additional_startup': float      # Extra cash needed
}
```

### Calculation Pattern
- Functions accept `project_cost` (scalar) and `scenario` (dict)
- Returns numbers or DataFrames for display
- Examples: `calculate_loan_metrics(project_cost, scenario)`, `calculate_monthly_payment(loan_amount, rate, term)`

### Financial Formulas (Excel Equivalents)
- **Monthly Payment (PMT)**: `M = P × [r(1+r)^n] / [(1+r)^n - 1]` where r = annual_rate/12/100
- **Remaining Principal (FV)**: `FV = PV(1+r)^n - PMT((1+r)^n - 1)/r`
- **DSCR**: `NOI / Annual_Debt_Service`
- **IRR**: Newton-Raphson method (manual implementation in `calculate_irr()`)
- **10-Year Cash Flow**: Projects income with escalator, deducts operating costs and debt service

### UI Input Component Pattern
- Use `render_scenario_inputs(scenario, scenario_num, project_cost)` from `components/input_forms.py`
- All number inputs need unique `key=f"fieldname_{scenario_id}"` to prevent Streamlit rerun issues
- Income/cost inputs stored in session state (e.g., `st.session_state.hoa_fee`, `st.session_state.price_per`)

## Running & Debugging
```bash
# Start the application
streamlit run app.py

# Streamlit auto-reloads on file save
# Check browser console for client-side errors
# Check terminal for Python exceptions and calculations
```

## Common Tasks
- **Add new scenario field**: Add to `initialize_session_state()` default, then to scenario input form
- **New calculation**: Add function to `utils/calculations.py`, import in page that uses it
- **New page**: Create `pages/N_Title.py`, call `initialize_session_state()` at top, import calculations
- **Debugging session state**: Print `st.session_state` in terminal or use `st.write(st.session_state)` in app

## Key Files Reference
- **Calculations**: [utils/calculations.py](utils/calculations.py) (411 lines) - all math logic
- **Session State**: [utils/session_state.py](utils/session_state.py) - single source of truth for state
- **Components**: [components/input_forms.py](components/input_forms.py) - reusable UI
- **Formatters**: [utils/formatters.py](utils/formatters.py) - currency/percentage display
