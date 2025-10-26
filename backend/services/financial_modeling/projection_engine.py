"""
Financial Projection Engine
Generates detailed financial projections based on historical data and assumptions
Matches the structure of the provided cash flow template
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from loguru import logger
from dataclasses import dataclass, asdict
from enum import Enum


class ProjectionPeriod(Enum):
    """Projection period types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class ScenarioType(Enum):
    """Scenario types for what-if analysis"""
    BASE = "base"
    BEST = "best"
    WORST = "worst"
    CUSTOM = "custom"


@dataclass
class ModelAssumptions:
    """Financial model assumptions"""
    # Revenue assumptions
    revenue_growth_rate: float = 0.15  # 15% monthly growth
    revenue_start: float = 100000
    
    # Cost assumptions
    cogs_percent: float = 0.30  # 30% of revenue
    opex_fixed: float = 50000  # Fixed monthly operating expenses
    opex_variable_percent: float = 0.20  # 20% of revenue
    
    # Working capital
    days_receivables: int = 30
    days_payables: int = 45
    days_inventory: int = 0
    
    # Funding
    equity_raises: List[Dict] = None  # [{"month": 1, "amount": 1000000}]
    debt_raises: List[Dict] = None  # [{"month": 6, "amount": 500000, "rate": 0.08}]
    
    # Capital expenditure
    capex_schedule: List[Dict] = None  # [{"month": 9, "amount": 2000000, "description": "Equipment"}]
    
    # Tax
    tax_rate: float = 0.28
    
    # Other
    depreciation_rate: float = 0.10  # Annual depreciation rate
    starting_cash: float = 100000
    
    def __post_init__(self):
        if self.equity_raises is None:
            self.equity_raises = []
        if self.debt_raises is None:
            self.debt_raises = []
        if self.capex_schedule is None:
            self.capex_schedule = []


