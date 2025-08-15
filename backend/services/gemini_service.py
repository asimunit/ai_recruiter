"""
Gemini LLM service for generating match explanations
"""
import google.generativeai as genai
from typing import List, Dict, Optional
from config.settings import settings
import logging
import time

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini LLM"""

    def __init__(self):
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Gemini model"""
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required")

            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)

            # Initialize model
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

            # Test the model
            test_response = self.model.generate_content(
                "Hello, test connection")

            logger.info(
                f"✅ Gemini model {settings.GEMINI_MODEL} initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini model: {str(e)}")
            raise RuntimeError(f"Could not initialize Gemini model: {str(e)}")

    def generate_match_explanation(
            self,
            job_description: str,
            resume_content: str,
            similarity_score: float,
            matching_skills: List[str] = None
    ) -> str:
        """
        Generate explanation for why a resume matches a job description

        Args:
            job_description (str): Job description text
            resume_content (str): Resume content
            similarity_score (float): Similarity score (0-1)
            matching_skills (List[str]): List of matching skills

        Returns:
            str: Generated explanation
        """
        try:
            # Prepare the prompt
            prompt = self._create_match_explanation_prompt(
                job_description,
                resume_content,
                similarity_score,
                matching_skills
            )

            # Generate response
            response = self.model.generate_content(prompt)

            if response.text:
                explanation = response.text.strip()
                logger.info("Generated match explanation successfully")
                return explanation
            else:
                logger.warning("Empty response from Gemini")
                return self._fallback_explanation(similarity_score,
                                                  matching_skills)

        except Exception as e:
            logger.error(f"Failed to generate match explanation: {str(e)}")
            return self._fallback_explanation(similarity_score,
                                              matching_skills)

    def _create_match_explanation_prompt(
            self,
            job_description: str,
            resume_content: str,
            similarity_score: float,
            matching_skills: List[str] = None
    ) -> str:
        """Create a prompt for match explanation"""

        skills_text = ""
        if matching_skills:
            skills_text = f"\nMatching Skills Found: {', '.join(matching_skills)}"

        prompt = f"""
You are an AI recruitment assistant. Analyze the following job description and resume, then provide a concise explanation of why they match.

JOB DESCRIPTION:
{job_description[:1500]}

RESUME CONTENT:
{resume_content[:2000]}

SIMILARITY SCORE: {similarity_score:.2f}{skills_text}

Please provide a brief, professional explanation (2-3 sentences) covering:
1. Key matching qualifications or skills
2. Relevant experience alignment
3. Why this candidate would be a good fit

Keep the explanation concise, specific, and professional. Focus on the most relevant matches.
"""
        return prompt

    def generate_batch_explanations(
            self,
            job_description: str,
            resume_matches: List[Dict]
    ) -> List[str]:
        """
        Generate explanations for multiple resume matches

        Args:
            job_description (str): Job description text
            resume_matches (List[Dict]): List of resume match data

        Returns:
            List[str]: List of generated explanations
        """
        explanations = []

        for match in resume_matches:
            try:
                explanation = self.generate_match_explanation(
                    job_description,
                    match.get('resume_content', ''),
                    match.get('similarity_score', 0.0),
                    match.get('matching_skills', [])
                )
                explanations.append(explanation)

                # Add small delay to avoid rate limiting
                time.sleep(0.1)

            except Exception as e:
                logger.error(
                    f"Failed to generate explanation for match: {str(e)}")
                explanations.append(
                    self._fallback_explanation(
                        match.get('similarity_score', 0.0),
                        match.get('matching_skills', [])
                    )
                )

        return explanations

    def _fallback_explanation(self, similarity_score: float,
                              matching_skills: List[str] = None) -> str:
        """Generate a fallback explanation when Gemini fails"""

        score_text = f"This candidate shows a {similarity_score:.1%} match"

        if matching_skills and len(matching_skills) > 0:
            skills_text = f" with relevant skills including {', '.join(matching_skills[:3])}"
            if len(matching_skills) > 3:
                skills_text += f" and {len(matching_skills) - 3} others"
        else:
            skills_text = " based on overall profile alignment"

        explanation = f"{score_text}{skills_text}. Review full resume for detailed qualifications."

        return explanation

    def generate_job_analysis(self, job_description: str) -> Dict[str, any]:
        """
        Analyze a job description to extract key requirements

        Args:
            job_description (str): Job description text

        Returns:
            Dict: Analyzed job requirements
        """
        try:
            prompt = f"""
Analyze the following job description and extract key information in a structured format:

JOB DESCRIPTION:
{job_description}

Please extract and return:
1. Required technical skills (comma-separated list)
2. Years of experience required (number or range)
3. Education requirements
4. Key responsibilities (top 3)
5. Nice-to-have skills (comma-separated list)

Format your response as:
REQUIRED_SKILLS: [list]
EXPERIENCE: [years]
EDUCATION: [requirements]
RESPONSIBILITIES: [top 3]
NICE_TO_HAVE: [list]
"""

            response = self.model.generate_content(prompt)

            if response.text:
                return self._parse_job_analysis(response.text)
            else:
                return self._default_job_analysis()

        except Exception as e:
            logger.error(f"Failed to analyze job description: {str(e)}")
            return self._default_job_analysis()

    def _parse_job_analysis(self, response_text: str) -> Dict[str, any]:
        """Parse the job analysis response"""
        try:
            analysis = {
                'required_skills': [],
                'experience_years': None,
                'education': '',
                'responsibilities': [],
                'nice_to_have': []
            }

            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('REQUIRED_SKILLS:'):
                    skills = line.replace('REQUIRED_SKILLS:', '').strip()
                    analysis['required_skills'] = [s.strip() for s in
                                                   skills.split(',') if
                                                   s.strip()]
                elif line.startswith('EXPERIENCE:'):
                    exp = line.replace('EXPERIENCE:', '').strip()
                    analysis['experience_years'] = exp
                elif line.startswith('EDUCATION:'):
                    analysis['education'] = line.replace('EDUCATION:',
                                                         '').strip()
                elif line.startswith('RESPONSIBILITIES:'):
                    resp = line.replace('RESPONSIBILITIES:', '').strip()
                    analysis['responsibilities'] = [r.strip() for r in
                                                    resp.split(',') if
                                                    r.strip()]
                elif line.startswith('NICE_TO_HAVE:'):
                    nth = line.replace('NICE_TO_HAVE:', '').strip()
                    analysis['nice_to_have'] = [s.strip() for s in
                                                nth.split(',') if s.strip()]

            return analysis

        except Exception as e:
            logger.error(f"Failed to parse job analysis: {str(e)}")
            return self._default_job_analysis()

    def _default_job_analysis(self) -> Dict[str, any]:
        """Return default job analysis structure"""
        return {
            'required_skills': [],
            'experience_years': None,
            'education': '',
            'responsibilities': [],
            'nice_to_have': []
        }

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the Gemini model"""
        return {
            'model_name': settings.GEMINI_MODEL,
            'status': 'initialized' if self.model else 'not_initialized',
            'api_key_configured': bool(settings.GEMINI_API_KEY)
        }


# Global Gemini service instance
gemini_service = GeminiService()


def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance"""
    return gemini_service