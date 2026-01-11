# Real Estate Investment Calculator

A comprehensive multi-page Streamlit web application for real estate investment analysis that allows users to create and compare up to 3 financing scenarios side-by-side.

## Features

- **Multi-Scenario Comparison**: Create and compare up to 3 financing scenarios
- **Comprehensive Calculations**: Loan metrics, DSCR, cash flow projections, IRR, waterfall distributions
- **10-Year Projections**: Detailed year-by-year cash flow analysis
- **Exit Analysis**: Calculate exit prices based on cap rates
- **Professional UI**: Clean, intuitive interface with real-time calculations

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
cd real_estate_calculator
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Pages Overview

1. **Project Setup & Financing**: Enter project details and create financing scenarios
2. **Income & Costs**: Configure income projections and operating costs
3. **Debt Service & DSCR**: Calculate debt service and coverage ratios
4. **10-Year Cash Flow Analysis**: View detailed cash flow projections
5. **Exit & Returns**: Calculate exit price, IRR, and cash-on-cash returns
6. **Waterfall Distribution**: Analyze profit distribution to GP and LP
7. **Final Comparison**: Side-by-side comparison of all scenarios

## Project Structure

```
real_estate_calculator/
├── app.py                          # Main entry point
├── requirements.txt
├── README.md
├── utils/
│   ├── __init__.py
│   ├── calculations.py             # All calculation functions
│   ├── formatters.py               # Currency, percentage formatting
│   └── session_state.py            # Session state initialization
├── components/
│   ├── __init__.py
│   └── input_forms.py              # Reusable UI components
└── pages/
    ├── 2_Income_Costs.py
    ├── 3_Debt_Service.py
    ├── 4_Cash_Flow_Analysis.py
    ├── 5_Exit_Returns.py
    ├── 6_Waterfall_Distribution.py
    └── 7_Final_Comparison.py
```

## Usage

1. Start with **Page 1** to enter project details and create scenarios
2. Navigate through pages 2-6 to configure all parameters
3. View the final comparison on **Page 7**
4. Export comparison tables as CSV for further analysis

## Key Calculations

- **Loan Amortization**: Standard loan payment formula
- **DSCR**: Debt Service Coverage Ratio = NOI / Annual Debt Service
- **IRR**: Internal Rate of Return based on cash flows
- **Exit Price**: NOI Year 10 / Exit Cap Rate
- **Cash-on-Cash**: Total Cash Returned / Total Cash Invested

## Notes

- All monetary values are formatted with $ and commas
- Percentages show 2 decimal places
- DSCR shows 3 decimal places
- Session state persists data across all pages
- The application uses manual IRR calculation (Newton-Raphson method) which works with standard numpy




