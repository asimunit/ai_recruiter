"""
UI components for Streamlit frontend
"""
import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Recruitr</h1>
        <p>Smart Resume Matcher using FAISS + Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown("### 🧭 Navigation")

        # Navigation options
        pages = {
            "📄 Upload Resumes": "upload",
            "🔍 Job Matching": "matching",
            "📊 Results & Analytics": "results"
        }

        selected = st.radio("Go to:", list(pages.keys()), key="navigation")
        current_page = pages[selected]

        st.markdown("---")

        # Quick stats
        st.markdown("### 📈 Quick Stats")

        try:
            resume_count = st.session_state.get_resume_count()
            st.metric("Total Resumes", resume_count)
        except:
            st.metric("Total Resumes", "N/A")

        # API Connection Status
        st.markdown("### 🔌 API Status")
        render_api_status_indicator()

        st.markdown("---")

        # Settings
        st.markdown("### ⚙️ Settings")

        # Initialize default values if not set
        if 'similarity_threshold' not in st.session_state:
            st.session_state.similarity_threshold = 0.7
        if 'top_k' not in st.session_state:
            st.session_state.top_k = 10

        # Similarity threshold
        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.similarity_threshold,
            step=0.05,
            key="similarity_slider",
            help="Minimum similarity score for matches"
        )

        # Top K results
        top_k = st.number_input(
            "Max Results",
            min_value=1,
            max_value=50,
            value=st.session_state.top_k,
            key="top_k_input",
            help="Maximum number of results to return"
        )

        # Update session state only if values changed
        if similarity_threshold != st.session_state.similarity_threshold:
            st.session_state.similarity_threshold = similarity_threshold
        if top_k != st.session_state.top_k:
            st.session_state.top_k = top_k

        return current_page

def render_api_status_indicator():
    """Render API connection status indicator"""
    try:
        is_connected = st.session_state.check_api_connection()

        if is_connected:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")

    except:
        st.warning("🟡 Unknown")

def show_api_status(api_url):
    """Show detailed API status"""
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("API Status", "🟢 Online")

            with col2:
                st.metric("Total Resumes", data.get('total_resumes', 0))

            with col3:
                st.metric("Version", data.get('version', 'N/A'))

            with col4:
                st.metric("Model", "Gemini + mxbai")

    except:
        st.error("❌ API connection failed. Please ensure the backend is running.")

def render_footer():
    """Render footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 AI Recruitr v1.0.0 | Built with FastAPI + Streamlit + FAISS + Gemini AI</p>
        <p>Made with ❤️ for smarter recruiting</p>
    </div>
    """, unsafe_allow_html=True)