@dataclass
class MonthlyProjection:
    """Single month financial projection"""
    month: int
    date_start: str
    date_end: str
    fiscal_year: str
    
    # Income Statement
    revenue: float
    cogs: float
    gross_profit: float
    operating_expenses: float
    ebitda: float
    depreciation: float
    ebit: float
    interest_expense: float
    ebt: float
    tax: float
    net_income: float
    
    # Cash Flow
    opening_cash: float
    ebitda_cash: float
    working_capital_change: float
    equity_raised: float
    debt_raised: float
    interest_paid: float
    tax_paid: float
    capex: float
    closing_cash: float
    cash_flow_movement: float
    free_cash_flow: float
    
    # Metrics
    cash_runway_months: float
    burn_rate: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ProjectionEngine:
    """
    Generate detailed financial projections
    Similar to the provided cash flow template but with full P&L and metrics
    """
    
    def __init__(self):
        """Initialize projection engine"""
        logger.info("ProjectionEngine initialized")
    
    def generate_projections(
        self,
        assumptions: ModelAssumptions,
        months: int = 36,
        start_date: Optional[datetime] = None,
        scenario: ScenarioType = ScenarioType.BASE
    ) -> List[MonthlyProjection]:
        """
        Generate monthly financial projections
        
        Args:
            assumptions: Model assumptions
            months: Number of months to project
            start_date: Starting date (defaults to next month)
            scenario: Scenario type for adjustments
            
        Returns:
            List of monthly projections
        """
        if start_date is None:
            start_date = datetime.now().replace(day=1) + relativedelta(months=1)
        
        # Adjust assumptions for scenario
        assumptions = self._adjust_for_scenario(assumptions, scenario)
        
        projections = []
        current_cash = assumptions.starting_cash
        current_debt = 0
        cumulative_depreciation = 0
        
        for month_num in range(1, months + 1):
            month_start = start_date + relativedelta(months=month_num - 1)
            month_end = month_start + relativedelta(months=1, days=-1)
            fiscal_year = month_start.year if month_start.month >= 8 else month_start.year - 1
            
            # Calculate revenue (with growth)
            revenue = assumptions.revenue_start * ((1 + assumptions.revenue_growth_rate) ** (month_num - 1))
            
            # Calculate costs
            cogs = revenue * assumptions.cogs_percent
            gross_profit = revenue - cogs
            
            opex_variable = revenue * assumptions.opex_variable_percent
            operating_expenses = assumptions.opex_fixed + opex_variable
            
            ebitda = gross_profit - operating_expenses
            
            # Depreciation (simplified - based on cumulative capex)
            depreciation = cumulative_depreciation * (assumptions.depreciation_rate / 12) if month_num > 1 else 0
            
            ebit = ebitda - depreciation
            
            # Interest expense
            interest_expense = current_debt * (0.08 / 12) if current_debt > 0 else 0  # Assume 8% annual rate
            
            ebt = ebit - interest_expense
            
            # Tax (only on positive earnings)
            tax = max(0, ebt * assumptions.tax_rate)
            
            net_income = ebt - tax
            
            # Cash Flow
            opening_cash = current_cash
            
            # Working capital change (simplified)
            working_capital_change = 0  # TODO: Implement proper working capital calculation
            
            # Funding events
            equity_raised = sum(e["amount"] for e in assumptions.equity_raises if e["month"] == month_num)
            debt_raised = sum(d["amount"] for d in assumptions.debt_raises if d["month"] == month_num)
            
            if debt_raised > 0:
                current_debt += debt_raised
            
            # Interest and tax payments
            interest_paid = interest_expense
            tax_paid = tax
            
            # Cap expenditure
            capex = sum(c["amount"] for c in assumptions.capex_schedule if c["month"] == month_num)
            if capex > 0:
                cumulative_depreciation += capex
            
            # Calculate cash movements
            cash_from_operations = ebitda
            cash_from_financing = equity_raised + debt_raised
            cash_from_investing = -capex
            
            closing_cash = (
                opening_cash
                + cash_from_operations
                + working_capital_change
                + cash_from_financing
                - interest_paid
                - tax_paid
                + cash_from_investing
            )
            
            cash_flow_movement = closing_cash - opening_cash
            free_cash_flow = ebitda + working_capital_change - capex - interest_paid - tax_paid
            
            # Update current cash for next iteration
            current_cash = closing_cash
            
            # Calculate metrics
            burn_rate = -free_cash_flow if free_cash_flow < 0 else 0
            cash_runway_months = (closing_cash / burn_rate) if burn_rate > 0 else 999
            
            # Create projection
            projection = MonthlyProjection(
                month=month_num,
                date_start=month_start.strftime("%Y-%m-%d"),
                date_end=month_end.strftime("%Y-%m-%d"),
                fiscal_year=str(fiscal_year),
                revenue=revenue,
                cogs=cogs,
                gross_profit=gross_profit,
                operating_expenses=operating_expenses,
                ebitda=ebitda,
                depreciation=depreciation,
                ebit=ebit,
                interest_expense=interest_expense,
                ebt=ebt,
                tax=tax,
                net_income=net_income,
                opening_cash=opening_cash,
                ebitda_cash=ebitda,
                working_capital_change=working_capital_change,
                equity_raised=equity_raised,
                debt_raised=debt_raised,
                interest_paid=interest_paid,
                tax_paid=tax_paid,
                capex=capex,
                closing_cash=closing_cash,
                cash_flow_movement=cash_flow_movement,
                free_cash_flow=free_cash_flow,
                cash_runway_months=cash_runway_months,
                burn_rate=burn_rate
            )
            
            projections.append(projection)
        
        logger.info(f"Generated {len(projections)} month projections for {scenario.value} scenario")
        return projections
    
    def _adjust_for_scenario(
        self,
        assumptions: ModelAssumptions,
        scenario: ScenarioType
    ) -> ModelAssumptions:
        """
        Adjust assumptions based on scenario type
        
        Args:
            assumptions: Base assumptions
            scenario: Scenario type
            
        Returns:
            Adjusted assumptions
        """
        if scenario == ScenarioType.BASE:
            return assumptions
        
        # Create a copy
        adjusted = ModelAssumptions(
            revenue_growth_rate=assumptions.revenue_growth_rate,
            revenue_start=assumptions.revenue_start,
            cogs_percent=assumptions.cogs_percent,
            opex_fixed=assumptions.opex_fixed,
            opex_variable_percent=assumptions.opex_variable_percent,
            days_receivables=assumptions.days_receivables,
            days_payables=assumptions.days_payables,
            days_inventory=assumptions.days_inventory,
            equity_raises=assumptions.equity_raises.copy(),
            debt_raises=assumptions.debt_raises.copy(),
            capex_schedule=assumptions.capex_schedule.copy(),
            tax_rate=assumptions.tax_rate,
            depreciation_rate=assumptions.depreciation_rate,
            starting_cash=assumptions.starting_cash
        )
        
        if scenario == ScenarioType.BEST:
            # Best case: Higher growth, lower costs
            adjusted.revenue_growth_rate *= 1.5  # 50% higher growth
            adjusted.cogs_percent *= 0.9  # 10% better unit economics
            adjusted.opex_variable_percent *= 0.9  # 10% more efficient
        
        elif scenario == ScenarioType.WORST:
            # Worst case: Lower growth, higher costs
            adjusted.revenue_growth_rate *= 0.5  # 50% lower growth
            adjusted.cogs_percent *= 1.2  # 20% worse unit economics
            adjusted.opex_variable_percent *= 1.2  # 20% less efficient
            adjusted.opex_fixed *= 1.1  # 10% higher fixed costs
        
        return adjusted
    
    def export_to_dataframe(
        self,
        projections: List[MonthlyProjection]
    ) -> pd.DataFrame:
        """
        Convert projections to pandas DataFrame for easy export
        
        Args:
            projections: List of monthly projections
            
        Returns:
            DataFrame with all projection data
        """
        data = [p.to_dict() for p in projections]
        df = pd.DataFrame(data)
        return df
    
    def generate_scenario_comparison(
        self,
        assumptions: ModelAssumptions,
        months: int = 36
    ) -> Dict[str, List[MonthlyProjection]]:
        """
        Generate projections for all scenarios
        
        Args:
            assumptions: Base assumptions
            months: Number of months to project
            
        Returns:
            Dictionary with projections for each scenario
        """
        scenarios = {}
        
        for scenario_type in [ScenarioType.BEST, ScenarioType.BASE, ScenarioType.WORST]:
            projections = self.generate_projections(
                assumptions=assumptions,
                months=months,
                scenario=scenario_type
            )
            scenarios[scenario_type.value] = projections
        
        logger.info(f"Generated scenario comparison with {len(scenarios)} scenarios")
        return scenarios
    
    def calculate_key_metrics(
        self,
        projections: List[MonthlyProjection]
    ) -> Dict:
        """
        Calculate key financial metrics from projections
        
        Args:
            projections: List of monthly projections
            
        Returns:
            Dictionary of key metrics
        """
        if not projections:
            return {}
        
        # Extract data
        revenues = [p.revenue for p in projections]
        ebitdas = [p.ebitda for p in projections]
        cash_balances = [p.closing_cash for p in projections]
        
        # Calculate metrics
        metrics = {
            "total_revenue": sum(revenues),
            "avg_monthly_revenue": np.mean(revenues),
            "revenue_cagr": self._calculate_cagr(revenues[0], revenues[-1], len(revenues) / 12),
            "total_ebitda": sum(ebitdas),
            "avg_monthly_ebitda": np.mean(ebitdas),
            "months_to_profitability": self._months_to_profitability(ebitdas),
            "final_cash_balance": cash_balances[-1],
            "min_cash_balance": min(cash_balances),
            "months_cash_negative": sum(1 for cb in cash_balances if cb < 0),
            "total_equity_needed": sum(p.equity_raised for p in projections),
            "total_debt_raised": sum(p.debt_raised for p in projections),
            "total_capex": sum(p.capex for p in projections)
        }
        
        return metrics
    
    def _calculate_cagr(self, start_value: float, end_value: float, years: float) -> float:
        """Calculate Compound Annual Growth Rate"""
        if start_value <= 0 or years <= 0:
            return 0.0
        return (pow(end_value / start_value, 1 / years) - 1)
    
    def _months_to_profitability(self, ebitdas: List[float]) -> int:
        """Calculate months until first positive EBITDA"""
        for i, ebitda in enumerate(ebitdas, 1):
            if ebitda > 0:
                return i
        return -1  # Never profitable in projection period
