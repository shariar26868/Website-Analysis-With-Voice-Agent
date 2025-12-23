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


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Add +1 if not present (assuming US)
    if not digits.startswith('1') and len(digits) == 10:
        digits = '1' + digits
    
    return '+' + digits


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