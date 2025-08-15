"""
Utility helper functions for AI Recruitr
"""
import os
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration

    Args:
        log_level (str): Logging level
        log_file (Optional[str]): Log file path
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def ensure_directories(directories: List[Union[str, Path]]):
    """
    Ensure directories exist, create if they don't

    Args:
        directories (List[Union[str, Path]]): List of directory paths
    """
    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {str(e)}")
            raise


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate if file has allowed extension

    Args:
        filename (str): Name of the file
        allowed_extensions (List[str]): List of allowed extensions

    Returns:
        bool: True if valid, False otherwise
    """
    if not filename:
        return False

    file_extension = Path(filename).suffix.lower()
    return file_extension in [ext.lower() for ext in allowed_extensions]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Remove leading/trailing underscores and spaces
    sanitized = sanitized.strip('_ ')

    # Ensure filename is not empty
    if not sanitized:
        sanitized = f"file_{int(time.time())}"

    return sanitized


def calculate_file_hash(file_content: bytes) -> str:
    """
    Calculate SHA256 hash of file content

    Args:
        file_content (bytes): File content as bytes

    Returns:
        str: SHA256 hash hex digest
    """
    return hashlib.sha256(file_content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing

    Args:
        text (str): Raw text

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)

    # Normalize quotes
    text = re.sub(r'[“”]', '"',
                  text)  # Replace curly double quotes with straight double quotes
    text = re.sub(r"[‘’]", "'",
                  text)  # Replace curly single quotes with straight single quotes

    return text


def extract_skills_from_text(text: str, skill_keywords: List[str]) -> List[
    str]:
    """
    Extract skills from text based on keyword matching

    Args:
        text (str): Text to search for skills
        skill_keywords (List[str]): List of skill keywords

    Returns:
        List[str]: Found skills
    """
    found_skills = []
    text_lower = text.lower()

    for skill in skill_keywords:
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return list(set(found_skills))  # Remove duplicates


def extract_years_of_experience(text: str) -> Optional[int]:
    """
    Extract years of experience from text using regex patterns

    Args:
        text (str): Text to search

    Returns:
        Optional[int]: Years of experience or None
    """
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
        r'over\s*(\d+)\s*years?',
        r'more\s*than\s*(\d+)\s*years?',
        r'(\d+)\+\s*years?'
    ]

    max_years = 0

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                years = int(match)
                max_years = max(max_years, years)
            except ValueError:
                continue

    return max_years if max_years > 0 else None


def parse_contact_info(text: str) -> Dict[str, str]:
    """
    Parse contact information from text

    Args:
        text (str): Text to parse

    Returns:
        Dict[str, str]: Contact information
    """
    contact_info = {}

    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]

    # Phone number (multiple patterns)
    phone_patterns = [
        r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
        # International
    ]

    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            # Clean up phone number
            phone = re.sub(r'[^\d+]', '', phones[0])
            contact_info['phone'] = phone
            break

    # LinkedIn
    linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9\-]+)'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = f"linkedin.com/in/{linkedin_match.group(1)}"

    # GitHub
    github_pattern = r'(?:github\.com/)([A-Za-z0-9\-]+)'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = f"github.com/{github_match.group(1)}"

    return contact_info


def normalize_similarity_score(score: float) -> float:
    """
    Normalize similarity score to 0-1 range

    Args:
        score (float): Raw similarity score

    Returns:
        float: Normalized score between 0 and 1
    """
    return max(0.0, min(1.0, float(score)))


def format_processing_time(seconds: float) -> str:
    """
    Format processing time in human readable format

    Args:
        seconds (float): Time in seconds

    Returns:
        str: Formatted time string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def save_json_file(data: Any, file_path: Union[str, Path]) -> bool:
    """
    Save data to JSON file

    Args:
        data (Any): Data to save
        file_path (Union[str, Path]): Path to save file

    Returns:
        bool: Success status
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"JSON file saved: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {str(e)}")
        return False


def load_json_file(file_path: Union[str, Path]) -> Optional[Any]:
    """
    Load data from JSON file

    Args:
        file_path (Union[str, Path]): Path to JSON file

    Returns:
        Optional[Any]: Loaded data or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"JSON file loaded: {file_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {str(e)}")
        return None


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format

    Returns:
        str: Current timestamp
    """
    return datetime.now().isoformat()


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email (str): Email to validate

    Returns:
        bool: True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def batch_process(items: List[Any], batch_size: int = 10, delay: float = 0.1):
    """
    Process items in batches with optional delay

    Args:
        items (List[Any]): Items to process
        batch_size (int): Size of each batch
        delay (float): Delay between batches in seconds

    Yields:
        List[Any]: Batch of items
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield batch

        if delay > 0 and i + batch_size < len(items):
            time.sleep(delay)


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Merge two dictionaries recursively

    Args:
        dict1 (Dict): First dictionary
        dict2 (Dict): Second dictionary

    Returns:
        Dict: Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(
                value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def calculate_similarity_stats(similarities: List[float]) -> Dict[str, float]:
    """
    Calculate statistics for similarity scores

    Args:
        similarities (List[float]): List of similarity scores

    Returns:
        Dict[str, float]: Statistics dictionary
    """
    if not similarities:
        return {
            'min': 0.0,
            'max': 0.0,
            'mean': 0.0,
            'median': 0.0,
            'std': 0.0,
            'count': 0
        }

    similarities = sorted(similarities)
    n = len(similarities)

    stats = {
        'min': similarities[0],
        'max': similarities[-1],
        'mean': sum(similarities) / n,
        'median': similarities[n // 2] if n % 2 == 1 else (similarities[
                                                               n // 2 - 1] +
                                                           similarities[
                                                               n // 2]) / 2,
        'count': n
    }

    # Calculate standard deviation
    if n > 1:
        variance = sum((x - stats['mean']) ** 2 for x in similarities) / (
                    n - 1)
        stats['std'] = variance ** 0.5
    else:
        stats['std'] = 0.0

    return stats


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format float as percentage string

    Args:
        value (float): Value between 0 and 1
        decimals (int): Number of decimal places

    Returns:
        str: Formatted percentage
    """
    return f"{value * 100:.{decimals}f}%"


# Specialized helper functions for AI Recruitr

def extract_education_level(text: str) -> List[str]:
    """
    Extract education levels from resume text

    Args:
        text (str): Resume text

    Returns:
        List[str]: Found education levels
    """
    education_patterns = {
        'PhD': [r'ph\.?d\.?', r'doctor\s+of\s+philosophy', r'doctorate'],
        'Masters': [r'master\'?s?', r'm\.?s\.?', r'm\.?a\.?', r'mba'],
        'Bachelors': [r'bachelor\'?s?', r'b\.?s\.?', r'b\.?a\.?',
                      r'b\.?sc\.?'],
        'Associates': [r'associate\'?s?', r'a\.?s\.?', r'a\.?a\.?'],
        'High School': [r'high\s+school', r'secondary\s+school', r'diploma']
    }

    found_levels = []
    text_lower = text.lower()

    for level, patterns in education_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found_levels.append(level)
                break

    return found_levels


def extract_certifications(text: str) -> List[str]:
    """
    Extract certifications from resume text

    Args:
        text (str): Resume text

    Returns:
        List[str]: Found certifications
    """
    cert_patterns = [
        r'aws\s+certified\s+[\w\s]+',
        r'microsoft\s+certified\s+[\w\s]+',
        r'google\s+cloud\s+certified\s+[\w\s]+',
        r'cisco\s+certified\s+[\w\s]+',
        r'oracle\s+certified\s+[\w\s]+',
        r'pmp|project\s+management\s+professional',
        r'cissp',
        r'comptia\s+[\w\s]+',
        r'certified\s+[\w\s]+\s+professional',
        r'[\w\s]*\s+certification'
    ]

    certifications = []

    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        certifications.extend(matches)

    # Clean and deduplicate
    cleaned_certs = []
    for cert in certifications:
        cert = cert.strip()
        if cert and len(cert) > 3:  # Filter out very short matches
            cleaned_certs.append(cert.title())

    return list(set(cleaned_certs))