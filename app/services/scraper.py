"""
Website Scraping Service
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import re

from app.utils import logger


async def scrape_website(url: str) -> Dict[str, Any]:
    """
    Scrape website and extract key information
    
    Returns:
    - HTML content
    - Meta tags
    - Schema markup
    - Structured data
    - Page structure
    """
    try:
        logger.info(f"Scraping website: {url}")
        
        # Fetch website with timeout
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
            
            html_content = response.text
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract data
        scraped_data = {
            "success": True,
            "url": url,
            "title": extract_title(soup),
            "meta_description": extract_meta_description(soup),
            "headings": extract_headings(soup),
            "schema_markup": extract_schema_markup(soup, html_content),
            "meta_tags": extract_meta_tags(soup),
            "structured_data": extract_structured_data(soup),
            "content_text": extract_text_content(soup),
            "images": extract_images(soup),
            "links": extract_links(soup),
            "mobile_viewport": check_mobile_viewport(soup),
            "page_structure": analyze_page_structure(soup)
        }
        
        logger.info(f"Successfully scraped: {url}")
        return scraped_data
        
    except httpx.TimeoutException:
        logger.error(f"Timeout scraping: {url}")
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {str(e)}")
        return {"success": False, "error": str(e)}


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title"""
    title_tag = soup.find('title')
    return title_tag.get_text().strip() if title_tag else None


def extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description"""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    return meta_desc.get('content', '').strip() if meta_desc else None


def extract_headings(soup: BeautifulSoup) -> Dict[str, list]:
    """Extract all heading tags"""
    return {
        "h1": [h.get_text().strip() for h in soup.find_all('h1')],
        "h2": [h.get_text().strip() for h in soup.find_all('h2')],
        "h3": [h.get_text().strip() for h in soup.find_all('h3')]
    }


def extract_schema_markup(soup: BeautifulSoup, html: str) -> Dict[str, Any]:
    """Extract JSON-LD schema markup"""
    schemas = []
    
    # Find JSON-LD scripts
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            import json
            schema_data = json.loads(script.string)
            schemas.append(schema_data)
        except:
            continue
    
    # Check for microdata
    has_microdata = bool(soup.find(attrs={'itemtype': True}))
    
    return {
        "json_ld": schemas,
        "has_microdata": has_microdata,
        "count": len(schemas)
    }


def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract important meta tags"""
    meta_tags = {}
    
    # Open Graph tags
    for tag in soup.find_all('meta', attrs={'property': re.compile(r'^og:')}):
        property_name = tag.get('property', '')
        content = tag.get('content', '')
        meta_tags[property_name] = content
    
    # Twitter Card tags
    for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
        name = tag.get('name', '')
        content = tag.get('content', '')
        meta_tags[name] = content
    
    return meta_tags


def extract_structured_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check for structured data indicators"""
    return {
        "has_local_business": bool(soup.find(attrs={'itemtype': re.compile(r'LocalBusiness')})),
        "has_organization": bool(soup.find(attrs={'itemtype': re.compile(r'Organization')})),
        "has_product": bool(soup.find(attrs={'itemtype': re.compile(r'Product')})),
        "has_address": bool(soup.find(attrs={'itemprop': 'address'})),
        "has_telephone": bool(soup.find(attrs={'itemprop': 'telephone'}))
    }


def extract_text_content(soup: BeautifulSoup) -> str:
    """Extract main text content (first 2000 chars)"""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text[:2000]  # Limit for AI analysis


def extract_images(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract image information"""
    images = soup.find_all('img')
    return {
        "count": len(images),
        "with_alt": sum(1 for img in images if img.get('alt')),
        "without_alt": sum(1 for img in images if not img.get('alt'))
    }


def extract_links(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract link information"""
    links = soup.find_all('a', href=True)
    return {
        "total": len(links),
        "internal": sum(1 for link in links if not link['href'].startswith('http')),
        "external": sum(1 for link in links if link['href'].startswith('http'))
    }


def check_mobile_viewport(soup: BeautifulSoup) -> bool:
    """Check if viewport meta tag exists"""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    return bool(viewport)


def analyze_page_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze page structure quality"""
    return {
        "has_header": bool(soup.find('header')),
        "has_nav": bool(soup.find('nav')),
        "has_main": bool(soup.find('main')),
        "has_footer": bool(soup.find('footer')),
        "has_semantic_html": bool(soup.find(['article', 'section', 'aside']))
    }