"""
Deal Qualification Engine - scores and qualifies investment opportunities.
"""
from typing import Dict, List, Optional, Any
from loguru import logger
from openai import AsyncOpenAI
import os


class DealQualifier:
    """
    Qualifies investment deals using AI-powered analysis.
    
    Scores deals based on:
    - Market opportunity
    - Team quality
    - Product/technology
    - Traction/metrics
    - Financial health
    - Strategic fit
    """
    
    def __init__(self):
        """Initialize the deal qualifier."""
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Scoring weights
        self.weights = {
            'market_opportunity': 0.25,
            'team': 0.20,
            'product': 0.20,
            'traction': 0.20,
            'financials': 0.10,
            'strategic_fit': 0.05
        }
    
    async def qualify_deal(self, deal: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Qualify a single deal and return comprehensive analysis.
        
        Args:
            deal: Deal dictionary with company information
            context: Additional context like investment thesis, target sectors
            
        Returns:
            {
                'score': 85.5,  # Overall score 0-100
                'recommendation': 'Strong Pass',  # Pass/Strong Pass/Review/Reject
                'scores': {
                    'market_opportunity': 90,
                    'team': 85,
                    'product': 80,
                    'traction': 85,
                    'financials': 75,
                    'strategic_fit': 95
                },
                'strengths': ['Strong market', 'Experienced team'],
                'concerns': ['Limited traction', 'High burn rate'],
                'analysis': 'Detailed analysis text...'
            }
        """
        try:
            # Extract key information
            company_name = deal.get('name', 'Unknown')
            description = deal.get('description', '')
            industry = deal.get('industry', '')
            stage = deal.get('stage', '')
            funding_amount = deal.get('funding_amount', 0)
            location = deal.get('location', '')
            
            logger.info(f"Qualifying deal: {company_name}")
            
            # Score each dimension
            scores = await self._score_dimensions(deal, context)
            
            # Calculate weighted overall score
            overall_score = sum(
                scores.get(dim, 0) * weight
                for dim, weight in self.weights.items()
            )
            
            # Generate recommendation
            recommendation = self._get_recommendation(overall_score, scores)
            
            # Extract strengths and concerns
            strengths, concerns = self._extract_insights(scores, deal)
            
            # Generate detailed analysis
            analysis = await self._generate_analysis(deal, scores, context)
            
            return {
                'score': round(overall_score, 1),
                'recommendation': recommendation,
                'scores': scores,
                'strengths': strengths,
                'concerns': concerns,
                'analysis': analysis,
                'qualified_at': deal.get('scraped_at', '')
            }
            
        except Exception as e:
            logger.error(f"Error qualifying deal {deal.get('name')}: {e}")
            return {
                'score': 0,
                'recommendation': 'Error',
                'error': str(e)
            }
    
    async def qualify_batch(
        self,
        deals: List[Dict[str, Any]],
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Qualify multiple deals in batch.
        
        Args:
            deals: List of deal dictionaries
            context: Shared context for all deals
            
        Returns:
            List of qualification results
        """
        import asyncio
        
        tasks = [self.qualify_deal(deal, context) for deal in deals]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        qualified_deals = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error qualifying deal {i}: {result}")
                qualified_deals.append({
                    'deal': deals[i],
                    'score': 0,
                    'recommendation': 'Error',
                    'error': str(result)
                })
            else:
                qualified_deals.append({
                    'deal': deals[i],
                    **result
                })
        
        return qualified_deals
    
    async def _score_dimensions(
        self,
        deal: Dict[str, Any],
        context: Optional[Dict]
    ) -> Dict[str, float]:
        """Score individual dimensions of the deal."""
        
        # Build prompt for LLM scoring
        prompt = self._build_scoring_prompt(deal, context)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert investment analyst scoring startup deals. "
                                 "Provide scores 0-100 for each dimension based on available information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            import json
            scores_text = response.choices[0].message.content
            scores = json.loads(scores_text)
            
            # Validate and normalize scores
            normalized_scores = {}
            for dim in self.weights.keys():
                score = scores.get(dim, 50)  # Default to 50 if missing
                normalized_scores[dim] = max(0, min(100, float(score)))
            
            return normalized_scores
            
        except Exception as e:
            logger.error(f"Error scoring dimensions: {e}")
            # Return default scores
            return {dim: 50.0 for dim in self.weights.keys()}
    
    def _build_scoring_prompt(self, deal: Dict[str, Any], context: Optional[Dict]) -> str:
        """Build prompt for LLM scoring."""
        
        prompt = f"""Score this investment opportunity across 6 dimensions (0-100):

**Company Information:**
- Name: {deal.get('name', 'Unknown')}
- Description: {deal.get('description', 'No description')}
- Industry: {deal.get('industry', 'Unknown')}
- Stage: {deal.get('stage', 'Unknown')}
- Location: {deal.get('location', 'Unknown')}
- Funding Amount: ${deal.get('funding_amount', 0):,.0f}
- Total Funding: ${deal.get('total_funding', 0):,.0f}
- Investors: {', '.join(deal.get('investors', [])[:5])}
- Employee Count: {deal.get('employee_count', 'Unknown')}
- Founded: {deal.get('founded_year', 'Unknown')}
- Website: {deal.get('website', 'Unknown')}
"""
        
        if context:
            prompt += f"\n**Investment Context:**\n"
            if 'target_industries' in context:
                prompt += f"- Target Industries: {', '.join(context['target_industries'])}\n"
            if 'target_stages' in context:
                prompt += f"- Target Stages: {', '.join(context['target_stages'])}\n"
            if 'geographic_focus' in context:
                prompt += f"- Geographic Focus: {', '.join(context['geographic_focus'])}\n"
        
        prompt += """
**Score the following dimensions (0-100):**

1. **market_opportunity**: Size, growth, competition, timing
2. **team**: Experience, track record, completeness, execution ability
3. **product**: Innovation, differentiation, scalability, technology
4. **traction**: Revenue, users, growth rate, unit economics
5. **financials**: Burn rate, runway, capital efficiency, path to profitability
6. **strategic_fit**: Alignment with our thesis, portfolio synergies

Return ONLY a JSON object with scores:
{
    "market_opportunity": 85,
    "team": 75,
    "product": 90,
    "traction": 70,
    "financials": 65,
    "strategic_fit": 80
}
"""
        
        return prompt
    
    def _get_recommendation(self, overall_score: float, scores: Dict[str, float]) -> str:
        """Determine recommendation based on scores."""
        
        # Check for red flags (any dimension below 30)
        min_score = min(scores.values())
        if min_score < 30:
            return "Reject"
        
        # Overall score thresholds
        if overall_score >= 80:
            return "Strong Pass"
        elif overall_score >= 65:
            return "Pass"
        elif overall_score >= 50:
            return "Review"
        else:
            return "Reject"
    
    def _extract_insights(
        self,
        scores: Dict[str, float],
        deal: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """Extract key strengths and concerns from scores."""
        
        strengths = []
        concerns = []
        
        # Dimension names in human-readable form
        dim_names = {
            'market_opportunity': 'Market Opportunity',
            'team': 'Team Quality',
            'product': 'Product/Technology',
            'traction': 'Traction',
            'financials': 'Financial Health',
            'strategic_fit': 'Strategic Fit'
        }
        
        # Identify strengths (score >= 75)
        for dim, score in scores.items():
            if score >= 75:
                strengths.append(f"Strong {dim_names[dim].lower()} (score: {score:.0f})")
        
        # Identify concerns (score < 60)
        for dim, score in scores.items():
            if score < 60:
                concerns.append(f"Limited {dim_names[dim].lower()} (score: {score:.0f})")
        
        # Add deal-specific insights
        if deal.get('funding_amount', 0) > 50_000_000:
            strengths.append(f"Significant funding raised (${deal['funding_amount']:,.0f})")
        
        if deal.get('investors'):
            notable_investors = ['sequoia', 'a16z', 'yc', 'accel', 'kleiner']
            investor_names = [inv.lower() for inv in deal.get('investors', [])]
            if any(notable in ' '.join(investor_names) for notable in notable_investors):
                strengths.append("Backed by top-tier investors")
        
        return strengths[:5], concerns[:5]  # Limit to top 5 each
    
    async def _generate_analysis(
        self,
        deal: Dict[str, Any],
        scores: Dict[str, float],
        context: Optional[Dict]
    ) -> str:
        """Generate detailed analysis narrative."""
        
        try:
            prompt = f"""Write a concise investment analysis (3-4 paragraphs) for this deal:

**Company:** {deal.get('name')}
**Description:** {deal.get('description')}
**Industry:** {deal.get('industry')}
**Stage:** {deal.get('stage')}
**Funding:** ${deal.get('funding_amount', 0):,.0f}

**Scores:**
- Market Opportunity: {scores.get('market_opportunity', 0):.0f}/100
- Team: {scores.get('team', 0):.0f}/100
- Product: {scores.get('product', 0):.0f}/100
- Traction: {scores.get('traction', 0):.0f}/100
- Financials: {scores.get('financials', 0):.0f}/100
- Strategic Fit: {scores.get('strategic_fit', 0):.0f}/100

Provide a balanced analysis covering:
1. Key strengths and opportunities
2. Main risks and concerns
3. Overall investment perspective
"""
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise investment analyst. Write clear, direct analyses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return "Analysis could not be generated."
    
    def filter_by_threshold(
        self,
        qualified_deals: List[Dict[str, Any]],
        min_score: float = 50.0,
        recommendations: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter qualified deals by minimum score and recommendations.
        
        Args:
            qualified_deals: List of deals with qualification results
            min_score: Minimum overall score (default: 50)
            recommendations: List of acceptable recommendations (e.g., ['Strong Pass', 'Pass'])
            
        Returns:
            Filtered list of deals
        """
        filtered = []
        
        for deal_result in qualified_deals:
            score = deal_result.get('score', 0)
            recommendation = deal_result.get('recommendation', '')
            
            # Check score threshold
            if score < min_score:
                continue
            
            # Check recommendation filter
            if recommendations and recommendation not in recommendations:
                continue
            
            filtered.append(deal_result)
        
        return filtered