def render_upload_stats(uploaded_files_count, processing_time=None):
    """Render upload statistics"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Files Uploaded", uploaded_files_count)

    with col2:
        if processing_time:
            st.metric("Processing Time", f"{processing_time:.2f}s")
        else:
            st.metric("Processing Time", "N/A")

    with col3:
        total_resumes = st.session_state.get_resume_count()
        st.metric("Total in Database", total_resumes)

def render_file_upload_area():
    """Render file upload area with drag and drop"""
    st.markdown("""
    <div class="upload-area">
        <h3>📁 Upload Resume Files</h3>
        <p>Drag and drop PDF, DOCX, or TXT files here</p>
        <p style="color: #666; font-size: 0.9em;">Max file size: 10MB per file</p>
    </div>
    """, unsafe_allow_html=True)

    return st.file_uploader(
        "Choose resume files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload one or more resume files to process"
    )

def render_job_description_form():
    """Render job description input form"""
    st.markdown("### 📝 Job Description")

    with st.form("job_description_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            job_title = st.text_input(
                "Job Title *",
                placeholder="e.g. Senior Python Developer",
                help="Enter the job title"
            )

            job_description = st.text_area(
                "Job Description *",
                height=200,
                placeholder="Enter the full job description including responsibilities, requirements, and qualifications...",
                help="Provide detailed job description for better matching"
            )

            requirements = st.text_area(
                "Additional Requirements",
                height=100,
                placeholder="Any specific requirements or qualifications...",
                help="Optional: Additional specific requirements"
            )

        with col2:
            location = st.text_input(
                "Location",
                placeholder="e.g. New York, Remote"
            )

            experience_level = st.selectbox(
                "Experience Level",
                ["Entry Level", "Mid Level", "Senior Level", "Executive", "Not Specified"]
            )

            skills_required = st.text_area(
                "Required Skills",
                height=100,
                placeholder="Python, JavaScript, React, SQL...",
                help="Enter comma-separated skills"
            )

        submitted = st.form_submit_button("🔍 Find Matching Resumes", use_container_width=True)

        if submitted:
            if not job_title or not job_description:
                st.error("Please fill in the required fields (Job Title and Job Description)")
                return None

            # Parse skills
            skills_list = []
            if skills_required:
                skills_list = [skill.strip() for skill in skills_required.split(',') if skill.strip()]

            return {
                "job_description": {
                    "title": job_title,
                    "description": job_description,
                    "requirements": requirements if requirements else None,
                    "location": location if location else None,
                    "experience_level": experience_level if experience_level != "Not Specified" else None,
                    "skills_required": skills_list
                },
                "top_k": st.session_state.get('top_k', 10),
                "similarity_threshold": st.session_state.get('similarity_threshold', 0.7)
            }

    return None

def render_match_results(results):
    """Render matching results"""
    if not results or not results.get('matches'):
        st.info("No matching resumes found. Try adjusting the similarity threshold or upload more resumes.")
        return

    st.success(f"Found {results['matches_found']} matching resumes in {results['processing_time']:.2f} seconds!")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Matches Found", results['matches_found'])

    with col2:
        st.metric("Total Resumes", results['total_resumes'])

    with col3:
        avg_score = sum(match['similarity_score'] for match in results['matches']) / len(results['matches'])
        st.metric("Avg. Similarity", f"{avg_score:.2%}")

    with col4:
        st.metric("Processing Time", f"{results['processing_time']:.2f}s")

    st.markdown("---")

    # Individual match results
    st.markdown("### 📋 Matching Candidates")

    for i, match in enumerate(results['matches'], 1):
        with st.expander(f"#{i} {match['filename']} - {match['similarity_score']:.1%} match"):

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Match Explanation:**")
                st.write(match['match_explanation'])

                if match.get('matching_skills'):
                    st.markdown(f"**Matching Skills:** {', '.join(match['matching_skills'])}")

                if match.get('experience_match'):
                    st.markdown(f"**Experience:** {match['experience_match']} years")

            with col2:
                # Similarity score gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = match['similarity_score'] * 100,
                    title = {'text': "Match %"},
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))

                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)

def render_analytics_dashboard(results_history):
    """Render analytics dashboard"""
    if not results_history:
        st.info("No matching history available yet. Perform some job matches to see analytics.")
        return

    st.markdown("### 📊 Analytics Dashboard")

    # Create sample analytics (in a real app, you'd store this data)
    col1, col2 = st.columns(2)

    with col1:
        # Match success rate over time
        st.markdown("#### Match Success Rate")
        success_data = [85, 78, 92, 88, 95, 82, 90]
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        fig = px.line(x=days, y=success_data, title="Weekly Match Success Rate")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top skills in demand
        st.markdown("#### Top Skills in Demand")
        skills_data = {
            'Python': 45,
            'JavaScript': 38,
            'React': 32,
            'SQL': 28,
            'AWS': 25,
            'Java': 22
        }

        fig = px.bar(x=list(skills_data.keys()), y=list(skills_data.values()),
                    title="Most Requested Skills")
        st.plotly_chart(fig, use_container_width=True)

def show_loading_spinner(message="Processing..."):
    """Show loading spinner with message"""
    return st.spinner(message)

def show_success_message(message):
    """Show success message"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Show error message"""
    st.error(f"❌ {message}")

def show_info_message(message):
    """Show info message"""
    st.info(f"ℹ️ {message}")

def render_progress_bar(progress, text=""):
    """Render progress bar"""
    progress_bar = st.progress(progress)
    if text:
        st.text(text)
    return progress_bar