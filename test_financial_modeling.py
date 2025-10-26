#!/usr/bin/env python3
"""
Test script for Feature 4: Financial Modeling & Scenario Planning
Tests the complete workflow from API calls to Excel export
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

def test_generate_model():
    """Test generating a financial projection model"""
    print("\n" + "="*60)
    print("TEST 1: Generate Financial Projection Model")
    print("="*60)
    
    assumptions = {
        "revenue_start": 100000,
        "revenue_growth_rate": 0.15,
        "cogs_percent": 0.30,
        "opex_fixed": 50000,
        "opex_variable_percent": 0.20,
        "starting_cash": 100000,
        "equity_raises": [
            {"month": 6, "amount": 500000}
        ],
        "capex_schedule": [
            {"month": 3, "amount": 100000}
        ],
        "tax_rate": 0.28,
        "debt_raises": [],
        "days_receivables": 30,
        "days_payables": 45,
        "days_inventory": 0,
        "depreciation_rate": 0.10
    }
    
    response = requests.post(
        f"{API_BASE_URL}/modeling/generate",
        json={
            "assumptions": assumptions,
            "months": 36
        }
    )
    
    if response.ok:
        result = response.json()
        model = result.get("model", {})
        projections = model.get("projections", [])
        metrics = model.get("metrics", {})
        
        print(f"✅ Model generated successfully!")
        print(f"\nKey Metrics:")
        print(f"  - Total Revenue: ${metrics.get('total_revenue', 0):,.0f}")
        print(f"  - Revenue CAGR: {metrics.get('revenue_cagr', 0)*100:.1f}%")
        print(f"  - Months to Profitability: {metrics.get('months_to_profitability', 'N/A')}")
        print(f"  - Final Cash Balance: ${metrics.get('final_cash_balance', 0):,.0f}")
        print(f"  - Min Cash Balance: ${metrics.get('min_cash_balance', 0):,.0f}")
        
        print(f"\nFirst 3 Months:")
        for i in range(min(3, len(projections))):
            p = projections[i]
            print(f"  Month {p['month']}: Revenue=${p['revenue']:,.0f}, EBITDA=${p['ebitda']:,.0f}, Cash=${p['closing_cash']:,.0f}")
        
        return model
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_scenario_analysis(base_assumptions):
    """Test running scenario analysis"""
    print("\n" + "="*60)
    print("TEST 2: Run Scenario Analysis")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/modeling/scenario",
        json={
            "assumptions": base_assumptions,
            "months": 36,
            "scenarios": ["base", "best", "worst"]
        }
    )
    
    if response.ok:
        result = response.json()
        comparison = result.get("comparison", {})
        
        print(f"✅ Scenario analysis complete!")
        print(f"\nScenario Comparison:")
        
        for scenario, metrics in comparison.items():
            print(f"\n  {scenario.upper()} Case:")
            print(f"    - Total Revenue: ${metrics.get('total_revenue', 0):,.0f}")
            print(f"    - Final Cash: ${metrics.get('final_cash', 0):,.0f}")
            print(f"    - Months to Profit: {metrics.get('months_to_profitability', 'N/A')}")
        
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_get_templates():
    """Test getting available templates"""
    print("\n" + "="*60)
    print("TEST 3: Get Available Templates")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/modeling/templates")
    
    if response.ok:
        result = response.json()
        templates = result.get("templates", [])
        
        print(f"✅ Found {len(templates)} templates:")
        for template in templates:
            print(f"\n  {template['name']}")
            print(f"    {template['description']}")
            print(f"    Fields: {', '.join(template['fields'])}")
        
        return templates
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_export_model(model_data):
    """Test exporting model to Excel"""
    print("\n" + "="*60)
    print("TEST 4: Export Model to Excel")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/modeling/export",
        json={
            "projections_data": model_data,
            "format": "excel",
            "file_name": "test_financial_model"
        }
    )
    
    if response.ok:
        # Save file
        filename = f"test_financial_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Model exported successfully!")
        print(f"   File saved as: {filename}")
        print(f"   File size: {len(response.content):,} bytes")
        
        return filename
    else:
        print(f"❌ Error: {response.text}")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Feature 4: Financial Modeling & Scenario Planning")
    print("End-to-End API Test Suite")
    print("="*60)
    
    # Test 1: Generate model
    model = test_generate_model()
    
    if not model:
        print("\n❌ Model generation failed. Stopping tests.")
        return
    
    # Test 2: Scenario analysis
    test_scenario_analysis(model.get("assumptions", {}))
    
    # Test 3: Get templates
    test_get_templates()
    
    # Test 4: Export
    test_export_model(model)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Test the frontend UI in Streamlit")
    print("2. Try uploading a financial document and extracting data")
    print("3. Generate projections from imported data")
    print("4. Compare scenarios in the UI")
    print("5. Export and verify Excel format matches template")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
