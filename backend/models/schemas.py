"""
Pydantic models for AI Recruitr API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ResumeUpload(BaseModel):
    """Model for resume upload request"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")


class ResumeData(BaseModel):
    """Model for processed resume data"""
    id: str = Field(..., description="Unique resume ID")
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="Extracted text content")
    sections: Dict[str, str] = Field(default_factory=dict,
                                     description="Resume sections")
    skills: List[str] = Field(default_factory=list,
                              description="Extracted skills")
    experience_years: Optional[int] = Field(None,
                                            description="Years of experience")
    education: List[str] = Field(default_factory=list,
                                 description="Education details")
    created_at: datetime = Field(default_factory=datetime.now)


class JobDescription(BaseModel):
    """Model for job description input"""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Job description text")
    requirements: Optional[str] = Field(None, description="Job requirements")
    location: Optional[str] = Field(None, description="Job location")
    experience_level: Optional[str] = Field(None,
                                            description="Required experience level")
    skills_required: List[str] = Field(default_factory=list,
                                       description="Required skills")


class MatchResult(BaseModel):
    """Model for resume matching result"""
    resume_id: str = Field(..., description="Resume ID")
    filename: str = Field(..., description="Resume filename")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    match_explanation: str = Field(...,
                                   description="AI-generated match explanation")
    matching_skills: List[str] = Field(default_factory=list,
                                       description="Matching skills")
    experience_match: Optional[str] = Field(None,
                                            description="Experience level match")


class MatchRequest(BaseModel):
    """Model for matching request"""
    job_description: JobDescription = Field(...,
                                            description="Job description to match against")
    top_k: int = Field(default=10,
                       description="Number of top matches to return")
    similarity_threshold: float = Field(default=0.7,
                                        description="Minimum similarity threshold")


class MatchResponse(BaseModel):
    """Model for matching response"""
    job_title: str = Field(..., description="Job title")
    total_resumes: int = Field(..., description="Total resumes in database")
    matches_found: int = Field(..., description="Number of matches found")
    matches: List[MatchResult] = Field(...,
                                       description="List of matching resumes")
    processing_time: float = Field(...,
                                   description="Processing time in seconds")


class EmbeddingRequest(BaseModel):
    """Model for embedding generation request"""
    text: str = Field(..., description="Text to generate embeddings for")


class EmbeddingResponse(BaseModel):
    """Model for embedding response"""
    embedding: List[float] = Field(...,
                                   description="Generated embedding vector")
    dimension: int = Field(..., description="Embedding dimension")


class StatusResponse(BaseModel):
    """Model for API status response"""
    status: str = Field(..., description="API status")
    version: str = Field(default="1.0.0", description="API version")
    total_resumes: int = Field(..., description="Total resumes indexed")
    embedding_model: str = Field(..., description="Embedding model name")
    llm_model: str = Field(..., description="LLM model name")


class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None,
                                  description="Detailed error information")
    code: Optional[int] = Field(None, description="Error code")


class ResumeSection(BaseModel):
    """Model for resume sections"""
    section_type: str = Field(...,
                              description="Type of section (e.g., experience, education)")
    content: str = Field(..., description="Section content")
    key_points: List[str] = Field(default_factory=list,
                                  description="Key points extracted")


class ParsedResume(BaseModel):
    """Model for completely parsed resume"""
    id: str = Field(..., description="Unique resume ID")
    filename: str = Field(..., description="Original filename")
    raw_content: str = Field(..., description="Raw extracted text")
    sections: List[ResumeSection] = Field(..., description="Parsed sections")
    contact_info: Dict[str, Any] = Field(default_factory=dict,
                                         description="Contact information")
    skills: List[str] = Field(default_factory=list,
                              description="Extracted skills")
    experience_years: Optional[int] = Field(None,
                                            description="Years of experience")
    education: List[str] = Field(default_factory=list,
                                 description="Education details")
    certifications: List[str] = Field(default_factory=list,
                                      description="Certifications")
    languages: List[str] = Field(default_factory=list,
                                 description="Languages known")
    created_at: datetime = Field(default_factory=datetime.now)
    embedding_generated: bool = Field(default=False,
                                      description="Whether embedding is generated")