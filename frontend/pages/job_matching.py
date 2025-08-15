"""
Job matching page for Streamlit frontend
"""
import streamlit as st
import time
import json
from frontend.components.ui_components import (
    render_job_description_form, show_loading_spinner, show_success_message,
    show_error_message, show_info_message, render_match_results
)

def render_matching_page():
    """Render the job matching page"""

    st.markdown("## 🔍 Job Matching")
    st.markdown("Enter a job description to find the best matching candidates from your resume database.")

    # Check if we have resumes in the database
    resume_count = st.session_state.get_resume_count()

    if resume_count == 0:
        st.warning("⚠️ No resumes found in the database. Please upload some resumes first.")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📄 Go to Upload Page", use_container_width=True):
                st.session_state.page = 'upload'
                st.rerun()
        return

    # Show database stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📚 Total Resumes", resume_count)

    with col2:
        threshold = st.session_state.get('similarity_threshold', 0.7)
        st.metric("🎯 Similarity Threshold", f"{threshold:.1%}")

    with col3:
        top_k = st.session_state.get('top_k', 10)
        st.metric("📊 Max Results", top_k)

    with col4:
        # API status
        try:
            is_connected = st.session_state.check_api_connection()
            status = "🟢 Online" if is_connected else "🔴 Offline"
            st.metric("🔌 API Status", status)
        except:
            st.metric("🔌 API Status", "🟡 Unknown")

    st.markdown("---")

    # Job description form
    job_request = render_job_description_form()

    # Process job matching request
    if job_request:
        process_job_matching(job_request)

    # Show example job descriptions
    render_example_jobs()

    # Show recent matching history
    render_matching_history()

def process_job_matching(job_request):
    """Process job matching request"""

    try:
        with show_loading_spinner("🔍 Searching for matching candidates..."):

            # Add progress indicators
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Generate job embedding
                status_text.text("Analyzing job description...")
                progress_bar.progress(0.2)
                time.sleep(0.5)

                # Step 2: Search FAISS index
                status_text.text("Searching resume database...")
                progress_bar.progress(0.5)
                time.sleep(0.5)

                # Step 3: Generate explanations
                status_text.text("Generating match explanations...")
                progress_bar.progress(0.8)

                # Call API
                results = st.session_state.match_job_to_resumes(job_request)

                progress_bar.progress(1.0)
                status_text.text("Matching complete!")

        if results:
            # Store results in session state
            st.session_state.match_results = results
            st.session_state.current_job_title = job_request['job_description']['title']

            # Store in matching history
            store_matching_history(job_request, results)

            # Show success message
            show_success_message(
                f"Found {results['matches_found']} matching candidates in {results['processing_time']:.2f} seconds!"
            )

            # Display results
            render_match_results(results)

            # Option to save results or go to results page
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("💾 Save Results", use_container_width=True):
                    save_results_to_file(results, job_request['job_description']['title'])

            with col2:
                if st.button("📊 View Analytics", use_container_width=True):
                    st.session_state.page = 'results'
                    st.rerun()

            with col3:
                if st.button("🔍 New Search", use_container_width=True):
                    st.rerun()

        else:
            show_error_message("No results returned from the matching service. Please try again.")

    except Exception as e:
        show_error_message(f"Matching failed: {str(e)}")

def render_example_jobs():
    """Render example job descriptions"""

    st.markdown("---")
    st.markdown("### 💡 Example Job Descriptions")

    examples = {
        "Senior Python Developer": {
            "title": "Senior Python Developer",
            "description": """We are looking for a Senior Python Developer to join our growing team. 
            You will be responsible for developing scalable web applications using Python and modern frameworks.
            
            Key Responsibilities:
            - Design and develop Python applications using Django/Flask
            - Work with databases (PostgreSQL, MongoDB)
            - Collaborate with cross-functional teams
            - Write clean, maintainable code with proper testing
            - Optimize application performance and scalability""",
            "requirements": """- 5+ years of Python development experience
            - Experience with Django or Flask frameworks
            - Knowledge of SQL and NoSQL databases
            - Familiarity with cloud platforms (AWS/Azure)
            - Strong problem-solving skills""",
            "location": "San Francisco, CA / Remote",
            "experience_level": "Senior Level",
            "skills": "Python, Django, Flask, PostgreSQL, MongoDB, AWS, Docker, Git"
        },

        "Frontend React Developer": {
            "title": "Frontend React Developer",
            "description": """Join our frontend team to build amazing user experiences using React and modern JavaScript.
            
            Key Responsibilities:
            - Develop responsive web applications using React
            - Collaborate with designers and backend developers
            - Optimize applications for maximum speed and scalability
            - Implement modern UI/UX designs
            - Write reusable and maintainable code""",
            "requirements": """- 3+ years of React development experience
            - Strong knowledge of JavaScript, HTML5, CSS3
            - Experience with state management (Redux/Context API)
            - Familiarity with build tools (Webpack, Vite)
            - Knowledge of testing frameworks""",
            "location": "New York, NY / Remote",
            "experience_level": "Mid Level",
            "skills": "React, JavaScript, TypeScript, HTML5, CSS3, Redux, Webpack, Jest"
        },

        "Data Scientist": {
            "title": "Data Scientist",
            "description": """We are seeking a Data Scientist to help us extract insights from large datasets and build predictive models.
            
            Key Responsibilities:
            - Analyze complex datasets to identify trends and patterns
            - Build and deploy machine learning models
            - Create data visualizations and reports
            - Collaborate with business teams to solve problems
            - Present findings to stakeholders""",
            "requirements": """- Master's degree in Data Science, Statistics, or related field
            - 4+ years of experience in data analysis and machine learning
            - Proficiency in Python and R
            - Experience with ML libraries (scikit-learn, TensorFlow, PyTorch)
            - Strong statistical analysis skills""",
            "location": "Boston, MA / Remote",
            "experience_level": "Senior Level",
            "skills": "Python, R, Machine Learning, TensorFlow, PyTorch, SQL, Pandas, NumPy, Matplotlib"
        }
    }

    selected_example = st.selectbox(
        "Choose an example to try:",
        ["Select an example..."] + list(examples.keys())
    )

    if selected_example != "Select an example...":
        example = examples[selected_example]

        with st.expander(f"👀 Preview: {selected_example}"):
            st.markdown(f"**Title:** {example['title']}")
            st.markdown(f"**Description:**\n{example['description']}")
            st.markdown(f"**Requirements:**\n{example['requirements']}")
            st.markdown(f"**Location:** {example['location']}")
            st.markdown(f"**Experience Level:** {example['experience_level']}")
            st.markdown(f"**Skills:** {example['skills']}")

        if st.button(f"🚀 Use '{selected_example}' Example", use_container_width=True):
            # Create job request from example
            skills_list = [skill.strip() for skill in example['skills'].split(',')]

            job_request = {
                "job_description": {
                    "title": example['title'],
                    "description": example['description'],
                    "requirements": example['requirements'],
                    "location": example['location'],
                    "experience_level": example['experience_level'],
                    "skills_required": skills_list
                },
                "top_k": st.session_state.get('top_k', 10),
                "similarity_threshold": st.session_state.get('similarity_threshold', 0.7)
            }

            # Process the example job
            process_job_matching(job_request)

