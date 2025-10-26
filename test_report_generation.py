"""
Test script for Feature 5: Investment Memo & Presentation Draft
Tests both memo and deck generation with various data combinations
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from services.report_generation import InvestmentMemoGenerator, PitchDeckGenerator
from loguru import logger


# Sample test data
SAMPLE_COMPANY_DATA = {
    "name": "AI Innovations Inc.",
    "description": "Advanced AI platform for enterprise automation and intelligence",
    "stage": "Series A",
    "industry": "Enterprise AI",
    "location": "San Francisco, CA",
    "founded": "2021",
    "website": "www.aiinnovations.com",
    "funding_amount": 5000000,
    "valuation": 20000000
}

SAMPLE_DEAL_DATA = {
    "qualification_score": 82,
    "strengths": [
        "Strong technical team with ML/AI expertise",
        "Clear product-market fit with growing customer base",
        "Defensible technology with patent applications",
        "Scalable business model with recurring revenue"
    ],
    "concerns": [
        "High customer acquisition costs",
        "Competitive market with established players",
        "Need for additional technical hires"
    ]
}

SAMPLE_MARKET_DATA = {
    "market_size": "$50B",
    "growth_rate": "25%",
    "trends": [
        "Increasing enterprise AI adoption",
        "Growing demand for automation solutions",
        "Shift toward intelligent decision-making systems"
    ],
    "competitors": [
        "DataRobot",
        "H2O.ai",
        "Databricks"
    ]
}

SAMPLE_FINANCIAL_MODEL = {
    "metrics": {
        "total_revenue_5y": 45000000,
        "revenue_cagr": 85,
        "months_to_profitability": 18,
        "projected_arr_y5": 50000000,
        "gross_margin": 75,
        "burn_rate": 500000
    },
    "projections": {
        "revenue": {
            "2024": 2000000,
            "2025": 5000000,
            "2026": 12000000,
            "2027": 24000000,
            "2028": 45000000
        },
        "expenses": {
            "2024": 3500000,
            "2025": 6000000,
            "2026": 10000000,
            "2027": 18000000,
            "2028": 30000000
        }
    }
}


async def test_memo_generation_full_data():
    """Test 1: Generate memo with all data"""
    logger.info("=" * 60)
    logger.info("TEST 1: Memo Generation with Full Data")
    logger.info("=" * 60)
    
    try:
        generator = InvestmentMemoGenerator()
        
        memo_bytes = await generator.generate_memo(
            company_data=SAMPLE_COMPANY_DATA,
            deal_data=SAMPLE_DEAL_DATA,
            market_data=SAMPLE_MARKET_DATA,
            financial_model=SAMPLE_FINANCIAL_MODEL,
            template_type="standard",
            analyst_name="John Doe",
            firm_name="Test Capital Partners"
        )
        
        # Save to file
        output_file = "test_outputs/full_data_memo.docx"
        os.makedirs("test_outputs", exist_ok=True)
        
        with open(output_file, "wb") as f:
            f.write(memo_bytes.getvalue())
        
        file_size = os.path.getsize(output_file)
        logger.success(f"✅ Test 1 PASSED: Generated memo with full data ({file_size:,} bytes)")
        logger.info(f"   Output: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 1 FAILED: {str(e)}")
        return False


async def test_memo_generation_minimal_data():
    """Test 2: Generate memo with minimal data"""
    logger.info("=" * 60)
    logger.info("TEST 2: Memo Generation with Minimal Data")
    logger.info("=" * 60)
    
    try:
        generator = InvestmentMemoGenerator()
        
        minimal_company = {
            "name": "Minimal Startup",
            "description": "A new startup in the tech space",
            "stage": "Seed",
            "industry": "Technology"
        }
        
        memo_bytes = await generator.generate_memo(
            company_data=minimal_company,
            deal_data=None,
            market_data=None,
            financial_model=None,
            template_type="standard",
            analyst_name="Jane Smith",
            firm_name="Venture Partners"
        )
        
        # Save to file
        output_file = "test_outputs/minimal_data_memo.docx"
        with open(output_file, "wb") as f:
            f.write(memo_bytes.getvalue())
        
        file_size = os.path.getsize(output_file)
        logger.success(f"✅ Test 2 PASSED: Generated memo with minimal data ({file_size:,} bytes)")
        logger.info(f"   Output: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 2 FAILED: {str(e)}")
        return False


async def test_deck_generation_full_data():
    """Test 3: Generate pitch deck with all data"""
    logger.info("=" * 60)
    logger.info("TEST 3: Pitch Deck Generation with Full Data")
    logger.info("=" * 60)
    
    try:
        generator = PitchDeckGenerator()
        
        deck_bytes = await generator.generate_deck(
            company_data=SAMPLE_COMPANY_DATA,
            deal_data=SAMPLE_DEAL_DATA,
            market_data=SAMPLE_MARKET_DATA,
            financial_model=SAMPLE_FINANCIAL_MODEL,
            template_type="standard"
        )
        
        # Save to file
        output_file = "test_outputs/full_data_deck.pptx"
        with open(output_file, "wb") as f:
            f.write(deck_bytes.getvalue())
        
        file_size = os.path.getsize(output_file)
        logger.success(f"✅ Test 3 PASSED: Generated deck with full data ({file_size:,} bytes)")
        logger.info(f"   Output: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 3 FAILED: {str(e)}")
        return False


async def test_deck_generation_minimal_data():
    """Test 4: Generate pitch deck with minimal data"""
    logger.info("=" * 60)
    logger.info("TEST 4: Pitch Deck Generation with Minimal Data")
    logger.info("=" * 60)
    
    try:
        generator = PitchDeckGenerator()
        
        minimal_company = {
            "name": "Quick Deck Startup",
            "description": "Fast-growing tech company",
            "stage": "Seed",
            "industry": "SaaS",
            "funding_amount": 1000000
        }
        
        deck_bytes = await generator.generate_deck(
            company_data=minimal_company,
            deal_data=None,
            market_data=None,
            financial_model=None,
            template_type="standard"
        )
        
        # Save to file
        output_file = "test_outputs/minimal_data_deck.pptx"
        with open(output_file, "wb") as f:
            f.write(deck_bytes.getvalue())
        
        file_size = os.path.getsize(output_file)
        logger.success(f"✅ Test 4 PASSED: Generated deck with minimal data ({file_size:,} bytes)")
        logger.info(f"   Output: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 4 FAILED: {str(e)}")
        return False


async def test_multiple_companies():
    """Test 5: Generate reports for multiple companies"""
    logger.info("=" * 60)
    logger.info("TEST 5: Multiple Companies Report Generation")
    logger.info("=" * 60)
    
    companies = [
        {
            "name": "HealthTech Solutions",
            "description": "Digital health platform for remote patient monitoring",
            "stage": "Series B",
            "industry": "HealthTech"
        },
        {
            "name": "FinanceAI Corp",
            "description": "AI-powered financial advisory platform",
            "stage": "Series A",
            "industry": "FinTech"
        },
        {
            "name": "EduLearn Platform",
            "description": "Online learning platform with adaptive AI",
            "stage": "Seed",
            "industry": "EdTech"
        }
    ]
    
    try:
        memo_generator = InvestmentMemoGenerator()
        deck_generator = PitchDeckGenerator()
        
        for i, company in enumerate(companies, 1):
            logger.info(f"Processing company {i}/3: {company['name']}")
            
            # Generate memo
            memo_bytes = await memo_generator.generate_memo(
                company_data=company,
                deal_data=None,
                market_data=None,
                financial_model=None,
                template_type="standard",
                analyst_name="Test Analyst",
                firm_name="Test Firm"
            )
            
            memo_file = f"test_outputs/multi_{company['name'].replace(' ', '_')}_memo.docx"
            with open(memo_file, "wb") as f:
                f.write(memo_bytes.getvalue())
            
            # Generate deck
            deck_bytes = await deck_generator.generate_deck(
                company_data=company,
                deal_data=None,
                market_data=None,
                financial_model=None,
                template_type="standard"
            )
            
            deck_file = f"test_outputs/multi_{company['name'].replace(' ', '_')}_deck.pptx"
            with open(deck_file, "wb") as f:
                f.write(deck_bytes.getvalue())
            
            logger.info(f"   ✓ Generated memo and deck for {company['name']}")
        
        logger.success(f"✅ Test 5 PASSED: Generated reports for {len(companies)} companies")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 5 FAILED: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests and generate summary"""
    logger.info("\n")
    logger.info("*" * 70)
    logger.info("FEATURE 5: INVESTMENT MEMO & PRESENTATION DRAFT - TEST SUITE")
    logger.info("*" * 70)
    logger.info("\n")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️  OPENAI_API_KEY not set - AI content generation may fail")
        logger.info("Set it with: export OPENAI_API_KEY='your-key-here'\n")
    
    results = []
    
    # Run all tests
    results.append(("Memo with Full Data", await test_memo_generation_full_data()))
    results.append(("Memo with Minimal Data", await test_memo_generation_minimal_data()))
    results.append(("Deck with Full Data", await test_deck_generation_full_data()))
    results.append(("Deck with Minimal Data", await test_deck_generation_minimal_data()))
    results.append(("Multiple Companies", await test_multiple_companies()))
    
    # Summary
    logger.info("\n")
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 70)
    logger.info(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.success("\n🎉 ALL TESTS PASSED! Feature 5 is working correctly.\n")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.\n")
    
    logger.info("📁 Output files saved to: test_outputs/")
    logger.info("   • Open .docx files in Microsoft Word or Google Docs")
    logger.info("   • Open .pptx files in Microsoft PowerPoint or Google Slides")
    logger.info("\n")
    
    return passed == total


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
