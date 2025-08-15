"""
Resume parsing service for extracting text and structured data from resumes
"""
import fitz  # PyMuPDF
from docx import Document
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ResumeParser:
    """Service for parsing resumes and extracting structured information"""

    def __init__(self):
        self.skills_patterns = self._load_skills_patterns()
        self.section_patterns = self._load_section_patterns()

    def parse_resume(self, file_path: str, filename: str) -> Dict:
        """
        Parse a resume file and extract structured information

        Args:
            file_path (str): Path to the resume file
            filename (str): Original filename

        Returns:
            Dict: Parsed resume data
        """
        try:
            # Extract raw text based on file type
            raw_text = self._extract_text(file_path, filename)

            if not raw_text.strip():
                raise ValueError("No text content found in the resume")

            # Generate unique ID for this resume
            resume_id = str(uuid.uuid4())

            # Extract structured information
            contact_info = self._extract_contact_info(raw_text)
            sections = self._extract_sections(raw_text)
            skills = self._extract_skills(raw_text)
            experience_years = self._extract_experience_years(raw_text)
            education = self._extract_education(raw_text)
            certifications = self._extract_certifications(raw_text)
            languages = self._extract_languages(raw_text)

            # Create structured resume data
            parsed_resume = {
                'id': resume_id,
                'filename': filename,
                'raw_content': raw_text,
                'contact_info': contact_info,
                'sections': sections,
                'skills': skills,
                'experience_years': experience_years,
                'education': education,
                'certifications': certifications,
                'languages': languages,
                'created_at': datetime.now(),
                'embedding_generated': False
            }

            logger.info(f"Successfully parsed resume: {filename}")
            return parsed_resume

        except Exception as e:
            logger.error(f"Failed to parse resume {filename}: {str(e)}")
            raise RuntimeError(f"Could not parse resume: {str(e)}")

    def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from different file formats"""

        file_extension = Path(filename).suffix.lower()

        try:
            if file_extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_extension == '.docx':
                return self._extract_docx_text(file_path)
            elif file_extension == '.txt':
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {str(e)}")
            raise

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""

            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text()
                text += "\n"

            doc.close()
            return text.strip()

        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise RuntimeError(f"Could not extract text from PDF: {str(e)}")

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""

            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            raise RuntimeError(f"Could not extract text from DOCX: {str(e)}")

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8',
                      errors='ignore') as file:
                return file.read().strip()

        except Exception as e:
            logger.error(f"TXT extraction failed: {str(e)}")
            raise RuntimeError(f"Could not extract text from TXT: {str(e)}")

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text"""
        contact_info = {}

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]

        # Phone pattern
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0]) if isinstance(phones[0],
                                                                     tuple) else \
            phones[0]

        # LinkedIn profile
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info['linkedin'] = linkedin.group()

        return contact_info

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from resume"""
        sections = {}

        for section_name, patterns in self.section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    # Get text after the section header until next section or end
                    start_pos = match.end()
                    next_section = self._find_next_section(text, start_pos)

                    if next_section:
                        section_text = text[start_pos:next_section].strip()
                    else:
                        section_text = text[start_pos:].strip()

                    sections[section_name] = section_text[
                                             :1000]  # Limit section length
                    break

        return sections

    def _find_next_section(self, text: str, start_pos: int) -> Optional[int]:
        """Find the start position of the next section"""
        all_patterns = []
        for patterns in self.section_patterns.values():
            all_patterns.extend(patterns)

        next_positions = []
        for pattern in all_patterns:
            match = re.search(pattern, text[start_pos:], re.IGNORECASE)
            if match:
                next_positions.append(start_pos + match.start())

        return min(next_positions) if next_positions else None

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        found_skills = []
        text_lower = text.lower()

        for skill_category, skills in self.skills_patterns.items():
            for skill in skills:
                # Look for exact skill matches (case-insensitive)
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b',
                             text_lower):
                    found_skills.append(skill)

        # Remove duplicates and sort
        return sorted(list(set(found_skills)))

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience from resume"""
        # Look for patterns like "5 years experience", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return max([int(match) for match in matches])
                except ValueError:
                    continue

        return None

    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []

        # Common degree patterns
        degree_patterns = [
            r'(Bachelor\'?s?\s+(?:of\s+)?(?:Science|Arts|Engineering|Business|Computer Science))',
            r'(Master\'?s?\s+(?:of\s+)?(?:Science|Arts|Engineering|Business|Computer Science))',
            r'(PhD|Ph\.D\.?|Doctor\s+of\s+Philosophy)',
            r'(MBA|Master\s+of\s+Business\s+Administration)',
            r'(B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?)',
        ]

        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)

        return list(set(education))

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume"""
        cert_patterns = [
            r'(AWS\s+Certified\s+[\w\s]+)',
            r'(Microsoft\s+Certified\s+[\w\s]+)',
            r'(Google\s+Cloud\s+Certified\s+[\w\s]+)',
            r'(Cisco\s+Certified\s+[\w\s]+)',
            r'(Oracle\s+Certified\s+[\w\s]+)',
            r'(PMP|Project\s+Management\s+Professional)',
            r'(CISSP|Certified\s+Information\s+Systems\s+Security\s+Professional)',
            r'(CompTIA\s+[\w\s]+)',
        ]

        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)

        return list(set(certifications))

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from resume"""
        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Hindi', 'Arabic', 'Russian',
            'Dutch', 'Swedish', 'Norwegian', 'Danish', 'Finnish'
        ]

        found_languages = []
        text_lower = text.lower()

        for lang in common_languages:
            if re.search(r'\b' + re.escape(lang.lower()) + r'\b', text_lower):
                found_languages.append(lang)

        return found_languages

    def _load_skills_patterns(self) -> Dict[str, List[str]]:
        """Load common skills patterns for extraction"""
        return {
            'programming': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#',
                'Go', 'Rust',
                'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL'
            ],
            'web_technologies': [
                'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js',
                'Express',
                'Django', 'Flask', 'Spring', 'ASP.NET', 'Ruby on Rails'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle',
                'SQL Server', 'Cassandra', 'DynamoDB', 'Elasticsearch'
            ],
            'cloud_platforms': [
                'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
                'Jenkins',
                'GitLab', 'GitHub Actions', 'Terraform', 'Ansible'
            ],
            'data_science': [
                'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
                'Pandas',
                'NumPy', 'Scikit-learn', 'Jupyter', 'Data Analysis',
                'Statistics'
            ],
            'tools': [
                'Git', 'Jira', 'Confluence', 'Slack', 'Trello', 'Agile',
                'Scrum',
                'Linux', 'Windows', 'macOS', 'VS Code', 'IntelliJ'
            ]
        }

    def _load_section_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying resume sections"""
        return {
            'experience': [
                r'(?:work\s+)?experience:?',
                r'professional\s+experience:?',
                r'employment\s+history:?',
                r'career\s+history:?'
            ],
            'education': [
                r'education:?',
                r'academic\s+background:?',
                r'qualifications:?'
            ],
            'skills': [
                r'(?:technical\s+)?skills:?',
                r'competencies:?',
                r'technologies:?',
                r'expertise:?'
            ],
            'summary': [
                r'(?:professional\s+)?summary:?',
                r'profile:?',
                r'objective:?',
                r'about\s+me:?'
            ],
            'projects': [
                r'projects:?',
                r'key\s+projects:?',
                r'notable\s+projects:?'
            ],
            'certifications': [
                r'certifications:?',
                r'certificates:?',
                r'professional\s+certifications:?'
            ]
        }


# Global resume parser instance
resume_parser = ResumeParser()


def get_resume_parser() -> ResumeParser:
    """Get the global resume parser instance"""
    return resume_parser