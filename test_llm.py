#!/usr/bin/env python
"""
Quick test script for LLM integration
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.llm_agents import InvestmentAnalystAgent

async def test_llm():
    """Test LLM analysis"""
    
    # Create agent
    agent = InvestmentAnalystAgent()
    
    # Test with a document
    filename = "20251024_193640_1e3a0c1e-82a8-4c68-b5b6-770a3799a9fe_Baladna Financial Documents.pdf"
    
    print("🔍 Testing LLM Agent")
    print(f"📄 Analyzing: {filename}")
    print("-" * 80)
    
    try:
        result = await agent.analyze_document(filename)
        
        print("\n✅ Analysis Complete!")
        print("\n" + "=" * 80)
        print("RESULTS:")
        print("=" * 80)
        
        # Print structured analysis
        print("\n📊 PRE-PROCESSING (Keyword-based):")
        structured = result.get("structured_analysis", {})
        print(f"  Red Flags Found: {structured.get('red_flags_count', 0)}")
        print(f"  Positive Signals: {structured.get('positive_signals_count', 0)}")
        print(f"  Preliminary Recommendation: {structured.get('preliminary_recommendation', {}).get('action', 'N/A')}")
        
        # Print LLM analysis
        llm = result.get("llm_analysis", {})
        print("\n🤖 LLM ANALYSIS:")
        print(f"  Status: {llm.get('status', 'unknown')}")
        
        if llm.get('status') == 'success':
            risk = llm.get('risk_assessment', {})
            print(f"\n  Risk Score: {risk.get('score', 0)}/10")
            print(f"  Risk Analysis: {risk.get('analysis', 'N/A')[:200]}...")
            
            rec = llm.get('recommendation', {})
            print(f"\n  Recommendation: {rec.get('action', 'N/A')}")
            print(f"  Confidence: {rec.get('confidence', 0)}%")
            print(f"  Reasoning: {rec.get('reasoning', 'N/A')[:200]}...")
        else:
            print(f"  Message: {llm.get('message', 'No message')}")
        
        # Print combined recommendation
        combined = result.get("combined_recommendation", {})
        print("\n🎯 COMBINED RECOMMENDATION:")
        print(f"  Action: {combined.get('action', 'N/A')}")
        print(f"  Confidence: {combined.get('confidence', 0)}%")
        print(f"  Structured Score: {combined.get('structured_score', 0)}%")
        
    except FileNotFoundError:
        print(f"\n❌ Error: Document not found")
        print("   Please upload a document first via the UI")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_llm())
