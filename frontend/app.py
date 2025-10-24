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
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        color: #333333;
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
            ["🏠 Home", "📤 Upload Documents", "📁 Document Library", "📊 Analysis", "💰 Financial Modeling", "📝 Generate Reports"],
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
    elif page == "📤 Upload Documents":
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
        {"icon": "🔍", "title": "AI-Powered Deal Sourcing", "status": "Coming Soon"},
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
            if feature['status'] == "Phase 1":
                st.success(feature['status'])
            else:
                st.info(feature['status'])


def show_upload_page():
    """Upload documents page"""
    
    st.write("### 📤 Upload Documents")
    st.write("Upload investment-related documents for analysis")
    
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
    
    # File uploader
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'txt', 'pptx', 'ppt', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, XLSX, PPTX, CSV, TXT, Images"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            file_size = len(file.getvalue()) / (1024 * 1024)  # Convert to MB
            st.write(f"- {file.name} ({file_size:.2f} MB)")
        
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
                        st.warning("Delete functionality coming soon!")
                
                st.divider()
    else:
        st.info("📭 No documents uploaded yet. Go to Upload Documents to get started!")


def show_analysis_page():
    """Analysis page - placeholder for Phase 2"""
    
    st.write("### 📊 Document Analysis")
    st.info("🚧 Document analysis features will be available in Phase 2")
    
    st.write("""
    **Coming Soon:**
    - 📄 Automated document summarization
    - 🔍 Key insights extraction
    - 🚨 Red flag identification
    - 💡 AI-powered recommendations
    - 📈 Trend analysis
    """)


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
