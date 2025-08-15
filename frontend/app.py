"""
Streamlit main application for AI Recruitr frontend
"""
import streamlit as st
import requests
import json
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.settings import settings
from frontend.pages.upload_resume import render_upload_page
from frontend.pages.job_matching import render_matching_page
from frontend.pages.results import render_results_page
from frontend.components.ui_components import (
    render_header, render_sidebar, render_footer, show_api_status
)

# Configure Streamlit page
st.set_page_config(
    page_title="AI Recruitr - Smart Resume Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    
    .match-result {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background: #f8f9ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'upload'

    if 'api_base_url' not in st.session_state:
        st.session_state.api_base_url = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1"

    if 'uploaded_resumes' not in st.session_state:
        st.session_state.uploaded_resumes = []

    if 'match_results' not in st.session_state:
        st.session_state.match_results = None

    if 'similarity_threshold' not in st.session_state:
        st.session_state.similarity_threshold = 0.7

    if 'top_k' not in st.session_state:
        st.session_state.top_k = 10

def main():
    """Main Streamlit application"""

    # Initialize session state first
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar
    selected_page = render_sidebar()
    st.session_state.page = selected_page

    # Show API status
    show_api_status(st.session_state.api_base_url)

    # Main content area
    if st.session_state.page == 'upload':
        render_upload_page()
    elif st.session_state.page == 'matching':
        render_matching_page()
    elif st.session_state.page == 'results':
        render_results_page()

    # Render footer
    render_footer()

def check_api_connection():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{st.session_state.api_base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# API Helper Functions
def upload_resume_to_api(file):
    """Upload resume file to API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{st.session_state.api_base_url}/upload-resume",
            files=files,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def match_job_to_resumes(job_data):
    """Match job description to resumes"""
    try:
        response = requests.post(
            f"{st.session_state.api_base_url}/match-job",
            json=job_data,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Matching failed: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Matching error: {str(e)}")
        return None

def get_resume_count():
    """Get total number of resumes in database"""
    try:
        response = requests.get(f"{st.session_state.api_base_url}/resumes/count", timeout=5)
        if response.status_code == 200:
            return response.json().get('total_resumes', 0)
        return 0
    except:
        return 0

def get_index_info():
    """Get FAISS index information"""
    try:
        response = requests.get(f"{st.session_state.api_base_url}/index/info", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Make helper functions available to other modules
st.session_state.upload_resume_to_api = upload_resume_to_api
st.session_state.match_job_to_resumes = match_job_to_resumes
st.session_state.get_resume_count = get_resume_count
st.session_state.get_index_info = get_index_info
st.session_state.check_api_connection = check_api_connection

if __name__ == "__main__":
    main()