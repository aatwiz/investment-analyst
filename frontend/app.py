"""
Streamlit Frontend for Investment Analyst AI Agent
Main application dashboard
"""
import streamlit as st
import requests
from pathlib import Path
import os
from datetime import datetime
from typing import List, Optional

# Page configuration
st.set_page_config(
    page_title="Investment Analyst AI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        background: transparent;
        transition: all 0.3s ease;
    }
    .upload-section:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.03);
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    .feature-card h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .feature-card p {
        color: #333333;
        margin: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_files(files: List, category: Optional[str] = None):
    """Upload files to backend"""
    try:
        files_data = []
        for file in files:
            files_data.append(("files", (file.name, file, file.type)))
        
        data = {}
        if category:
            data["category"] = category
        
        response = requests.post(
            f"{API_BASE_URL}/files/upload/batch",
            files=files_data,
            data=data
        )
        
        return response.json()
    except Exception as e:
        st.error(f"Error uploading files: {str(e)}")
        return None


def get_uploaded_files(category: Optional[str] = None):
    """Get list of uploaded files"""
    try:
        params = {"category": category} if category else {}
        response = requests.get(f"{API_BASE_URL}/files/list", params=params)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching files: {str(e)}")
        return None


def delete_file(filename: str):
    """Delete a file"""
    try:
        response = requests.delete(f"{API_BASE_URL}/files/delete/{filename}")
        return response.json()
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return None


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Investment Analyst AI Agent</h1>', unsafe_allow_html=True)
    
    # Check backend health
    backend_status = check_backend_health()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/investment-portfolio.png", width=100)
        st.title("Navigation")
        
        page = st.radio(
            "Go to",
            ["🏠 Home", "� Deal Sourcing", "🌐 Market Intelligence", "�📤 Upload Documents", "📁 Document Library", "📊 Analysis", "💰 Financial Modeling", "📝 Generate Reports"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Status indicator
        if backend_status:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Offline")
            st.info("Start backend: `uvicorn backend.main:app --reload`")
        
        st.divider()
        
        # Quick stats
        st.subheader("Quick Stats")
        try:
            files_data = get_uploaded_files()
            if files_data:
                st.metric("📄 Total Documents", files_data.get("count", 0))
            else:
                st.metric("📄 Total Documents", 0)
        except:
            st.metric("📄 Total Documents", "N/A")
    
    # Main content based on selected page
    if page == "🏠 Home":
        show_home_page()
    elif page == "� Deal Sourcing":
        show_deal_sourcing_page()
    elif page == "🌐 Market Intelligence":
        show_market_intelligence_page()
    elif page == "�📤 Upload Documents":
        show_upload_page()
    elif page == "📁 Document Library":
        show_library_page()
    elif page == "📊 Analysis":
        show_analysis_page()
    elif page == "💰 Financial Modeling":
        show_modeling_page()
    elif page == "📝 Generate Reports":
        show_reports_page()


def show_home_page():
    """Home page with overview"""
    
    st.write("### 🎯 Welcome to Your AI-Powered Investment Analysis Platform")
    st.write("Accelerate due diligence, financial modeling, and investment memo drafting with AI.")
    
    # Feature overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Document Analysis</h3>
            <p>Upload and analyze legal, financial, and market documents automatically.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>💡 AI Insights</h3>
            <p>Extract key insights, identify red flags, and get comprehensive summaries.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Financial Modeling</h3>
            <p>Generate projections, run scenarios, and create professional reports.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick start guide
    st.write("### 🚀 Quick Start Guide")
    
    with st.expander("1️⃣ Upload Documents", expanded=True):
        st.write("""
        - Navigate to **Upload Documents** page
        - Choose document category (Financial, Legal, Market, etc.)
        - Upload PDF, DOCX, XLSX, PPT, and more
        - Supports batch upload for multiple files
        """)
    
    with st.expander("2️⃣ Analyze Documents"):
        st.write("""
        - Go to **Analysis** page
        - Select documents to analyze
        - Choose analysis type (Summary, Key Points, Red Flags)
        - Get AI-powered insights instantly
        """)
    
    with st.expander("3️⃣ Build Financial Models"):
        st.write("""
        - Visit **Financial Modeling** page
        - Upload or import financial data
        - Generate projections and forecasts
        - Run what-if scenario analyses
        """)
    
    with st.expander("4️⃣ Generate Reports"):
        st.write("""
        - Navigate to **Generate Reports**
        - Select analyzed documents
        - Choose report type (Memo, Pitch Deck, Summary)
        - Auto-generate professional investment materials
        """)
    
    st.divider()
    
    # MVP Features
    st.write("### 🧩 MVP Features")
    
    features = [
        {"icon": "🔍", "title": "AI-Powered Deal Sourcing", "status": "✅ Live"},
        {"icon": "📄", "title": "Automated DD Document Analysis", "status": "Phase 2"},
        {"icon": "🌐", "title": "Market & Competitive Analysis", "status": "Phase 3"},
        {"icon": "📊", "title": "Financial Modeling & Scenarios", "status": "Phase 4"},
        {"icon": "📝", "title": "Investment Memo & Presentation", "status": "Phase 5"},
    ]
    
    for feature in features:
        col1, col2, col3 = st.columns([1, 6, 2])
        with col1:
            st.write(f"## {feature['icon']}")
        with col2:
            st.write(f"**{feature['title']}**")
        with col3:
            if feature['status'] == "✅ Live":
                st.success(feature['status'])
            elif feature['status'] == "Phase 1":
                st.success(feature['status'])
            else:
                st.info(feature['status'])


def show_deal_sourcing_page():
    """Deal sourcing page - Feature 1"""
    
    st.write("### 🔍 AI-Powered Deal Sourcing")
    st.write("Automatically discover and qualify investment opportunities from multiple platforms")
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔎 Scrape Deals", "📋 Deal Pipeline", "🎯 Qualified Deals", "📊 Statistics", "📄 Daily Report"])
    
    with tab1:
        show_scrape_deals_tab()
    
    with tab2:
        show_deal_pipeline_tab()
    
    with tab3:
        show_qualified_deals_tab()
    
    with tab4:
        show_deal_stats_tab()
    
    with tab5:
        show_daily_report_tab()


def show_scrape_deals_tab():
    """Tab for scraping new deals"""
    
    st.write("#### Configure Deal Scraping")
    
    # Platform selection
    st.write("**Data Source:**")
    
    st.info("🚀 **TechCrunch** - Real funding announcements from curated tech journalism. Includes 8 major deals totaling $6.8B (Anthropic, Scale AI, Ramp, Perplexity AI, Brex, Vercel, Runway, Harvey)")
    
    techcrunch = st.checkbox("TechCrunch (automatically selected)", value=True, disabled=True, help="Real funding data - currently the only source")
    
    # Collect selected platforms
    platforms = ["techcrunch"]  # Always use TechCrunch
    
    st.divider()
    
    # Filters
    st.write("**Filters (Optional):**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        industries = st.multiselect(
            "Industries",
            ["Fintech", "HealthTech", "E-commerce", "SaaS", "AI/ML", "EdTech", "CleanTech", "AgriTech"],
            help="Filter by industry sectors"
        )
        
        locations = st.multiselect(
            "Locations",
            ["UAE", "Saudi Arabia", "Egypt", "United States", "United Kingdom", "Singapore"],
            help="Filter by geographic location"
        )
    
    with col2:
        stages = st.multiselect(
            "Funding Stages",
            ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Series D+"],
            help="Filter by funding stage"
        )
        
        min_funding = st.number_input(
            "Minimum Funding ($)",
            min_value=0,
            value=500000,
            step=100000,
            help="Minimum funding amount in USD"
        )
    
    st.divider()
    
    # Qualification settings
    st.write("**AI Qualification:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        qualify_deals = st.checkbox("Qualify deals with AI", value=True, help="Use GPT-4o-mini to score deals")
    
    with col2:
        if qualify_deals:
            min_score = st.slider("Minimum Score", 0, 100, 60, help="Only show deals above this score")
        else:
            min_score = 0
    
    st.divider()
    
    # Scrape button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("🚀 Start Scraping", type="primary", use_container_width=True, disabled=len(platforms) == 0):
            if not platforms:
                st.error("Please select at least one platform")
            else:
                scrape_deals(platforms, industries, locations, stages, min_funding, qualify_deals, min_score)


def scrape_deals(platforms, industries, locations, stages, min_funding, qualify, min_score):
    """Execute deal scraping"""
    
    with st.spinner(f"Scraping deals from {len(platforms)} platform(s)..."):
        try:
            # Build request payload
            payload = {
                "platforms": platforms,
                "qualify": qualify,
                "min_score": min_score
            }
            
            # Add filters if provided
            filters = {}
            if industries:
                filters["industries"] = [i.lower() for i in industries]
            if locations:
                filters["locations"] = locations
            if stages:
                filters["stages"] = [s.replace("-", " ").title() for s in stages]
            if min_funding > 0:
                filters["min_funding"] = min_funding
            
            if filters:
                payload["filters"] = filters
            
            # Make API call
            response = requests.post(
                f"{API_BASE_URL}/companies/scrape",
                json=payload,
                timeout=180  # 3 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    st.success("✅ Scraping completed successfully!")
                    
                    # Display summary
                    summary = result.get("summary", {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Scraped", summary.get("total_scraped", 0))
                    with col2:
                        st.metric("Unique Companies", summary.get("unique_companies", 0))
                    with col3:
                        st.metric("Qualified Deals", summary.get("qualified_deals", 0))
                    with col4:
                        total_funding = summary.get("total_funding", 0)
                        if total_funding >= 1_000_000_000:
                            st.metric("Total Funding", f"${total_funding/1_000_000_000:.1f}B")
                        else:
                            st.metric("Total Funding", f"${total_funding/1_000_000:.1f}M")
                    
                    # Top deals
                    deals = result.get("deals", [])
                    if deals:
                        st.write("### 🏆 Top Deals")
                        display_deals_table(deals[:10])
                    
                    # Platform breakdown
                    if summary.get("platforms"):
                        with st.expander("📊 Platform Breakdown"):
                            for platform, count in summary["platforms"].items():
                                st.write(f"- **{platform}**: {count} deals")
                    
                    # Top industries
                    if summary.get("top_industries"):
                        with st.expander("🏭 Top Industries"):
                            for industry, count in list(summary["top_industries"].items())[:10]:
                                st.write(f"- **{industry}**: {count} deals")
                
                else:
                    st.error(f"Scraping failed: {result.get('message', 'Unknown error')}")
            
            else:
                st.error(f"API Error: {response.status_code}")
                st.write(response.text)
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. This can happen with large scraping jobs. Try reducing the number of platforms or adding more specific filters.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_deal_pipeline_tab():
    """Tab for viewing all deals"""
    
    st.write("#### All Deals Pipeline")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        platform_filter = st.selectbox(
            "Platform",
            ["All", "Crunchbase", "AngelList", "Bloomberg", "Magnitt", "Wamda", "PitchBook"]
        )
    
    with col2:
        industry_filter = st.text_input("Industry", placeholder="e.g. fintech")
    
    with col3:
        min_funding_filter = st.number_input("Min Funding ($M)", min_value=0.0, value=0.0, step=0.5)
    
    with col4:
        limit = st.selectbox("Results per page", [20, 50, 100], index=1)
    
    # Fetch button
    if st.button("🔍 Fetch Deals", use_container_width=True):
        fetch_deals(platform_filter, industry_filter, min_funding_filter, limit)


def fetch_deals(platform, industry, min_funding, limit):
    """Fetch deals from API"""
    
    with st.spinner("Fetching deals..."):
        try:
            params = {"limit": limit, "offset": 0}
            
            if platform != "All":
                params["platforms"] = platform.lower()
            if industry:
                params["industries"] = industry.lower()
            if min_funding > 0:
                params["min_funding"] = int(min_funding * 1_000_000)
            
            response = requests.get(
                f"{API_BASE_URL}/companies/deals",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    deals = result.get("deals", [])
                    count = result.get("count", 0)
                    
                    if deals:
                        st.success(f"Found {count} deals")
                        display_deals_table(deals)
                    else:
                        st.info("📭 No deals found matching your criteria. Try scraping first!")
                else:
                    st.warning(result.get("message", "No deals available yet"))
            else:
                st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_qualified_deals_tab():
    """Tab for qualified deals only"""
    
    st.write("#### AI-Qualified Investment Opportunities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("Minimum Score", 0, 100, 70)
    
    with col2:
        recommendations = st.multiselect(
            "Recommendations",
            ["Strong Pass", "Pass", "Review"],
            default=["Strong Pass", "Pass"]
        )
    
    with col3:
        limit = st.selectbox("Results", [10, 20, 50], index=1)
    
    if st.button("🎯 Show Qualified Deals", use_container_width=True):
        fetch_qualified_deals(min_score, recommendations, limit)


def fetch_qualified_deals(min_score, recommendations, limit):
    """Fetch qualified deals"""
    
    with st.spinner("Fetching qualified deals..."):
        try:
            params = {
                "min_score": min_score,
                "limit": limit,
                "offset": 0
            }
            
            if recommendations:
                params["recommendations"] = ",".join(recommendations)
            
            response = requests.get(
                f"{API_BASE_URL}/companies/deals",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    deals = result.get("deals", [])
                    
                    if deals:
                        st.success(f"Found {len(deals)} qualified deals")
                        display_qualified_deals_table(deals)
                    else:
                        st.info("📭 No qualified deals found. Run scraping with AI qualification enabled!")
                else:
                    st.warning(result.get("message"))
            else:
                st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_deal_stats_tab():
    """Tab for statistics"""
    
    st.write("#### Pipeline Statistics")
    
    if st.button("📊 Refresh Stats", use_container_width=True):
        fetch_deal_stats()


def show_daily_report_tab():
    """Tab for generating daily potential deals reports"""
    
    st.write("#### 📄 Daily Potential Deals Report")
    st.write("Generate a comprehensive report of investment opportunities matching your criteria")
    
    st.write("")
    
    # Criteria Form
    with st.form("report_criteria_form"):
        st.write("**Report Criteria:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sectors
            sectors = st.multiselect(
                "Target Sectors",
                ["Fintech", "ClimateTech", "Enterprise SaaS", "AI & Machine Learning", 
                 "Healthcare", "AgriTech", "Cybersecurity", "E-commerce", "EdTech", "PropTech"],
                default=["Fintech", "ClimateTech", "Enterprise SaaS"],
                help="Industries to focus on"
            )
            
            # Stages
            stages = st.multiselect(
                "Investment Stages",
                ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth"],
                default=["Seed", "Series A", "Series B"],
                help="Funding stages to include"
            )
            
            # Revenue Range
            st.write("**Revenue Range:**")
            rev_col1, rev_col2 = st.columns(2)
            with rev_col1:
                min_revenue = st.number_input(
                    "Min Revenue ($)",
                    min_value=0,
                    value=500_000,
                    step=100_000,
                    format="%d"
                )
            with rev_col2:
                max_revenue = st.number_input(
                    "Max Revenue ($)",
                    min_value=0,
                    value=10_000_000,
                    step=1_000_000,
                    format="%d"
                )
        
        with col2:
            # Geographies
            geographies = st.multiselect(
                "Target Geographies",
                ["North America", "Europe", "Asia", "Latin America", "Middle East", "Africa"],
                default=["North America", "Europe"],
                help="Geographic regions to focus on"
            )
            
            # Max Deals
            max_deals = st.slider(
                "Maximum Deals",
                min_value=5,
                max_value=50,
                value=20,
                help="Maximum number of deals to include in report"
            )
            
            # Days Back
            days_back = st.slider(
                "Look Back Period (days)",
                min_value=7,
                max_value=90,
                value=30,
                help="How far back to look for deals"
            )
        
        # Generate button
        submitted = st.form_submit_button("🔍 Generate Report", type="primary", use_container_width=True)
    
    if submitted:
        if not sectors or not stages:
            st.error("⚠️ Please select at least one sector and one stage")
            return
        
        # Store criteria in session state
        st.session_state.report_criteria = {
            "sectors": sectors,
            "stages": stages,
            "min_revenue": min_revenue,
            "max_revenue": max_revenue,
            "geographies": geographies,
            "max_deals": max_deals,
            "days_back": days_back
        }
        
        # Generate report
        generate_daily_report(st.session_state.report_criteria)
    
    # Show previous report if exists
    if hasattr(st.session_state, 'last_report') and st.session_state.last_report:
        st.write("---")
        display_daily_report(st.session_state.last_report)


def generate_daily_report(criteria):
    """Generate daily deals report"""
    
    with st.spinner("🔎 Discovering investment opportunities..."):
        try:
            # Call discover API
            response = requests.post(
                f"{API_BASE_URL}/companies/discover",
                json=criteria,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    st.session_state.last_report = result
                    st.success(f"✅ Found {result['deal_count']} deals matching your criteria!")
                    st.rerun()  # Force refresh to show the report
                else:
                    st.error("Failed to generate report")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        
        except requests.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def display_daily_report(report_data):
    """Display the generated report"""
    
    deals = report_data.get("deals", [])
    criteria = report_data.get("criteria", {})
    
    # Header
    st.write("### 📊 Generated Report")
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Deals", report_data.get("deal_count", 0))
    with col2:
        sectors_str = ", ".join(criteria.get("sectors", [])[:3])
        if len(criteria.get("sectors", [])) > 3:
            sectors_str += f" +{len(criteria['sectors'])-3}"
        st.metric("Sectors", sectors_str)
    with col3:
        stages_str = ", ".join(criteria.get("stages", [])[:2])
        if len(criteria.get("stages", [])) > 2:
            stages_str += f" +{len(criteria['stages'])-2}"
        st.metric("Stages", stages_str)
    
    # Export buttons
    st.write("")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("📥 Export DOCX", use_container_width=True):
            download_report("docx", criteria)
    
    with col2:
        if st.button("📥 Export HTML", use_container_width=True):
            download_report("html", criteria)
    
    with col3:
        if st.button("📥 Export TXT", use_container_width=True):
            download_report("text", criteria)
    
    st.write("---")
    
    # Deal cards
    if not deals:
        st.info("No deals found matching criteria")
        return
    
    for i, deal in enumerate(deals, 1):
        with st.expander(f"🔍 {i}. {deal['company_name']} - {deal['stage']}", expanded=(i <= 3)):
            # Header info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Sector:** {deal['sector']}")
                st.write(f"**Stage:** {deal['stage']}")
            
            with col2:
                if deal.get('funding_amount'):
                    funding = deal['funding_amount']
                    if funding >= 1_000_000_000:
                        st.write(f"**Funding:** ${funding/1_000_000_000:.1f}B")
                    elif funding >= 1_000_000:
                        st.write(f"**Funding:** ${funding/1_000_000:.1f}M")
                    else:
                        st.write(f"**Funding:** ${funding:,.0f}")
                
                if deal.get('lead_investor'):
                    st.write(f"**Lead Investor:** {deal['lead_investor']}")
            
            with col3:
                if deal.get('location'):
                    st.write(f"**Location:** {deal['location']}")
                if deal.get('confidence_score'):
                    score = deal['confidence_score'] * 100
                    st.write(f"**Confidence:** {score:.0f}%")
            
            # Description
            if deal.get('description'):
                st.write("")
                st.write(f"**Description:** {deal['description']}")
            
            # Key Signals
            if deal.get('key_signals'):
                st.write("")
                st.write("**🎯 Key Signals:**")
                for signal in deal['key_signals']:
                    st.success(f"• {signal}")
            
            # Potential Fit
            if deal.get('potential_fit'):
                st.write("")
                st.info(f"**Potential Fit:** {deal['potential_fit']}")
            
            # Risk Flags
            if deal.get('risk_flags'):
                st.write("")
                st.write("**⚠️ Risk Flags:**")
                for risk in deal['risk_flags']:
                    st.warning(f"• {risk}")
            
            # Sources & Links
            col1, col2 = st.columns(2)
            with col1:
                if deal.get('sources'):
                    st.caption(f"📰 Sources: {', '.join(deal['sources'])}")
            with col2:
                if deal.get('website'):
                    st.markdown(f"[🔗 Visit Website]({deal['website']})")


def download_report(format_type, criteria):
    """Download report in specified format"""
    
    with st.spinner(f"Generating {format_type.upper()} report..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/companies/export-report",
                json={
                    "criteria": criteria,
                    "format": format_type
                },
                timeout=120
            )
            
            if response.status_code == 200:
                # Create download link
                from datetime import datetime
                filename = f"Daily_Deals_Report_{datetime.now().strftime('%Y%m%d')}.{format_type if format_type != 'text' else 'txt'}"
                
                st.download_button(
                    label=f"⬇️ Download {format_type.upper()}",
                    data=response.content,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if format_type == "docx" else "text/html" if format_type == "html" else "text/plain"
                )
                
                st.success(f"✅ Report generated! Click above to download.")
            else:
                st.error(f"Failed to generate report: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")


def fetch_deal_stats():
    """Fetch deal statistics"""
    
    with st.spinner("Loading statistics..."):
        try:
            response = requests.get(f"{API_BASE_URL}/companies/stats")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    stats = result.get("stats", {})
                    
                    # Overview metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Deals", stats.get("total_deals", 0))
                    with col2:
                        st.metric("Avg Score", f"{stats.get('avg_score', 0):.1f}")
                    with col3:
                        st.metric("Platforms", len(stats.get("by_platform", {})))
                    with col4:
                        last_updated = stats.get("last_updated", "Never")
                        st.metric("Last Updated", last_updated if last_updated != "Never" else "N/A")
                    
                    st.divider()
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if stats.get("by_platform"):
                            st.write("**Deals by Platform**")
                            for platform, count in stats["by_platform"].items():
                                st.write(f"- {platform}: {count}")
                    
                    with col2:
                        if stats.get("by_recommendation"):
                            st.write("**By Recommendation**")
                            for rec, count in stats["by_recommendation"].items():
                                st.write(f"- {rec}: {count}")
                    
                    # More details
                    if stats.get("by_industry"):
                        with st.expander("🏭 Top Industries"):
                            for industry, count in list(stats["by_industry"].items())[:15]:
                                st.write(f"- {industry}: {count}")
                    
                    if stats.get("by_location"):
                        with st.expander("🌍 Top Locations"):
                            for location, count in list(stats["by_location"].items())[:15]:
                                st.write(f"- {location}: {count}")
                else:
                    st.info(result.get("message", "No statistics available yet"))
            else:
                st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")


def display_deals_table(deals):
    """Display deals in a formatted table"""
    
    for deal in deals:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                # Company name and description
                name = deal.get("deal", {}).get("name") if "deal" in deal else deal.get("name", "Unknown")
                desc = deal.get("deal", {}).get("description") if "deal" in deal else deal.get("description", "")
                
                st.write(f"### {name}")
                if desc:
                    st.caption(desc[:200] + "..." if len(desc) > 200 else desc)
            
            with col2:
                # Key metrics
                deal_data = deal.get("deal", {}) if "deal" in deal else deal
                
                funding = deal_data.get("funding_amount", 0)
                if funding:
                    st.metric("Funding", f"${funding/1_000_000:.1f}M")
                
                stage = deal_data.get("stage", "N/A")
                if stage:
                    st.write(f"**Stage:** {stage}")
                
                location = deal_data.get("location", "N/A")
                if location:
                    st.write(f"**Location:** {location}")
            
            with col3:
                # Score and source
                if "score" in deal:
                    score = deal.get("score", 0)
                    score_color = "🟢" if score >= 75 else "🟡" if score >= 60 else "🔴"
                    st.metric("Score", f"{score_color} {score:.0f}")
                
                source = deal_data.get("source", "Unknown")
                source_url = deal_data.get("source_url", "")
                source_article = deal_data.get("source_article_title", "")
                
                if source_url:
                    # Show clickable link to original article
                    st.markdown(f"**Source:** [{source}]({source_url})")
                    if source_article:
                        st.caption(f"📰 {source_article[:50]}..." if len(source_article) > 50 else f"📰 {source_article}")
                else:
                    st.caption(f"📍 {source}")
            
            st.divider()


def display_qualified_deals_table(deals):
    """Display qualified deals with full details"""
    
    for deal in deals:
        with st.expander(f"{'🟢' if deal.get('recommendation') == 'Strong Pass' else '🟡'} {deal.get('deal', {}).get('name', 'Unknown')} - Score: {deal.get('score', 0):.0f}"):
            
            deal_data = deal.get("deal", {})
            
            # Basic info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Industry:** {deal_data.get('industry', 'N/A')}")
                st.write(f"**Stage:** {deal_data.get('stage', 'N/A')}")
            
            with col2:
                funding = deal_data.get("funding_amount", 0)
                st.write(f"**Funding:** ${funding/1_000_000:.1f}M" if funding else "**Funding:** N/A")
                st.write(f"**Location:** {deal_data.get('location', 'N/A')}")
            
            with col3:
                st.write(f"**Recommendation:** {deal.get('recommendation', 'N/A')}")
                st.write(f"**Source:** {deal_data.get('source', 'N/A')}")
            
            # Description
            desc = deal_data.get("description", "")
            if desc:
                st.write("**Description:**")
                st.write(desc)
            
            # Scores breakdown
            if deal.get("scores"):
                st.write("**Score Breakdown:**")
                scores = deal["scores"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Market", f"{scores.get('market_opportunity', 0):.0f}")
                    st.metric("Team", f"{scores.get('team', 0):.0f}")
                with col2:
                    st.metric("Product", f"{scores.get('product', 0):.0f}")
                    st.metric("Traction", f"{scores.get('traction', 0):.0f}")
                with col3:
                    st.metric("Financials", f"{scores.get('financials', 0):.0f}")
                    st.metric("Strategic Fit", f"{scores.get('strategic_fit', 0):.0f}")
            
            # Strengths and concerns
            col1, col2 = st.columns(2)
            
            with col1:
                strengths = deal.get("strengths", [])
                if strengths:
                    st.write("**✅ Strengths:**")
                    for strength in strengths:
                        st.success(f"• {strength}")
            
            with col2:
                concerns = deal.get("concerns", [])
                if concerns:
                    st.write("**⚠️ Concerns:**")
                    for concern in concerns:
                        st.warning(f"• {concern}")
            
            # Analysis
            analysis = deal.get("analysis", "")
            if analysis:
                st.write("**📝 Analysis:**")
                st.write(analysis)
            
            # Links
            if deal_data.get("source_url"):
                st.write(f"[🔗 View on {deal_data.get('source', 'Platform')}]({deal_data['source_url']})")


def show_market_intelligence_page():
    """Market Intelligence & Competitive Analysis page"""
    
    st.write("# 🌐 Market Intelligence & Competitive Analysis")
    st.write("Generate comprehensive market research and competitive insights")
    
    st.write("")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Market Analysis", "🏢 Competitor Analysis", "📈 Industry Trends"])
    
    with tab1:
        show_market_analysis_tab()
    
    with tab2:
        show_competitor_analysis_tab()
    
    with tab3:
        show_industry_trends_tab()


def show_market_analysis_tab():
    """Market analysis tab"""
    st.write("### 📊 Comprehensive Market Analysis")
    st.write("Generate detailed market research for companies and industries")
    
    st.write("")
    
    # Input form
    with st.form("market_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name",
                placeholder="e.g., Anthropic, Stripe, SpaceX",
                help="Enter the company name to analyze"
            )
            
            industry = st.text_input(
                "Industry/Sector",
                placeholder="e.g., AI & Machine Learning, Fintech, Aerospace",
                help="Specify the industry or sector"
            )
        
        with col2:
            company_desc = st.text_area(
                "Company Description (Optional)",
                placeholder="Brief description of the company...",
                help="Provide context to improve analysis quality"
            )
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            include_competitors = st.checkbox("Include Competitive Analysis", value=True)
        
        with col4:
            include_trends = st.checkbox("Include Industry Trends", value=True)
        
        with col5:
            include_regulatory = st.checkbox("Include Regulatory Analysis", value=True)
        
        submitted = st.form_submit_button("🔍 Generate Market Analysis", type="primary")
    
    if submitted:
        if not company_name or not industry:
            st.error("⚠️ Please provide both company name and industry")
            return
        
        with st.spinner(f"🔎 Analyzing market for {company_name}..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/market/analyze",
                    json={
                        "company_name": company_name,
                        "industry": industry,
                        "description": company_desc if company_desc else None,
                        "include_competitors": include_competitors,
                        "include_trends": include_trends,
                        "include_regulatory": include_regulatory
                    },
                    timeout=120  # Market research can take time
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"✅ Market analysis completed for {company_name}")
                    
                    # Market Overview
                    st.write("---")
                    st.write("### 📈 Market Overview")
                    
                    # Key Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        market_size = data['metrics']['market_size']
                        if market_size >= 1_000_000_000:
                            st.metric("Market Size", f"${market_size/1_000_000_000:.1f}B")
                        else:
                            st.metric("Market Size", f"${market_size/1_000_000:.1f}M")
                    
                    with col2:
                        st.metric("Growth Rate", f"{data['metrics']['growth_rate']:.1f}%")
                    
                    with col3:
                        st.metric("Market Position", f"#{data['metrics']['market_position']}")
                    
                    with col4:
                        st.metric("YoY Growth", f"{data['metrics']['yoy_growth']:.1f}%")
                    
                    # Market Overview Text
                    st.write("")
                    st.info(data['market_overview'])
                    
                    # Trends
                    if include_trends and data.get('trends'):
                        st.write("---")
                        st.write("### 📊 Key Trends")
                        for trend in data['trends']:
                            st.write(f"• {trend}")
                    
                    # Competitive Position
                    if include_competitors:
                        st.write("---")
                        st.write("### 🏆 Competitive Position")
                        
                        # Competitor Market Shares
                        if data['metrics'].get('market_shares'):
                            st.write("**Market Share Distribution:**")
                            
                            import pandas as pd
                            shares_df = pd.DataFrame([
                                {"Company": company, "Market Share": f"{share:.1f}%"}
                                for company, share in data['metrics']['market_shares'].items()
                            ])
                            st.dataframe(shares_df, use_container_width=True, hide_index=True)
                        
                        st.write("")
                        st.write("**Competitive Analysis:**")
                        st.write(data['competitive_position'])
                        
                        if data.get('competitors'):
                            st.write("**Key Competitors:**")
                            for competitor in data['competitors']:
                                st.write(f"• {competitor}")
                    
                    # Opportunities & Threats
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("---")
                        st.write("### ✅ Opportunities")
                        for opp in data['opportunities']:
                            st.write(f"• {opp}")
                    
                    with col2:
                        st.write("---")
                        st.write("### ⚠️ Threats")
                        for threat in data['threats']:
                            st.write(f"• {threat}")
                    
                    # Key Drivers
                    st.write("---")
                    st.write("### 🚀 Key Growth Drivers")
                    for driver in data['key_drivers']:
                        st.write(f"• {driver}")
                    
                    # Regulatory
                    if include_regulatory:
                        st.write("---")
                        st.write("### ⚖️ Regulatory Environment")
                        st.write(data['regulatory_environment'])
                    
                    # Full Report
                    if data.get('report_text'):
                        st.write("---")
                        with st.expander("📄 View Full Report"):
                            st.markdown(data['report_text'])
                    
                else:
                    st.error(f"Failed to generate analysis: {response.text}")
            
            except requests.Timeout:
                st.error("⏱️ Request timed out. Market research can take time - please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_competitor_analysis_tab():
    """Competitor analysis tab"""
    st.write("### 🏢 Competitor Analysis")
    st.write("Identify and analyze key competitors in your market")
    
    st.write("")
    
    with st.form("competitor_form"):
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Stripe, Square, Adyen",
            help="Enter the company to analyze"
        )
        
        industry = st.text_input(
            "Industry",
            placeholder="e.g., Payments & Fintech",
            help="Specify the industry"
        )
        
        submitted = st.form_submit_button("🔍 Analyze Competitors", type="primary")
    
    if submitted:
        if not company_name or not industry:
            st.error("⚠️ Please provide both company name and industry")
            return
        
        with st.spinner(f"🔎 Analyzing competitors for {company_name}..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/market/competitors",
                    json={
                        "company_name": company_name,
                        "industry": industry
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"✅ Competitor analysis completed")
                    
                    st.write("---")
                    
                    # Market Shares Table
                    st.write("### 📊 Market Share Distribution")
                    
                    import pandas as pd
                    df = pd.DataFrame([
                        {"Competitor": comp, "Market Share": f"{share:.1f}%"}
                        for comp, share in data['competitors'].items()
                    ])
                    
                    # Sort by market share
                    df = df.sort_values("Market Share", ascending=False)
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Competitive Position
                    st.write("---")
                    st.write("### 🏆 Competitive Position Analysis")
                    st.info(data['competitive_position'])
                
                else:
                    st.error(f"Failed to analyze competitors: {response.text}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_industry_trends_tab():
    """Industry trends tab"""
    st.write("### 📈 Industry Trends Analysis")
    st.write("Discover current trends and market dynamics")
    
    st.write("")
    
    with st.form("trends_form"):
        industry = st.text_input(
            "Industry/Sector",
            placeholder="e.g., Fintech, AI, Healthcare",
            help="Enter the industry to analyze"
        )
        
        count = st.slider(
            "Number of Trends",
            min_value=3,
            max_value=15,
            value=5,
            help="How many trends to retrieve"
        )
        
        submitted = st.form_submit_button("🔍 Get Industry Trends", type="primary")
    
    if submitted:
        if not industry:
            st.error("⚠️ Please provide an industry")
            return
        
        with st.spinner(f"🔎 Analyzing trends in {industry}..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/market/trends",
                    json={
                        "industry": industry,
                        "count": count
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"✅ Found {len(data['trends'])} key trends in {industry}")
                    
                    st.write("---")
                    st.write(f"### 🔥 Top Trends in {industry}")
                    
                    for i, trend in enumerate(data['trends'], 1):
                        with st.container():
                            st.write(f"**{i}. {trend}**")
                            st.write("")
                
                else:
                    st.error(f"Failed to fetch trends: {response.text}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_upload_page():
    """Upload documents page"""
    
    st.write("### 📤 Upload Documents")
    st.write("Upload investment-related documents for analysis")
    
    st.write("")  # Spacing
    
    # Category selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category = st.selectbox(
            "Document Category",
            ["Financial Documents", "Legal Documents", "Market Research", "Company Reports", "Other"],
            help="Categorize your documents for better organization"
        )
    
    with col2:
        st.write("")  # Spacing
    
    # Map display names to backend values
    category_map = {
        "Financial Documents": "financial",
        "Legal Documents": "legal",
        "Market Research": "market",
        "Company Reports": "company",
        "Other": "other"
    }
    
    st.write("")  # Spacing
    
    # File uploader - clean design without wrapper box
    uploaded_files = st.file_uploader(
        "📁 Choose files to upload",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'txt', 'pptx', 'ppt', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Drag and drop files here or click to browse\n\nSupported: PDF, DOCX, XLSX, PPTX, CSV, TXT, Images (up to 100MB per file)",
        label_visibility="visible"
    )
    
    if uploaded_files:
        st.write("")  # Spacing
        st.info(f"📋 **{len(uploaded_files)} file(s) selected**")
        
        # Show files in a clean format
        for idx, file in enumerate(uploaded_files, 1):
            file_size = len(file.getvalue()) / (1024 * 1024)  # Convert to MB
            st.write(f"{idx}. `{file.name}` - {file_size:.2f} MB")
        
        st.write("")  # Spacing
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("📤 Upload Files", type="primary", use_container_width=True):
                with st.spinner("Uploading files..."):
                    result = upload_files(uploaded_files, category_map[category])
                    
                    if result and result.get("success"):
                        st.success(f"✅ Successfully uploaded {result.get('uploaded_count', 0)} files!")
                        
                        if result.get("errors"):
                            st.warning(f"⚠️ {len(result['errors'])} file(s) failed to upload")
                            with st.expander("View errors"):
                                for error in result['errors']:
                                    st.error(f"{error['filename']}: {error['error']}")
                    else:
                        st.error("Failed to upload files. Please try again.")
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.rerun()
    
    st.divider()
    
    # Supported file types info
    with st.expander("ℹ️ Supported File Types & Guidelines"):
        st.write("""
        **Supported File Types:**
        - 📄 **Documents:** PDF, DOCX, DOC, TXT
        - 📊 **Spreadsheets:** XLSX, XLS, CSV
        - 📽️ **Presentations:** PPTX, PPT
        - 🖼️ **Images:** JPG, JPEG, PNG (with OCR)
        
        **Upload Guidelines:**
        - Maximum file size: 100 MB per file
        - Batch upload: Up to 10 files at once
        - Categories help organize and process documents efficiently
        - Clear file names improve searchability
        """)


def show_library_page():
    """Document library page"""
    
    st.write("### 📁 Document Library")
    st.write("View and manage uploaded documents")
    
    # Filter options
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "Financial", "Legal", "Market", "Company", "Other"]
        )
    
    with col2:
        st.write("")  # Spacing
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get files
    category = category_filter.lower() if category_filter != "All" else None
    files_data = get_uploaded_files(category)
    
    if files_data and files_data.get("files"):
        files = files_data["files"]
        
        st.write(f"**Found {len(files)} document(s)**")
        
        # Display files in a table-like format
        for idx, file in enumerate(files):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"📄 **{file['filename']}**")
                
                with col2:
                    size_mb = file['size'] / (1024 * 1024)
                    st.write(f"{size_mb:.2f} MB")
                
                with col3:
                    created = datetime.fromisoformat(file['created_at'])
                    st.write(created.strftime("%Y-%m-%d %H:%M"))
                
                with col4:
                    if st.button("🗑️", key=f"delete_{idx}"):
                        with st.spinner("Deleting file..."):
                            result = delete_file(file['filename'])
                            if result and result.get("success"):
                                st.success("✅ File deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete file")
                
                st.divider()
    else:
        st.info("📭 No documents uploaded yet. Go to Upload Documents to get started!")


def show_analysis_page():
    """Analysis page with document analysis features"""
    
    st.write("### 📊 Document Analysis")
    st.write("Analyze uploaded documents for investment insights")
    
    # Get uploaded files
    files_data = get_uploaded_files()
    
    if not files_data or not files_data.get("files"):
        st.warning("📭 No documents uploaded yet. Please upload documents first!")
        return
    
    files = files_data["files"]
    
    # File selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_file = st.selectbox(
            "Select a document to analyze",
            options=[f['filename'] for f in files],
            help="Choose a document from your uploaded files"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["llm_powered", "comprehensive", "summary", "red_flags", "financial"],
            help="Type of analysis to perform"
        )
        
        # Show LLM info if selected
        if analysis_type == "llm_powered":
            st.info("🤖 **LLM-Powered Analysis**: Uses AI to provide deep insights, risk assessment, and investment recommendations. Pre-processes with keyword analysis then applies GPT-4 reasoning.")
    
    # Analyze button
    if st.button("🔍 Analyze Document", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing {selected_file}..."):
            try:
                # Route to appropriate endpoint based on analysis type
                if analysis_type == "llm_powered":
                    endpoint = f"{API_BASE_URL}/llm/analyze"
                    payload = {"filename": selected_file}
                else:
                    endpoint = f"{API_BASE_URL}/analysis/analyze"
                    payload = {
                        "filename": selected_file,
                        "analysis_type": analysis_type
                    }
                
                response = requests.post(endpoint, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle both "success" (keyword API) and "status" (LLM API) response formats
                    is_success = result.get("success") or result.get("status") == "success"
                    
                    if is_success:
                        st.success("✅ Analysis completed successfully!")
                        
                        # Display results based on analysis type
                        analysis = result.get("analysis", {})
                        
                        if analysis_type == "llm_powered":
                            display_llm_analysis(analysis, result)
                        elif analysis_type == "comprehensive":
                            display_comprehensive_analysis(analysis, result)
                        elif analysis_type == "summary":
                            display_summary_analysis(analysis)
                        elif analysis_type == "red_flags":
                            display_red_flags_analysis(analysis)
                        elif analysis_type == "financial":
                            display_financial_analysis(analysis)
                    else:
                        st.error(f"Analysis failed: {result.get('error')}")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error analyzing document: {str(e)}")
    
    # Quick actions
    st.divider()
    st.write("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Extract Content", use_container_width=True):
            with st.spinner("Extracting content..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/analysis/extract/{selected_file}")
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Content extracted!")
                        
                        with st.expander("📄 Extracted Text", expanded=True):
                            st.text_area("Content", result.get("text", ""), height=300)
                        
                        if result.get("tables"):
                            with st.expander(f"📊 Tables ({result.get('table_count', 0)})"):
                                st.json(result.get("tables"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("🚨 Red Flags Only", use_container_width=True):
            with st.spinner("Detecting red flags..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/analysis/red-flags/{selected_file}")
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            analysis = result.get("analysis", {})
                            display_red_flags_analysis(analysis)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col3:
        if st.button("📝 Quick Summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/analysis/summary/{selected_file}")
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            analysis = result.get("analysis", {})
                            display_summary_analysis(analysis)
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def display_llm_analysis(analysis: dict, result: dict):
    """Display LLM-powered analysis results"""
    
    # Extract LLM analysis data
    llm_data = analysis.get("llm_analysis", {})
    
    # Executive Summary
    exec_summary = llm_data.get("executive_summary") or llm_data.get("risk_assessment", {}).get("analysis", "")
    if exec_summary:
        st.write("### 📋 Executive Summary")
        st.info(exec_summary)
    
    # Investment Recommendation
    st.write("### 💡 Investment Recommendation")
    rec_data = llm_data.get("recommendation", {})
    recommendation = rec_data.get("action", "N/A")
    confidence = rec_data.get("confidence", 0)
    reasoning = rec_data.get("reasoning", "")
    
    recommendation_colors = {
        "BUY": "🟢",
        "HOLD": "🟡",
        "AVOID": "🔴"
    }
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(
            "Recommendation",
            f"{recommendation_colors.get(recommendation, '⚪')} {recommendation}"
        )
    with col2:
        st.metric("Confidence", f"{confidence}%")
    
    if reasoning:
        st.write(f"**Reasoning:** {reasoning}")
    
    # Risk Assessment
    st.write("### ⚠️ Risk Assessment")
    risk = llm_data.get("risk_assessment", {})
    
    col1, col2 = st.columns([1, 3])
    with col1:
        risk_score = risk.get("score", 0)
        risk_color = "🔴" if risk_score >= 7 else "🟡" if risk_score >= 4 else "🟢"
        st.metric("Risk Score", f"{risk_color} {risk_score}/10")
    
    with col2:
        risk_analysis = risk.get("analysis", "")
        if risk_analysis:
            st.write(f"**Analysis:** {risk_analysis}")
    
    # Critical Risks
    critical_risks = risk.get("critical_risks", [])
    if critical_risks:
        with st.expander("🚨 Critical Risks", expanded=True):
            for r in critical_risks:
                severity = r.get("severity", 0)
                issue = r.get("issue", "")
                impact = r.get("impact", "")
                st.error(f"**{r.get('category', '').upper()}** (Severity: {severity}/10)")
                st.write(f"Issue: {issue}")
                st.write(f"Impact: {impact}")
                if r.get("mitigation"):
                    st.success(f"💡 Mitigation: {r['mitigation']}")
                st.divider()
    
    # Opportunity Analysis
    st.write("### 🎯 Opportunity Analysis")
    opp = llm_data.get("opportunity_analysis", {})
    
    if opp.get("analysis"):
        st.write(opp["analysis"])
    
    col1, col2 = st.columns(2)
    with col1:
        key_strengths = opp.get("key_strengths", [])
        if key_strengths:
            with st.expander("💪 Key Strengths", expanded=True):
                for strength in key_strengths:
                    st.success(f"✅ **{strength.get('area', '')}**")
                    st.write(strength.get("description", ""))
                    if strength.get("competitive_advantage"):
                        st.info(f"🎯 {strength['competitive_advantage']}")
    
    with col2:
        growth = opp.get("growth_potential", {})
        if growth:
            with st.expander("📈 Growth Potential", expanded=True):
                if growth.get("market_size"):
                    st.write(f"**Market:** {growth['market_size']}")
                if growth.get("scalability"):
                    st.write(f"**Scalability:** {growth['scalability']}")
                if growth.get("timeline"):
                    st.write(f"**Timeline:** {growth['timeline']}")
    
    # Financial Health
    st.write("### 💰 Financial Health")
    fin = llm_data.get("financial_health", {})
    
    if fin.get("analysis"):
        st.write(fin["analysis"])
    
    key_metrics = fin.get("key_metrics", {})
    if key_metrics:
        col1, col2, col3 = st.columns(3)
        with col1:
            if key_metrics.get("revenue_trend"):
                st.metric("Revenue Trend", key_metrics["revenue_trend"])
        with col2:
            if key_metrics.get("profitability"):
                st.metric("Profitability", key_metrics["profitability"])
        with col3:
            if key_metrics.get("cash_position"):
                st.metric("Cash Position", key_metrics["cash_position"])
    
    # Concerns and Positives
    col1, col2 = st.columns(2)
    with col1:
        concerns = fin.get("concerns", [])
        if concerns:
            with st.expander("⚠️ Concerns"):
                for concern in concerns:
                    st.warning(f"• {concern}")
    
    with col2:
        positives = fin.get("positives", [])
        if positives:
            with st.expander("✅ Positives"):
                for positive in positives:
                    st.success(f"• {positive}")
    
    # Next Steps
    next_steps = llm_data.get("next_steps", [])
    if next_steps:
        st.write("### 📝 Recommended Next Steps")
        for i, step in enumerate(next_steps, 1):
            if isinstance(step, dict):
                priority = step.get("priority", "medium")
                priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.write(f"{i}. {priority_emoji} **{step.get('category', '').title()}:** {step.get('action', '')}")
                if step.get("rationale"):
                    st.caption(f"   ↳ {step['rationale']}")
            else:
                st.write(f"{i}. {step}")
    
    # Raw Analysis (collapsible)
    with st.expander("🔍 View Raw Analysis JSON"):
        st.json(analysis)
        st.write("### 📝 Recommended Next Steps")
        for i, step in enumerate(analysis["next_steps"], 1):
            st.write(f"{i}. {step}")
    
    # Raw Analysis (collapsible)
    with st.expander("🔍 View Raw Analysis JSON"):
        st.json(analysis)


def display_comprehensive_analysis(analysis: dict, result: dict):
    """Display comprehensive analysis results"""
    
    # Summary
    st.write("### � Document Summary")
    summary = analysis.get("summary", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Document Type", summary.get("document_type", "N/A"))
    with col2:
        st.metric("Word Count", f"{summary.get('word_count', 0):,}")
    with col3:
        st.metric("Tables", summary.get("table_count", 0))
    with col4:
        has_tables = "✅" if summary.get("has_tables") else "❌"
        st.metric("Has Tables", has_tables)
    
    if summary.get("preview"):
        with st.expander("� Document Preview"):
            st.write(summary.get("preview"))
    
    # Red Flags
    st.write("### 🚨 Red Flags Analysis")
    red_flags = analysis.get("red_flags", {})
    
    col1, col2 = st.columns(2)
    with col1:
        severity_color = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        severity = red_flags.get("severity_level", "low")
        st.metric("Severity Level", f"{severity_color.get(severity, '')} {severity.upper()}")
    with col2:
        st.metric("Total Flags", red_flags.get("total_flags", 0))
    
    if red_flags.get("has_red_flags"):
        flags_by_category = red_flags.get("flags_by_category", {})
        for category, flags in flags_by_category.items():
            if flags:
                with st.expander(f"🚩 {category.title()} ({len(flags)} issues)"):
                    for flag in flags[:5]:  # Show first 5
                        st.warning(f"**{flag['keyword']}**")
                        st.caption(flag.get('context', '')[:200])
    else:
        st.success("✅ No red flags detected!")
    
    # Positive Signals
    st.write("### ✅ Positive Signals")
    positive = analysis.get("positive_signals", {})
    
    col1, col2 = st.columns(2)
    with col1:
        strength = positive.get("strength_level", "weak")
        st.metric("Strength Level", strength.upper())
    with col2:
        st.metric("Total Signals", positive.get("total_signals", 0))
    
    if positive.get("has_positive_signals"):
        signals_by_category = positive.get("signals_by_category", {})
        for category, signals in signals_by_category.items():
            if signals:
                with st.expander(f"💚 {category.title()} ({len(signals)})"):
                    for signal in signals[:5]:
                        st.success(f"**{signal['keyword']}**")
                        st.caption(signal.get('context', '')[:200])
    
    # Financial Metrics
    st.write("### 💰 Financial Metrics")
    financial = analysis.get("financial_metrics", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Currency Values Found", financial.get("currency_values_found", 0))
    with col2:
        st.metric("Percentages Found", financial.get("percentages_found", 0))
    with col3:
        has_data = "✅" if financial.get("has_financial_data") else "❌"
        st.metric("Has Financial Data", has_data)
    
    if financial.get("sample_values"):
        with st.expander("� Sample Values"):
            st.write(", ".join(financial.get("sample_values", [])[:10]))
    
    # Recommendation
    st.write("### 🎯 Investment Recommendation")
    recommendation = analysis.get("recommendation", {})
    
    rec_text = recommendation.get("recommendation", "N/A")
    confidence = recommendation.get("confidence", "N/A")
    score = recommendation.get("score", 0)
    
    # Color code the recommendation
    rec_color = {
        "Strong Buy": "🟢",
        "Buy": "🟢",
        "Hold": "🟡",
        "Caution": "🟠",
        "Avoid": "🔴"
    }
    
    st.info(f"{rec_color.get(rec_text, '⚪')} **{rec_text}** (Confidence: {confidence}, Score: {score})")
    st.caption(recommendation.get("reasoning", ""))


def display_summary_analysis(analysis: dict):
    """Display summary analysis"""
    
    st.write("### � Document Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Type", analysis.get("document_type", "N/A"))
    with col2:
        st.metric("Words", f"{analysis.get('word_count', 0):,}")
    with col3:
        st.metric("Characters", f"{analysis.get('character_count', 0):,}")
    with col4:
        st.metric("Tables", analysis.get("table_count", 0))
    
    if analysis.get("preview"):
        st.write("**Preview:**")
        st.write(analysis.get("preview"))


def display_red_flags_analysis(analysis: dict):
    """Display red flags analysis"""
    
    st.write("### 🚨 Red Flags Detection")
    
    col1, col2 = st.columns(2)
    with col1:
        severity = analysis.get("severity_level", "low")
        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        st.metric("Severity", f"{severity_emoji.get(severity, '')} {severity.upper()}")
    with col2:
        st.metric("Total Flags", analysis.get("total_flags", 0))
    
    if analysis.get("has_red_flags"):
        flags_by_category = analysis.get("flags_by_category", {})
        
        for category, flags in flags_by_category.items():
            if flags:
                st.write(f"#### 🚩 {category.title()} Issues ({len(flags)})")
                for idx, flag in enumerate(flags):
                    with st.expander(f"{idx+1}. {flag['keyword']} - {flag.get('severity', 'low').upper()}"):
                        st.write(flag.get('context', ''))
    else:
        st.success("✅ No red flags detected in this document!")


def display_financial_analysis(analysis: dict):
    """Display financial analysis"""
    
    st.write("### � Financial Analysis")
    
    metrics = analysis.get("metrics", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Currency Values", metrics.get("currency_values_found", 0))
    with col2:
        st.metric("Percentages", metrics.get("percentages_found", 0))
    with col3:
        has_data = "✅" if metrics.get("has_financial_data") else "❌"
        st.metric("Has Data", has_data)
    
    if metrics.get("sample_values"):
        st.write("**Sample Currency Values:**")
        st.write(", ".join(metrics.get("sample_values", [])[:20]))
    
    if metrics.get("sample_percentages"):
        st.write("**Sample Percentages:**")
        st.write(", ".join(metrics.get("sample_percentages", [])[:20]))
    
    # If Excel/CSV file
    if analysis.get("has_financial_statements"):
        st.write("**Financial Statements Detected:**")
        for sheet in analysis.get("financial_sheets", []):
            with st.expander(f"📊 {sheet['name']}"):
                st.write(f"- Rows: {sheet['rows']}")
                st.write(f"- Columns: {sheet['columns']}")
                st.write(f"- Column Names: {', '.join(sheet['column_names'][:10])}")


def show_modeling_page():
    """Financial modeling page - placeholder for Phase 4"""
    
    st.write("### 💰 Financial Modeling")
    st.info("🚧 Financial modeling features will be available in Phase 4")
    
    st.write("""
    **Coming Soon:**
    - 📊 Revenue projections
    - 💵 Cash flow modeling
    - 📈 Valuation models
    - 🎯 Scenario planning
    - 📉 Sensitivity analysis
    """)


def show_reports_page():
    """Reports page - placeholder for Phase 5"""
    
    st.write("### 📝 Generate Reports")
    st.info("🚧 Report generation features will be available in Phase 5")
    
    st.write("""
    **Coming Soon:**
    - 📄 Investment memos
    - 📽️ Pitch decks
    - 📋 Due diligence summaries
    - 📊 Executive summaries
    - 🎨 Custom templates
    """)


if __name__ == "__main__":
    main()
