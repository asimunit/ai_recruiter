"""
Results and analytics page for Streamlit frontend
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from frontend.components.ui_components import render_analytics_dashboard


def render_results_page():
    """Render the results and analytics page"""

    st.markdown("## 📊 Results & Analytics")
    st.markdown(
        "View matching results, analytics, and insights from your recruitment activities.")

    # Check if we have any results
    if not st.session_state.get('match_results') and not st.session_state.get(
            'matching_history'):
        st.info(
            "No results available yet. Perform some job matches to see analytics here.")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔍 Start Job Matching", use_container_width=True):
                st.session_state.page = 'matching'
                st.rerun()
        return

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Current Results", "📈 Analytics", "📊 Insights", "📁 Export"])

    with tab1:
        render_current_results()

    with tab2:
        render_analytics_tab()

    with tab3:
        render_insights_tab()

    with tab4:
        render_export_tab()


def render_current_results():
    """Render current matching results"""

    if not st.session_state.get('match_results'):
        st.info(
            "No current results. Run a job match search to see results here.")
        return

    results = st.session_state.match_results
    job_title = st.session_state.get('current_job_title', 'Unknown Job')

    st.markdown(f"### 🎯 Latest Results: {job_title}")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Candidates Found", results['matches_found'])

    with col2:
        st.metric("Total Searched", results['total_resumes'])

    with col3:
        if results.get('matches'):
            avg_score = sum(match['similarity_score'] for match in
                            results['matches']) / len(results['matches'])
            st.metric("Avg. Match Score", f"{avg_score:.1%}")
        else:
            st.metric("Avg. Match Score", "N/A")

    with col4:
        st.metric("Processing Time", f"{results['processing_time']:.2f}s")

    # Score distribution chart
    if results.get('matches'):
        render_score_distribution(results['matches'])

    # Detailed results table
    render_results_table(results['matches'])


def render_score_distribution(matches):
    """Render similarity score distribution chart"""

    st.markdown("#### 📊 Score Distribution")

    scores = [match['similarity_score'] for match in matches]

    # Create histogram
    fig = px.histogram(
        x=scores,
        nbins=10,
        title="Similarity Score Distribution",
        labels={'x': 'Similarity Score', 'y': 'Number of Candidates'},
        color_discrete_sequence=['#667eea']
    )

    fig.update_layout(
        xaxis_title="Similarity Score",
        yaxis_title="Number of Candidates",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def render_results_table(matches):
    """Render detailed results table"""

    if not matches:
        st.info("No matches to display.")
        return

    st.markdown("#### 📝 Detailed Results")

    # Create DataFrame
    data = []
    for i, match in enumerate(matches, 1):
        data.append({
            'Rank': i,
            'Filename': match['filename'],
            'Score': f"{match['similarity_score']:.1%}",
            'Experience': match.get('experience_match', 'N/A'),
            'Matching Skills': len(match.get('matching_skills', [])),
            'Resume ID': match['resume_id'][:8] + "..."  # Truncate for display
        })

    df = pd.DataFrame(data)

    # Display with formatting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Match Score",
                help="Similarity score",
                min_value=0,
                max_value=1,
                format="%.1f%%"
            ),
            "Matching Skills": st.column_config.NumberColumn(
                "Skills Match",
                help="Number of matching skills",
                min_value=0
            )
        }
    )

    # Detailed view for selected candidate
    st.markdown("#### 🔍 Candidate Details")

    selected_candidate = st.selectbox(
        "Select candidate for detailed view:",
        options=range(len(matches)),
        format_func=lambda
            x: f"{matches[x]['filename']} - {matches[x]['similarity_score']:.1%}"
    )

    if selected_candidate is not None:
        render_candidate_details(matches[selected_candidate])


def render_candidate_details(match):
    """Render detailed view of a specific candidate"""

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**📄 {match['filename']}**")
        st.markdown(f"**Match Explanation:**")
        st.write(match['match_explanation'])

        if match.get('matching_skills'):
            st.markdown("**🎯 Matching Skills:**")
            skills_cols = st.columns(3)
            for i, skill in enumerate(match['matching_skills']):
                skills_cols[i % 3].badge(skill, outline=True)

    with col2:
        # Score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=match['similarity_score'] * 100,
            title={'text': "Match Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 90], 'color': "lightgreen"},
                    {'range': [90, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))

        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)


def render_analytics_tab():
    """Render analytics dashboard"""

    if not st.session_state.get('matching_history'):
        st.info("No matching history available for analytics.")
        return

    history = st.session_state.matching_history

    st.markdown("### 📈 Matching Analytics")

    # Time series analysis
    render_matching_trends(history)

    # Success rate analysis
    render_success_rate_analysis(history)

    # Popular skills analysis
    render_skills_analysis()


def render_matching_trends(history):
    """Render matching trends over time"""

    st.markdown("#### 📅 Matching Trends")

    # Prepare data
    dates = [item['timestamp'] for item in history]
    matches_found = [item['matches_found'] for item in history]
    processing_times = [item['processing_time'] for item in history]

    col1, col2 = st.columns(2)

    with col1:
        # Matches over time
        fig = px.line(
            x=dates, y=matches_found,
            title="Matches Found Over Time",
            labels={'x': 'Date', 'y': 'Matches Found'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Processing time over time
        fig = px.line(
            x=dates, y=processing_times,
            title="Processing Time Trends",
            labels={'x': 'Date', 'y': 'Processing Time (s)'}
        )
        st.plotly_chart(fig, use_container_width=True)


def render_success_rate_analysis(history):
    """Render success rate analysis"""

    st.markdown("#### ✅ Success Rate Analysis")

    # Calculate success metrics
    total_searches = len(history)
    successful_searches = sum(
        1 for item in history if item['matches_found'] > 0)
    success_rate = (
                               successful_searches / total_searches) * 100 if total_searches > 0 else 0

    avg_matches = sum(item['matches_found'] for item in
                      history) / total_searches if total_searches > 0 else 0
    avg_processing_time = sum(item['processing_time'] for item in
                              history) / total_searches if total_searches > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Success Rate", f"{success_rate:.1f}%")

    with col2:
        st.metric("Avg. Matches", f"{avg_matches:.1f}")

    with col3:
        st.metric("Total Searches", total_searches)

    with col4:
        st.metric("Avg. Time", f"{avg_processing_time:.2f}s")

    # Success rate by threshold
    thresholds = [item['threshold'] for item in history]
    threshold_success = {}

    for item in history:
        threshold = item['threshold']
        if threshold not in threshold_success:
            threshold_success[threshold] = {'total': 0, 'successful': 0}

        threshold_success[threshold]['total'] += 1
        if item['matches_found'] > 0:
            threshold_success[threshold]['successful'] += 1

    # Plot threshold vs success rate
    if len(threshold_success) > 1:
        threshold_values = []
        success_rates = []

        for threshold, data in threshold_success.items():
            threshold_values.append(threshold)
            success_rates.append((data['successful'] / data['total']) * 100)

        fig = px.scatter(
            x=threshold_values, y=success_rates,
            title="Success Rate by Similarity Threshold",
            labels={'x': 'Similarity Threshold', 'y': 'Success Rate (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)


def render_skills_analysis():
    """Render skills analysis from current results"""

    st.markdown("#### 🎯 Skills Analysis")

    if not st.session_state.get(
            'match_results') or not st.session_state.match_results.get(
            'matches'):
        st.info("No current results available for skills analysis.")
        return

    # Extract skills from current matches
    all_skills = []
    for match in st.session_state.match_results['matches']:
        all_skills.extend(match.get('matching_skills', []))

    if not all_skills:
        st.info("No skills data available in current results.")
        return

    # Count skill frequency
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1

    # Sort by frequency
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1],
                           reverse=True)[:10]

    if sorted_skills:
        skills, counts = zip(*sorted_skills)

        fig = px.bar(
            x=list(counts), y=list(skills),
            orientation='h',
            title="Top Matching Skills in Current Results",
            labels={'x': 'Frequency', 'y': 'Skills'}
        )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def render_insights_tab():
    """Render insights and recommendations"""

    st.markdown("### 💡 Insights & Recommendations")

    # Generate insights based on data
    insights = generate_insights()

    for insight in insights:
        st.markdown(f"**{insight['title']}**")
        st.info(insight['description'])

        if insight.get('action'):
            st.markdown(f"*💡 Recommendation: {insight['action']}*")

        st.markdown("---")


def generate_insights():
    """Generate insights based on matching history and results"""

    insights = []

    # Database size insight
    resume_count = st.session_state.get_resume_count()
    if resume_count < 10:
        insights.append({
            'title': '📚 Small Database Size',
            'description': f'You currently have {resume_count} resumes in your database. A larger database typically yields better matching results.',
            'action': 'Consider uploading more resumes to improve matching quality and coverage.'
        })

    # Matching history insights
    if st.session_state.get('matching_history'):
        history = st.session_state.matching_history

        # Low success rate
        successful_searches = sum(
            1 for item in history if item['matches_found'] > 0)
        success_rate = (successful_searches / len(history)) * 100

        if success_rate < 50:
            insights.append({
                'title': '📉 Low Match Success Rate',
                'description': f'Your current success rate is {success_rate:.1f}%. This might indicate that your job descriptions are very specific or your resume database needs expansion.',
                'action': 'Try lowering the similarity threshold or adding more diverse resumes to your database.'
            })

        # High processing times
        avg_time = sum(item['processing_time'] for item in history) / len(
            history)
        if avg_time > 10:
            insights.append({
                'title': '⏱️ Slow Processing Times',
                'description': f'Average processing time is {avg_time:.2f} seconds. This might be due to large resume database or API performance.',
                'action': 'Consider optimizing your FAISS index or checking your API server performance.'
            })

    # Current results insights
    if st.session_state.get('match_results'):
        results = st.session_state.match_results

        if results['matches_found'] == 0:
            insights.append({
                'title': '🎯 No Matches Found',
                'description': 'Your last search returned no matches. This might be due to a high similarity threshold or very specific job requirements.',
                'action': 'Try lowering the similarity threshold or broadening the job description.'
            })

        elif results['matches_found'] > 0:
            avg_score = sum(match['similarity_score'] for match in
                            results['matches']) / len(results['matches'])

            if avg_score < 0.6:
                insights.append({
                    'title': '📊 Low Average Similarity',
                    'description': f'Your matches have an average similarity of {avg_score:.1%}. This suggests partial matches rather than strong candidates.',
                    'action': 'Consider reviewing job requirements or expanding the resume database with more relevant profiles.'
                })

    # Default insight if no specific insights
    if not insights:
        insights.append({
            'title': '✅ System Performing Well',
            'description': 'Your AI Recruitr system appears to be working effectively with good matching performance.',
            'action': 'Continue using the system and consider sharing feedback for further improvements.'
        })

    return insights


def render_export_tab():
    """Render export options"""

    st.markdown("### 📁 Export Data")
    st.markdown(
        "Export your matching results and analytics data in various formats.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Current Results")

        if st.session_state.get('match_results'):
            # JSON export
            if st.button("📄 Export as JSON", use_container_width=True):
                export_results_json()

            # CSV export
            if st.button("📊 Export as CSV", use_container_width=True):
                export_results_csv()
        else:
            st.info("No current results to export.")

    with col2:
        st.markdown("#### Matching History")

        if st.session_state.get('matching_history'):
            # History JSON export
            if st.button("📚 Export History (JSON)", use_container_width=True):
                export_history_json()

            # Analytics report
            if st.button("📈 Generate Analytics Report",
                         use_container_width=True):
                generate_analytics_report()
        else:
            st.info("No matching history to export.")


def export_results_json():
    """Export current results as JSON"""
    import json

    if not st.session_state.get('match_results'):
        st.error("No results to export.")
        return

    data = {
        'export_timestamp': datetime.now().isoformat(),
        'job_title': st.session_state.get('current_job_title', 'Unknown'),
        'results': st.session_state.match_results
    }

    json_str = json.dumps(data, indent=2, default=str)

    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def export_results_csv():
    """Export current results as CSV"""

    if not st.session_state.get(
            'match_results') or not st.session_state.match_results.get(
            'matches'):
        st.error("No results to export.")
        return

    # Create DataFrame
    data = []
    for match in st.session_state.match_results['matches']:
        data.append({
            'Filename': match['filename'],
            'Resume_ID': match['resume_id'],
            'Similarity_Score': match['similarity_score'],
            'Experience_Match': match.get('experience_match', ''),
            'Matching_Skills': ', '.join(match.get('matching_skills', [])),
            'Match_Explanation': match['match_explanation']
        })

    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def export_history_json():
    """Export matching history as JSON"""
    import json

    if not st.session_state.get('matching_history'):
        st.error("No history to export.")
        return

    data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_searches': len(st.session_state.matching_history),
        'history': st.session_state.matching_history
    }

    json_str = json.dumps(data, indent=2, default=str)

    st.download_button(
        label="📥 Download History JSON",
        data=json_str,
        file_name=f"matching_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def generate_analytics_report():
    """Generate comprehensive analytics report"""

    st.success("📊 Analytics report generated! (Feature coming soon)")
    st.info(
        "This feature will generate a comprehensive PDF report with all analytics, insights, and recommendations.")


if __name__ == "__main__":
    render_results_page()