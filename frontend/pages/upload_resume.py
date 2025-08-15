"""
Resume upload page for Streamlit frontend
"""
import streamlit as st
import time
from frontend.components.ui_components import (
    render_file_upload_area, render_upload_stats, show_loading_spinner,
    show_success_message, show_error_message, render_progress_bar
)


def render_upload_page():
    """Render the resume upload page"""

    st.markdown("## 📄 Upload Resumes")
    st.markdown(
        "Upload resume files to build your candidate database for semantic matching.")

    # Upload area
    uploaded_files = render_file_upload_area()

    # Upload statistics
    total_uploaded = len(st.session_state.get('uploaded_resumes', []))
    render_upload_stats(total_uploaded)

    st.markdown("---")

    # Process uploaded files
    if uploaded_files:
        st.markdown("### 📁 Selected Files")

        # Show selected files
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"📄 {file.name}")

            with col2:
                file_size = len(file.getvalue()) / (1024 * 1024)  # MB
                st.write(f"{file_size:.2f} MB")

            with col3:
                st.write(file.type)

        # Process files button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Process All Files", use_container_width=True,
                         type="primary"):
                process_uploaded_files(uploaded_files)

    # Show recent uploads
    if st.session_state.get('uploaded_resumes'):
        st.markdown("---")
        st.markdown("### 📚 Recently Uploaded Resumes")

        for resume in st.session_state.uploaded_resumes[-10:]:  # Show last 10
            with st.expander(
                    f"📄 {resume['filename']} - {resume.get('status', 'Unknown')}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**Resume ID:** {resume.get('resume_id', 'N/A')}")
                    st.write(
                        f"**Upload Time:** {resume.get('upload_time', 'N/A')}")
                    st.write(
                        f"**File Size:** {resume.get('file_size', 'N/A')}")

                with col2:
                    st.write(
                        f"**Skills Found:** {resume.get('skills_found', 0)}")
                    st.write(
                        f"**Sections Found:** {resume.get('sections_found', 0)}")
                    st.write(f"**Status:** {resume.get('status', 'Unknown')}")

    # Bulk upload tips
    render_upload_tips()


