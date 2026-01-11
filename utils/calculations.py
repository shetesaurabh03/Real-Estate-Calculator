"""All calculation functions for real estate investment analysis"""

import numpy as np
import pandas as pd
from .formatters import format_currency, format_percentage


def calculate_loan_metrics(project_cost, scenario):
    """
    Calculate loan amount, down payment, raise, and reserve cash for a scenario
    
    Returns:
        dict: Contains loan_amount, down_payment, raise_amount, difference_reserve_cash
    """
    loan_amount = project_cost * (scenario.get('loan_percent', 0) / 100)
    down_payment = project_cost * (scenario.get('down_payment_percent', 0) / 100)
    raise_amount = down_payment + scenario.get('additional_startup', 0)
    adjusted_raise = scenario.get('adjusted_raise', 0)
    difference_reserve_cash = adjusted_raise - raise_amount
    
    return {
        'loan_amount': loan_amount,
        'down_payment': down_payment,
        'raise_amount': raise_amount,
        'difference_reserve_cash': difference_reserve_cash
    }


def calculate_monthly_payment(loan_amount, annual_rate, term_years):
    """
    Calculate monthly loan payment using standard amortization formula (PMT function)
    
    Excel: -PMT(interest/12, term*12, loan)
    M = P × [r(1+r)^n] / [(1+r)^n - 1]
    Where:
    P = Loan Amount
    r = Monthly interest rate (annual rate / 12 / 100)
    n = Number of payments (term × 12)
    """
    if loan_amount <= 0 or term_years <= 0:
        return 0.0
    
    if annual_rate == 0:
        return loan_amount / (term_years * 12)
    
    monthly_rate = annual_rate / 12 / 100
    num_payments = term_years * 12
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
              ((1 + monthly_rate)**num_payments - 1)
    
    return payment


def calculate_fv(rate, nper, pmt, pv):
    """
    Calculate Future Value (FV function - Excel equivalent)
    
    Excel: FV(rate, nper, pmt, pv)
    
    For remaining principal on a loan:
    FV = PV*(1+r)^n - PMT*((1+r)^n - 1)/r
    
    Args:
        rate: Interest rate per period (monthly rate = annual_rate/12/100)
        nper: Number of periods (number of payments made)
        pmt: Payment per period (monthly payment)
        pv: Present value (loan amount, positive)
    
    Returns:
        float: Future value (remaining principal)
    """
    if rate == 0:
        return pv - (pmt * nper)
    
    fv = pv * ((1 + rate)**nper) - pmt * (((1 + rate)**nper - 1) / rate)
    return max(0, fv)  # Remaining principal cannot be negative


def calculate_remaining_principal(loan_amount, annual_rate, term_years, payments_made):
    """
    Calculate remaining principal after a number of payments.

    Args:
        loan_amount: Original loan principal (positive)
        annual_rate: Annual interest rate as percentage (e.g., 5.0)
        term_years: Loan term in years used to compute the payment schedule
        payments_made: Number of payments already made (periods, typically months)

    Returns:
        float: Remaining principal (>= 0)
    """
    if loan_amount <= 0 or term_years <= 0 or payments_made <= 0:
        return 0.0

    monthly_rate = annual_rate / 12 / 100
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, term_years)

    return calculate_fv(monthly_rate, payments_made, monthly_payment, loan_amount)


def calculate_ipmt(loan_amount, annual_rate, term_years, period=1):
    """
    Calculate interest payment for a specific period (IPMT function)
    
    Excel: -IPMT(interest/12, period, term*12, loan)
    
    Args:
        loan_amount: Principal loan amount
        annual_rate: Annual interest rate as percentage
        term_years: Loan term in years
        period: Payment period (1 for first payment)
    
    Returns:
        float: Interest payment for the period
    """
    if loan_amount <= 0 or term_years <= 0 or period < 1:
        return 0.0
    
    monthly_rate = annual_rate / 12 / 100
    num_payments = term_years * 12
    
    if monthly_rate == 0:
        return 0.0
    
    # Remaining principal at the start of the period
    if period == 1:
        remaining_principal = loan_amount
    else:
        # Calculate remaining principal after (period-1) payments
        monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, term_years)
        remaining_principal = loan_amount * ((1 + monthly_rate)**num_payments - (1 + monthly_rate)**(period - 1)) / \
                             ((1 + monthly_rate)**num_payments - 1)
    
    interest_payment = remaining_principal * monthly_rate
    return interest_payment


def calculate_annual_debt_service(loan_amount, annual_rate, term_years):
    """Calculate annual debt service (monthly payment × 12)"""
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, term_years)
    return monthly_payment * 12


def calculate_noi(gross_income, total_annual_costs):
    """
    Calculate Net Operating Income
    
    NOI = Gross Income - Operating Costs
    """
    return gross_income - total_annual_costs


def calculate_dscr(noi, annual_debt_service):
    """
    Calculate Debt Service Coverage Ratio
    
    DSCR = NOI / Annual Debt Service
    """
    if annual_debt_service == 0:
        return None
    return noi / annual_debt_service


