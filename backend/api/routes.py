"""
FastAPI routes for AI Recruitr backend
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import aiofiles
import os
import time
from pathlib import Path

from backend.models.schemas import (
    JobDescription, MatchRequest, MatchResponse, MatchResult,
    EmbeddingRequest, EmbeddingResponse, StatusResponse, ErrorResponse,
    ParsedResume
)
from backend.services.resume_parser import get_resume_parser
from backend.services.embedding_service import get_embedding_service
from backend.services.faiss_service import get_faiss_service
from backend.services.gemini_service import get_gemini_service
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Get service instances
resume_parser = get_resume_parser()
embedding_service = get_embedding_service()
faiss_service = get_faiss_service()
gemini_service = get_gemini_service()


@router.get("/", response_model=StatusResponse)
async def get_status():
    """Get API status and information"""
    try:
        return StatusResponse(
            status="healthy",
            version="1.0.0",
            total_resumes=faiss_service.get_total_vectors(),
            embedding_model=settings.EMBEDDING_MODEL,
            llm_model=settings.GEMINI_MODEL
        )
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unavailable")


@router.post("/upload-resume", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    """Upload and process a resume file"""

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Check file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )

    try:
        # Save uploaded file
        file_path = settings.RESUMES_DIR / file.filename

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Parse resume
        parsed_resume = resume_parser.parse_resume(str(file_path),
                                                   file.filename)

        # Generate embedding
        embedding = embedding_service.generate_embedding(
            parsed_resume['raw_content'])

        # Add to FAISS index
        faiss_service.add_vector(
            resume_id=parsed_resume['id'],
            embedding=embedding,
            resume_data=parsed_resume
        )

        # Mark embedding as generated
        parsed_resume['embedding_generated'] = True

        # Clean up temporary file
        try:
            os.remove(file_path)
        except:
            pass

        logger.info(f"Successfully processed resume: {file.filename}")

        return {
            "message": "Resume uploaded and processed successfully",
            "resume_id": parsed_resume['id'],
            "filename": file.filename,
            "skills_found": len(parsed_resume['skills']),
            "sections_found": len(parsed_resume['sections'])
        }

    except Exception as e:
        logger.error(f"Resume upload failed: {str(e)}")

        # Clean up file if exists
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        raise HTTPException(status_code=500,
                            detail=f"Failed to process resume: {str(e)}")


@router.post("/match-job", response_model=MatchResponse)
async def match_job_to_resumes(request: MatchRequest):
    """Match a job description to resumes in the database"""

    start_time = time.time()

    try:
        job_desc = request.job_description

        # Combine job description text
        job_text = f"{job_desc.title}\n{job_desc.description}"
        if job_desc.requirements:
            job_text += f"\n{job_desc.requirements}"

        # Generate embedding for job description
        job_embedding = embedding_service.generate_embedding(job_text)

        # Search for similar resumes
        search_results = faiss_service.search(
            query_embedding=job_embedding,
            top_k=request.top_k,
            threshold=request.similarity_threshold
        )

        if not search_results:
            return MatchResponse(
                job_title=job_desc.title,
                total_resumes=faiss_service.get_total_vectors(),
                matches_found=0,
                matches=[],
                processing_time=time.time() - start_time
            )

        # Generate match explanations using Gemini
        matches = []
        for result in search_results:
            try:
                # Get resume content from sections
                resume_content = ""
                if 'sections' in result and isinstance(result['sections'],
                                                       dict):
                    resume_content = " ".join(result['sections'].values())

                # Generate explanation
                explanation = gemini_service.generate_match_explanation(
                    job_description=job_text,
                    resume_content=resume_content,
                    similarity_score=result['similarity_score'],
                    matching_skills=result.get('skills', [])
                )

                # Find matching skills
                job_skills = set(
                    skill.lower() for skill in job_desc.skills_required)
                resume_skills = set(
                    skill.lower() for skill in result.get('skills', []))
                matching_skills = list(job_skills.intersection(resume_skills))

                match_result = MatchResult(
                    resume_id=result['resume_id'],
                    filename=result.get('filename', 'Unknown'),
                    similarity_score=result['similarity_score'],
                    match_explanation=explanation,
                    matching_skills=matching_skills,
                    experience_match=str(
                        result.get('experience_years', 'Not specified'))
                )

                matches.append(match_result)

            except Exception as e:
                logger.error(f"Error processing match result: {str(e)}")
                continue

        processing_time = time.time() - start_time

        logger.info(
            f"Job matching completed: {len(matches)} matches found in {processing_time:.2f}s")

        return MatchResponse(
            job_title=job_desc.title,
            total_resumes=faiss_service.get_total_vectors(),
            matches_found=len(matches),
            matches=matches,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Job matching failed: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Matching failed: {str(e)}")


@router.post("/generate-embedding", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """Generate embedding for given text"""

    try:
        embedding = embedding_service.generate_embedding(request.text)

        return EmbeddingResponse(
            embedding=embedding.tolist(),
            dimension=len(embedding)
        )

    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Failed to generate embedding: {str(e)}")


@router.get("/resumes/count")
async def get_resume_count():
    """Get total number of resumes in the database"""

    try:
        count = faiss_service.get_total_vectors()
        return {"total_resumes": count}

    except Exception as e:
        logger.error(f"Failed to get resume count: {str(e)}")
        raise HTTPException(status_code=500,
                            detail="Failed to get resume count")


@router.get("/index/info")
async def get_index_info():
    """Get information about the FAISS index"""

    try:
        index_info = faiss_service.get_index_info()
        embedding_info = embedding_service.get_model_info()
        gemini_info = gemini_service.get_model_info()

        return {
            "faiss_index": index_info,
            "embedding_model": embedding_info,
            "llm_model": gemini_info
        }

    except Exception as e:
        logger.error(f"Failed to get index info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get index info")


@router.post("/index/rebuild")
async def rebuild_index():
    """Rebuild the FAISS index (admin function)"""

    try:
        faiss_service.rebuild_index()
        return {"message": "Index rebuilt successfully"}

    except Exception as e:
        logger.error(f"Failed to rebuild index: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Failed to rebuild index: {str(e)}")


@router.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete a resume from the database"""

    try:
        # Note: FAISS doesn't support direct deletion, would need index rebuild
        success = faiss_service.delete_vector(resume_id)

        if success:
            return {"message": f"Resume {resume_id} deleted successfully"}
        else:
            return {
                "message": f"Resume {resume_id} not found or deletion not supported"}

    except Exception as e:
        logger.error(f"Failed to delete resume: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Failed to delete resume: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""

    try:
        # Basic health checks
        checks = {
            "embedding_service": embedding_service.get_model_info()[
                                     "status"] == "loaded",
            "faiss_service": faiss_service.get_total_vectors() >= 0,
            "gemini_service": gemini_service.get_model_info()[
                                  "status"] == "initialized"
        }

        all_healthy = all(checks.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }


# Error handlers
# @router.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     """Handle HTTP exceptions"""
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"error": exc.detail, "status_code": exc.status_code}
#     )
#
#
# @router.exception_handler(Exception)
# async def general_exception_handler(request, exc):
#     """Handle general exceptions"""
#     logger.error(f"Unhandled exception: {str(exc)}")
#     return JSONResponse(
#         status_code=500,
#         content={"error": "Internal server error", "detail": str(exc)}
#     )