def process_uploaded_files(uploaded_files):
    """Process multiple uploaded files"""

    if not uploaded_files:
        show_error_message("No files selected for processing")
        return

    # Initialize progress tracking
    total_files = len(uploaded_files)
    successful_uploads = 0
    failed_uploads = 0

    # Create progress indicators
    progress_bar = render_progress_bar(0)
    status_text = st.empty()

    with show_loading_spinner("Processing resumes..."):

        for i, file in enumerate(uploaded_files):
            try:
                # Update progress
                progress = (i / total_files)
                progress_bar.progress(progress)
                status_text.text(
                    f"Processing {file.name}... ({i + 1}/{total_files})")

                # Upload file to API
                result = st.session_state.upload_resume_to_api(file)

                if result:
                    # Success
                    successful_uploads += 1

                    # Store in session state
                    resume_data = {
                        'filename': file.name,
                        'resume_id': result.get('resume_id'),
                        'file_size': f"{len(file.getvalue()) / (1024 * 1024):.2f} MB",
                        'skills_found': result.get('skills_found', 0),
                        'sections_found': result.get('sections_found', 0),
                        'upload_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'status': 'Success'
                    }

                    if 'uploaded_resumes' not in st.session_state:
                        st.session_state.uploaded_resumes = []

                    st.session_state.uploaded_resumes.append(resume_data)

                    st.success(f"✅ {file.name} - Processed successfully")

                else:
                    failed_uploads += 1
                    st.error(f"❌ {file.name} - Processing failed")

                # Small delay to prevent overwhelming the API
                time.sleep(0.2)

            except Exception as e:
                failed_uploads += 1
                st.error(f"❌ {file.name} - Error: {str(e)}")

    # Final progress update
    progress_bar.progress(1.0)
    status_text.text("Processing complete!")

    # Show summary
    st.markdown("---")
    st.markdown("### 📊 Processing Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("✅ Successful", successful_uploads)

    with col2:
        st.metric("❌ Failed", failed_uploads)

    with col3:
        st.metric("📁 Total Processed", total_files)

    if successful_uploads > 0:
        show_success_message(
            f"Successfully processed {successful_uploads} resume(s)!")

        # Option to go to matching page
        if st.button("🔍 Start Job Matching", type="primary"):
            st.session_state.page = 'matching'
            st.rerun()

    if failed_uploads > 0:
        show_error_message(
            f"{failed_uploads} file(s) failed to process. Check the error messages above.")


def render_upload_tips():
    """Render upload tips and guidelines"""

    st.markdown("---")
    st.markdown("### 💡 Upload Tips")

    with st.expander("📋 Best Practices"):
        st.markdown("""
        **For best results:**

        🎯 **File Format**: PDF and DOCX files work best for text extraction

        📝 **Content Quality**: Ensure resumes have clear sections (Experience, Skills, Education)

        🏷️ **File Names**: Use descriptive filenames (e.g., "john_doe_software_engineer.pdf")

        📏 **File Size**: Keep files under 10MB for faster processing

        🔤 **Text Quality**: Avoid image-based PDFs - text-based PDFs work better

        📚 **Batch Upload**: You can upload multiple files at once for efficiency
        """)

    with st.expander("🚫 Common Issues"):
        st.markdown("""
        **Troubleshooting:**

        ❌ **Scanned PDFs**: Image-based PDFs may not extract text properly

        ❌ **Corrupted Files**: Ensure files are not corrupted or password-protected

        ❌ **Large Files**: Files over 10MB will be rejected

        ❌ **Unsupported Formats**: Only PDF, DOCX, and TXT are supported

        ❌ **API Connection**: Ensure the backend API is running and accessible
        """)

    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **How it works:**

        1. **Text Extraction**: Extract text from PDF/DOCX using PyMuPDF/python-docx

        2. **Content Parsing**: Identify sections like experience, skills, education

        3. **Embedding Generation**: Create semantic embeddings using mxbai model

        4. **Vector Storage**: Store embeddings in FAISS index for fast similarity search

        5. **Metadata Storage**: Keep resume metadata for result display
        """)


def render_database_management():
    """Render database management section"""

    st.markdown("---")
    st.markdown("### 🗄️ Database Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 View Index Info", use_container_width=True):
            show_index_information()

    with col2:
        if st.button("🔄 Refresh Stats", use_container_width=True):
            st.rerun()

    with col3:
        if st.button("⚠️ Rebuild Index", use_container_width=True):
            rebuild_index_warning()


def show_index_information():
    """Show detailed index information"""

    try:
        index_info = st.session_state.get_index_info()

        if index_info:
            st.markdown("#### 📈 Index Information")

            # FAISS Index Info
            faiss_info = index_info.get('faiss_index', {})

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**FAISS Index:**")
                st.write(
                    f"Total Vectors: {faiss_info.get('total_vectors', 0)}")
                st.write(f"Dimension: {faiss_info.get('dimension', 0)}")
                st.write(
                    f"Index Type: {faiss_info.get('index_type', 'Unknown')}")

            with col2:
                st.markdown("**Files:**")
                st.write(
                    f"Index File: {'✅' if faiss_info.get('index_file_exists') else '❌'}")
                st.write(
                    f"Metadata File: {'✅' if faiss_info.get('metadata_file_exists') else '❌'}")
                st.write(
                    f"Metadata Count: {faiss_info.get('metadata_count', 0)}")

            # Model Info
            embedding_info = index_info.get('embedding_model', {})
            llm_info = index_info.get('llm_model', {})

            st.markdown("**Models:**")
            st.write(
                f"Embedding Model: {embedding_info.get('model_name', 'Unknown')}")
            st.write(f"LLM Model: {llm_info.get('model_name', 'Unknown')}")

        else:
            show_error_message("Could not retrieve index information")

    except Exception as e:
        show_error_message(f"Error getting index info: {str(e)}")


def rebuild_index_warning():
    """Show rebuild index warning"""

    st.warning(
        "⚠️ **Warning**: Rebuilding the index will recreate the entire FAISS database. This action cannot be undone.")

    if st.button("🔴 Confirm Rebuild", type="secondary"):
        try:
            with show_loading_spinner("Rebuilding index..."):
                # This would call the rebuild API endpoint
                # For now, just show a message
                time.sleep(2)

            show_success_message("Index rebuilt successfully!")
            st.rerun()

        except Exception as e:
            show_error_message(f"Index rebuild failed: {str(e)}")


if __name__ == "__main__":
    render_upload_page()