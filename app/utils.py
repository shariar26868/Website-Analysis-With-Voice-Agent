
"""
Utility Functions and Helpers
"""
import re
import validators
from typing import Optional
from datetime import datetime


def validate_url(url: str) -> bool:
    """Validate URL format"""
    return validators.url(url)


def validate_phone(phone: str) -> bool:
    """Validate phone number (basic US format)"""
    pattern = r'^\+?1?\d{10,15}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))


def normalize_phone(phone: str, country_code: str = "880") -> str:
    """
    Normalize phone number to E.164 format
    
    Args:
        phone: Phone number in any format
        country_code: Default country code (880 for Bangladesh, 1 for USA)
    
    Returns:
        E.164 formatted phone number (e.g., +8801712345678)
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If already starts with country code, return with +
    if digits.startswith(country_code):
        return '+' + digits
    
    # If starts with 0 (local format), remove it and add country code
    if digits.startswith('0'):
        digits = digits[1:]
    
    # Check if it's US number (10 digits)
    if len(digits) == 10 and country_code == "1":
        return '+1' + digits
    
    # Add country code
    return '+' + country_code + digits


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format"""
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def calculate_overall_score(ai_score: int, seo_score: int) -> int:
    """Calculate overall score from AI and SEO scores"""
    # Weighted average: AI visibility 60%, SEO 40%
    return int((ai_score * 0.6) + (seo_score * 0.4))


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc or parsed.path


def sanitize_text(text: str) -> str:
    """Sanitize text for safe storage"""
    # Remove potential script tags and dangerous content
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    return text.strip()


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat() if dt else None


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return None


class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def info(message: str, **kwargs):
        timestamp = datetime.utcnow().isoformat()
        print(f"[INFO] {timestamp} - {message}", kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        timestamp = datetime.utcnow().isoformat()
        print(f"[ERROR] {timestamp} - {message}", kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        timestamp = datetime.utcnow().isoformat()
        print(f"[WARNING] {timestamp} - {message}", kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs):
        timestamp = datetime.utcnow().isoformat()
        print(f"[DEBUG] {timestamp} - {message}", kwargs)


# Initialize logger
logger = Logger()


def serialize_for_mongodb(data: dict) -> dict:
    """
    Convert Pydantic models to MongoDB-compatible dict
    Handles URL objects and nested structures
    """
    result = {}
    for key, value in data.items():
        # Check if it's a Pydantic URL by type name (not isinstance)
        if hasattr(value, '__class__') and 'Url' in value.__class__.__name__:
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = serialize_for_mongodb(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_for_mongodb(item) if isinstance(item, dict) 
                else str(item) if hasattr(item, '__class__') and 'Url' in item.__class__.__name__
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result