def calculate_income_projection(year_1_income, escalator, years=10):
    """
    Project income with annual escalation
    
    Returns:
        dict: Year-by-year income projections
    """
    projections = {}
    current_income = year_1_income
    
    for year in range(1, years + 1):
        projections[year] = current_income
        current_income = current_income * (1 + escalator / 100)
    
    return projections


def calculate_price_per_projection(price_per, escalator, years=10):
    """
    Project Price Per with annual escalation
    
    Formula: Price Per * (1 + (escalator / 100)) for each year
    
    Returns:
        dict: Year-by-year Price Per projections
    """
    projections = {}
    current_price = price_per
    
    for year in range(1, years + 1):
        projections[year] = current_price
        current_price = current_price * (1 + escalator / 100)
    
    return projections


def calculate_rent_projection(price_per, total_sqft, escalator, years=10):
    """
    Calculate rent projection: Rent = Price Per * Total Sqft for each year
    with annual escalation on Price Per
    
    Returns:
        dict: Year-by-year rent projections
    """
    price_per_projection = calculate_price_per_projection(price_per, escalator, years)
    rent_projection = {}
    
    for year in range(1, years + 1):
        rent_projection[year] = price_per_projection[year] * total_sqft
    
    return rent_projection


def calculate_total_annual_costs(year_1_income, cost_percentages):
    """
    Calculate total annual operating costs (using percentages - deprecated)
    
    Args:
        year_1_income: Year 1 gross income
        cost_percentages: dict with cost percentages (e.g., {'hoa': 1.0, 'cam': 1.0, ...})
    
    Returns:
        float: Total annual operating costs
    """
    total_pct = sum(cost_percentages.values())
    return year_1_income * (total_pct / 100)


def calculate_total_annual_costs_dollar(annual_cost):
    """
    Calculate total annual operating costs from dollar amount
    
    Args:
        annual_cost: Total annual cost in dollars (sum of all cost components)
    
    Returns:
        float: Total annual operating costs
    """
    return annual_cost


def calculate_10_year_cash_flow(scenario, price_per_projection, total_sqft, annual_costs, project_cost, adjusted_percent=0.85, gp_percent=0.20, lp_percent=0.80):
    """
    Calculate year-by-year cash flow for 10 years
    
    Args:
        scenario: Scenario dictionary
        price_per_projection: Dictionary of year -> price_per values
        total_sqft: Total square feet
        annual_costs: Annual operating costs
        project_cost: Total project cost
        adjusted_percent: Percentage of cash flow to adjust (default 0.85 = 85%)
        gp_percent: General Partner percentage of adjusted cash flow (default 0.20 = 20%)
        lp_percent: Limited Partner percentage of adjusted cash flow (default 0.80 = 80%)
    
    Returns:
        pd.DataFrame: DataFrame with Year, Rent, Cash Flow, Adjusted %, GP %, LP %, LP CoC
    """
    loan_metrics = calculate_loan_metrics(project_cost, scenario)
    loan_amount = loan_metrics['loan_amount']
    
    # Calculate annual debt service
    annual_debt_service = 0
    if scenario.get('type', 'Loan') == 'Loan':
        annual_debt_service = calculate_annual_debt_service(
            loan_amount,
            scenario.get('rate', 0),
            scenario.get('term', 25)
        )
    
    # Get adjusted raise for LP CoC calculation
    adjusted_raise = scenario.get('adjusted_raise', 0)
    
    data = []
    
    for year in range(1, 11):
        # Calculate rent: price_per * total_sqft
        price_per = price_per_projection.get(year, 0)
        rent = price_per * total_sqft
        
        cash_flow = rent - annual_costs - annual_debt_service
        adjusted = cash_flow * adjusted_percent
        gp_amount = adjusted * gp_percent
        lp_amount = adjusted * lp_percent
        
        # LP CoC = (LP amount / adjusted_raise) * 100
        lp_coc = (lp_amount / adjusted_raise * 100) if adjusted_raise > 0 else 0
        
        data.append({
            'Year': year,
            'Rent': rent,
            'Cash Flow': cash_flow,
            'Adjusted %': adjusted,
            'GP %': gp_amount,
            'LP %': lp_amount,
            'LP CoC': lp_coc
        })
    
    return pd.DataFrame(data)


def calculate_irr(initial_investment, cash_flows):
    """
    Calculate Internal Rate of Return
    
    Args:
        initial_investment: Initial cash outflow (negative)
        cash_flows: List of cash flows (positive for inflows)
    
    Returns:
        float: IRR as percentage, or None if calculation fails
    """
    try:
        # Combine initial investment (negative) with cash flows
        all_cash_flows = [-abs(initial_investment)] + list(cash_flows)
        
        # Try using numpy financial if available
        try:
            from numpy_financial import irr as np_irr
            irr = np_irr(all_cash_flows)
            if irr is not None:
                return irr * 100  # Convert to percentage
        except ImportError:
            pass
        
        # Manual IRR calculation using Newton-Raphson method
        irr = calculate_irr_manual(all_cash_flows)
        
        if irr is not None:
            return irr * 100  # Convert to percentage
        
        return None
    except:
        # Fallback manual calculation
        try:
            all_cash_flows = [-abs(initial_investment)] + list(cash_flows)
            return calculate_irr_manual(all_cash_flows) * 100
        except:
            return None


