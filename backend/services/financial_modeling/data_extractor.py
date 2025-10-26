"""
Financial Data Extractor
Extracts historical financial data from uploaded documents
Integrates with Feature 2 (Document Analysis)
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import re
from loguru import logger
from openai import AsyncOpenAI
import os
from pathlib import Path


class FinancialDataExtractor:
    """
    Extract financial data from various document formats
    Uses LLM to parse unstructured financial statements
    """
    
    def __init__(self):
        """Initialize extractor"""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("FinancialDataExtractor initialized")
    
    async def extract_from_document(
        self,
        file_path: str,
        document_type: str = "financial_statement"
    ) -> Dict:
        """
        Extract financial data from uploaded document
        
        Args:
            file_path: Path to the document
            document_type: Type of financial document
            
        Returns:
            Structured financial data
        """
        logger.info(f"Extracting financial data from {file_path}")
        
        # Read document content
        content = await self._read_document(file_path)
        
        # Use LLM to extract structured data
        financial_data = await self._extract_with_llm(content, document_type)
        
        return financial_data
    
    async def _read_document(self, file_path: str) -> str:
        """Read document content"""
        path = Path(file_path)
        
        if path.suffix == '.csv':
            df = pd.read_csv(file_path)
            return df.to_string()
        elif path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return df.to_string()
        elif path.suffix == '.txt':
            with open(file_path, 'r') as f:
                return f.read()
        else:
            # For PDFs and other formats, would use PyPDF2 or pdfplumber
            logger.warning(f"Unsupported file type: {path.suffix}")
            return ""
    
    async def _extract_with_llm(
        self,
        content: str,
        document_type: str
    ) -> Dict:
        """
        Use LLM to extract structured financial data
        
        Args:
            content: Document content
            document_type: Type of document
            
        Returns:
            Structured financial data
        """
        prompt = f"""
        Extract financial data from the following {document_type}. 
        
        Please extract:
        1. Revenue (historical periods with amounts)
        2. Cost of Goods Sold (COGS)
        3. Operating Expenses (OpEx)
        4. EBITDA
        5. Cash balances
        6. Any equity raises or debt financing
        7. Capital expenditures
        8. Key dates and periods
        
        Document content:
        {content[:4000]}  # Truncate to avoid token limits
        
        Return the data in JSON format with clear structure.
        If any values are missing, use null.
        Include currency if mentioned.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial analyst extracting structured data from documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse LLM response
            extracted_text = response.choices[0].message.content
            
            # Try to parse as JSON
            import json
            try:
                financial_data = json.loads(extracted_text)
            except:
                # If not valid JSON, create structured response
                financial_data = {
                    "extracted_text": extracted_text,
                    "status": "partial_extraction"
                }
            
            logger.info("Successfully extracted financial data with LLM")
            return financial_data
            
        except Exception as e:
            logger.error(f"Error extracting with LLM: {str(e)}")
            return {
                "error": str(e),
                "status": "extraction_failed"
            }
    
    def parse_csv_financial_model(self, file_path: str) -> Dict:
        """
        Parse financial model from CSV (like the provided template)
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Parsed financial data
        """
        logger.info(f"Parsing CSV financial model: {file_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(file_path, header=None)
            
            # Find key sections
            cash_flow_data = {}
            
            # Look for specific rows
            for idx, row in df.iterrows():
                if pd.notna(row[0]):
                    label = str(row[0]).strip()
                    
                    # Extract opening balance
                    if "Opening bank balance" in label or "opening" in label.lower():
                        values = [float(str(v).replace('$', '').replace(',', '').replace(' ', '')) 
                                 for v in row[4:] if pd.notna(v) and str(v).strip() != '']
                        cash_flow_data['opening_balance'] = values
                    
                    # Extract EBITDA
                    elif "EBITDA" in label:
                        values = [float(str(v).replace('$', '').replace(',', '').replace(' ', '').replace('(', '-').replace(')', '')) 
                                 for v in row[4:] if pd.notna(v) and str(v).strip() != '']
                        cash_flow_data['ebitda'] = values
                    
                    # Extract equity raises
                    elif "Equity raise" in label or "equity" in label.lower():
                        values = [float(str(v).replace('$', '').replace(',', '').replace(' ', '')) if pd.notna(v) and str(v).strip() != '' and str(v).replace('$', '').replace(',', '').replace(' ', '').strip() != '-' else 0
                                 for v in row[4:]]
                        cash_flow_data['equity_raises'] = values
                    
                    # Extract capex
                    elif "Capital expenditure" in label or "capex" in label.lower():
                        values = [float(str(v).replace('$', '').replace(',', '').replace(' ', '').replace('(', '-').replace(')', '')) if pd.notna(v) and str(v).strip() != '' else 0
                                 for v in row[4:]]
                        cash_flow_data['capex'] = values
            
            logger.info(f"Parsed {len(cash_flow_data)} data series from CSV")
            return cash_flow_data
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            return {"error": str(e)}
    
    def infer_assumptions_from_historical(
        self,
        historical_data: Dict
    ) -> Dict:
        """
        Infer model assumptions from historical data
        
        Args:
            historical_data: Historical financial data
            
        Returns:
            Inferred assumptions
        """
        assumptions = {}
        
        # Calculate average growth rate if revenue data available
        if 'revenue' in historical_data and len(historical_data['revenue']) > 1:
            revenues = historical_data['revenue']
            growth_rates = [(revenues[i] - revenues[i-1]) / revenues[i-1] 
                           for i in range(1, len(revenues)) if revenues[i-1] != 0]
            assumptions['revenue_growth_rate'] = sum(growth_rates) / len(growth_rates) if growth_rates else 0.1
        
        # Calculate average margins
        if 'revenue' in historical_data and 'cogs' in historical_data:
            revenues = historical_data['revenue']
            cogs = historical_data['cogs']
            margins = [(revenues[i] - cogs[i]) / revenues[i] 
                      for i in range(len(revenues)) if revenues[i] != 0]
            assumptions['gross_margin'] = sum(margins) / len(margins) if margins else 0.7
        
        logger.info(f"Inferred {len(assumptions)} assumptions from historical data")
        return assumptions