def render_matching_history():
    """Render recent matching history"""

    if 'matching_history' not in st.session_state or not st.session_state.matching_history:
        return

    st.markdown("---")
    st.markdown("### 📚 Recent Searches")

    # Show last 5 searches
    recent_searches = st.session_state.matching_history[-5:]

    for i, search in enumerate(reversed(recent_searches)):
        with st.expander(f"🔍 {search['job_title']} - {search['matches_found']} matches"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Search Time:** {search['timestamp']}")
                st.write(f"**Matches Found:** {search['matches_found']}")
                st.write(f"**Processing Time:** {search['processing_time']:.2f}s")

            with col2:
                st.write(f"**Threshold Used:** {search['threshold']:.1%}")
                st.write(f"**Top K:** {search['top_k']}")
                if search.get('avg_similarity'):
                    st.write(f"**Avg Similarity:** {search['avg_similarity']:.1%}")

            if st.button(f"🔄 Repeat Search", key=f"repeat_{i}"):
                # Repeat this search
                process_job_matching(search['job_request'])

def store_matching_history(job_request, results):
    """Store matching history in session state"""

    if 'matching_history' not in st.session_state:
        st.session_state.matching_history = []

    # Calculate average similarity
    avg_similarity = 0
    if results.get('matches'):
        avg_similarity = sum(match['similarity_score'] for match in results['matches']) / len(results['matches'])

    history_item = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'job_title': job_request['job_description']['title'],
        'job_request': job_request,
        'matches_found': results['matches_found'],
        'processing_time': results['processing_time'],
        'threshold': job_request['similarity_threshold'],
        'top_k': job_request['top_k'],
        'avg_similarity': avg_similarity
    }

    st.session_state.matching_history.append(history_item)

    # Keep only last 50 searches
    if len(st.session_state.matching_history) > 50:
        st.session_state.matching_history = st.session_state.matching_history[-50:]

def save_results_to_file(results, job_title):
    """Save matching results to a JSON file"""

    try:
        # Prepare data for download
        download_data = {
            'job_title': job_title,
            'search_timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_resumes_searched': results['total_resumes'],
            'matches_found': results['matches_found'],
            'processing_time': results['processing_time'],
            'matches': results['matches']
        }

        # Convert to JSON
        json_str = json.dumps(download_data, indent=2, default=str)

        # Create download button
        st.download_button(
            label="📥 Download Results (JSON)",
            data=json_str,
            file_name=f"job_matching_results_{job_title.replace(' ', '_').lower()}_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )

        show_success_message("Results prepared for download!")

    except Exception as e:
        show_error_message(f"Failed to prepare download: {str(e)}")

def render_advanced_filters():
    """Render advanced filtering options"""

    st.markdown("---")
    st.markdown("### ⚙️ Advanced Filters")

    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)

        with col1:
            # Experience range filter
            experience_filter = st.checkbox("Filter by Experience")
            if experience_filter:
                min_exp, max_exp = st.slider(
                    "Years of Experience",
                    min_value=0, max_value=20,
                    value=(0, 20),
                    step=1
                )

        with col2:
            # Skills weight adjustment
            skills_weight = st.slider(
                "Skills Matching Weight",
                min_value=0.0, max_value=1.0,
                value=0.5, step=0.1,
                help="Higher values prioritize skill matches over general similarity"
            )

        # Location preference
        location_filter = st.checkbox("Filter by Location")
        if location_filter:
            preferred_locations = st.text_input(
                "Preferred Locations (comma-separated)",
                placeholder="San Francisco, New York, Remote"
            )

        # Education level filter
        education_filter = st.checkbox("Filter by Education")
        if education_filter:
            education_levels = st.multiselect(
                "Required Education Levels",
                ["High School", "Bachelor's", "Master's", "PhD", "Certification"]
            )

if __name__ == "__main__":
    render_matching_page()