def calculate_irr_manual(cash_flows, guess=0.1, tolerance=1e-6, max_iter=100):
    """
    Manual IRR calculation using Newton-Raphson method
    """
    def npv(rate):
        return sum([cf / (1 + rate)**i for i, cf in enumerate(cash_flows)])
    
    def npv_derivative(rate):
        return sum([-i * cf / (1 + rate)**(i+1) for i, cf in enumerate(cash_flows)])
    
    rate = guess
    for _ in range(max_iter):
        npv_val = npv(rate)
        if abs(npv_val) < tolerance:
            return rate
        npv_deriv = npv_derivative(rate)
        if abs(npv_deriv) < tolerance:
            break
        rate = rate - npv_val / npv_deriv
    
    return None


def calculate_exit_price(noi_year_10, exit_cap_rate):
    """
    Calculate exit price based on cap rate
    
    Exit Price = NOI Year 10 / (Exit Cap Rate / 100)
    """
    if exit_cap_rate == 0:
        return None
    return noi_year_10 / (exit_cap_rate / 100)


def calculate_cash_on_cash(total_cash_returned, total_cash_invested):
    """
    Calculate cash-on-cash return
    
    Returns multiplier (e.g., 4.17x)
    """
    if total_cash_invested == 0:
        return None
    return total_cash_returned / total_cash_invested


def calculate_waterfall_distribution(left_to_distribute, adjusted_raise, gp_percent, lp_percent, hurdle_rate, years_held):
    """
    Calculate tiered waterfall distribution with hurdle returns
    
    Args:
        left_to_distribute: Total amount to distribute (sum of 10-year cash flows + projected equity)
        adjusted_raise: Initial LP investment (adjusted raise)
        gp_percent: GP ownership percentage (e.g., 20)
        lp_percent: LP ownership percentage (e.g., 80)
        hurdle_rate: Hurdle rate percentage (e.g., 8)
        years_held: Number of years held (typically 10)
    
    Returns:
        dict: Detailed waterfall distribution by tier and remaining amounts
    """
    
    # Tier returns (from distribution_tiers)
    tiers = {
        'tier1': {'return': 8, 'lp': 80, 'gp': 20},
        'tier2': {'return': 15, 'lp': 70, 'gp': 30},
        'tier3': {'return': 50, 'lp': 50, 'gp': 50}
    }
    
    # Initialize tracking
    remaining = left_to_distribute
    tier_distributions = {}
    gp_total = 0
    lp_total = 0
    
    # First Tier: LPs get hurdle return
    hurdle_return = adjusted_raise * (((1 + hurdle_rate / 100) ** years_held) - 1)
    
    if remaining >= hurdle_return:
        tier_distributions['hurdle'] = {
            'return_percent': hurdle_rate,
            'amount': hurdle_return,
            'gp': 0,
            'lp': hurdle_return
        }
        lp_total += hurdle_return
        remaining -= hurdle_return
    else:
        # Partial hurdle distribution
        tier_distributions['hurdle'] = {
            'return_percent': hurdle_rate,
            'amount': remaining,
            'gp': 0,
            'lp': remaining
        }
        lp_total += remaining
        remaining = 0
    
    # Distribute remaining by tier
    for tier_name, tier_config in tiers.items():
        if remaining <= 0:
            tier_distributions[tier_name] = {
                'return_percent': tier_config['return'],
                'amount': 0,
                'gp': 0,
                'lp': 0
            }
            continue
        
        # For each tier, distribute the entire remaining amount (not capped per tier)
        # GP gets: (amount / (GP%/100)) * (LP%/100)
        # LP gets: amount - GP amount
        gp_share_from_remaining = (remaining / (gp_percent / 100)) * (lp_percent / 100)
        
        # Ensure we don't exceed remaining
        if gp_share_from_remaining <= remaining:
            gp_amount = gp_share_from_remaining
            lp_amount = remaining - gp_amount
        else:
            # If formula exceeds remaining, split by percentages
            gp_amount = remaining * (gp_percent / 100)
            lp_amount = remaining * (lp_percent / 100)
        
        tier_distributions[tier_name] = {
            'return_percent': tier_config['return'],
            'amount': remaining,
            'gp': gp_amount,
            'lp': lp_amount
        }
        
        gp_total += gp_amount
        lp_total += lp_amount
        remaining -= (gp_amount + lp_amount)
    
    # Summary
    total_distributed = left_to_distribute - remaining
    
    return {
        'left_to_distribute': left_to_distribute,
        'adjusted_raise': adjusted_raise,
        'tier_distributions': tier_distributions,
        'gp_total': gp_total,
        'lp_total': lp_total,
        'total_distributed': total_distributed,
        'left_over': remaining,
        'lp_multiple': (adjusted_raise + lp_total) / adjusted_raise if adjusted_raise > 0 else 0
    }



