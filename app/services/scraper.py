# """
# Website Scraping Service
# """
# import httpx
# from bs4 import BeautifulSoup
# from typing import Dict, Any, Optional
# import re
# import json
# import asyncio

# from app.utils import logger


# async def scrape_website(url: str) -> Dict[str, Any]:
#     """
#     Scrape website and extract SEO + AI relevant data
#     """
#     try:
#         logger.info(f"Scraping website: {url}")

#         headers = {
#             "User-Agent": (
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/120.0.0.0 Safari/537.36"
#             ),
#             "Accept-Language": "en-US,en;q=0.9",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Connection": "keep-alive",
#             "Referer": "https://www.google.com/",  # Pretend we came from Google
#         }

#         async with httpx.AsyncClient(
#             timeout=20.0,
#             follow_redirects=True
#         ) as client:

#             # Retry up to 2 times on temporary blocks
#             for attempt in range(2):
#                 response = await client.get(url, headers=headers)
#                 if response.status_code == 200:
#                     break
#                 logger.warning(f"Attempt {attempt+1}: HTTP {response.status_code} for {url}")
#                 await asyncio.sleep(1)

#             if response.status_code != 200:
#                 return {
#                     "success": False,
#                     "error": f"HTTP {response.status_code} - Access blocked or forbidden"
#                 }

#         html = response.text.strip()

#         if len(html) < 200:
#             return {
#                 "success": False,
#                 "error": "Page content too small or blocked"
#             }

#         soup = BeautifulSoup(html, "lxml")

#         scraped_data = {
#             "success": True,
#             "url": url,
#             "title": extract_title(soup),
#             "meta_description": extract_meta_description(soup),
#             "headings": extract_headings(soup),
#             "schema_markup": extract_schema_markup(soup),
#             "meta_tags": extract_meta_tags(soup),
#             "structured_data": extract_structured_data(soup),
#             "content_text": extract_text_content(soup),
#             "images": extract_images(soup),
#             "links": extract_links(soup),
#             "mobile_viewport": check_mobile_viewport(soup),
#             "page_structure": analyze_page_structure(soup),
#         }

#         logger.info(f"Scraping successful: {url}")
#         return scraped_data

#     except httpx.TimeoutException:
#         logger.error(f"Timeout scraping: {url}")
#         return {"success": False, "error": "Request timeout"}

#     except Exception as e:
#         import traceback
#         logger.error(f"Scraping failed: {repr(e)}")
#         logger.error(traceback.format_exc())
#         return {"success": False, "error": repr(e)}


# # ------------------------------------------------------------------
# # EXTRACTION HELPERS (unchanged)
# # ------------------------------------------------------------------

# def extract_title(soup: BeautifulSoup) -> Optional[str]:
#     tag = soup.find("title")
#     return tag.get_text(strip=True) if tag else None


# def extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
#     tag = soup.find("meta", attrs={"name": "description"})
#     return tag.get("content", "").strip() if tag else None


# def extract_headings(soup: BeautifulSoup) -> Dict[str, list]:
#     return {
#         "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
#         "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
#         "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
#     }


# def extract_schema_markup(soup: BeautifulSoup) -> Dict[str, Any]:
#     schemas = []
#     for script in soup.find_all("script", type="application/ld+json"):
#         try:
#             schemas.append(json.loads(script.string))
#         except Exception:
#             continue
#     has_microdata = bool(soup.find(attrs={"itemtype": True}))
#     return {
#         "json_ld": schemas,
#         "has_microdata": has_microdata,
#         "count": len(schemas),
#     }


# def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
#     meta = {}
#     for tag in soup.find_all("meta"):
#         if tag.get("property", "").startswith("og:"):
#             meta[tag["property"]] = tag.get("content", "")
#         if tag.get("name", "").startswith("twitter:"):
#             meta[tag["name"]] = tag.get("content", "")
#     return meta


# def extract_structured_data(soup: BeautifulSoup) -> Dict[str, bool]:
#     return {
#         "has_local_business": bool(soup.find(attrs={"itemtype": re.compile("LocalBusiness")})),
#         "has_organization": bool(soup.find(attrs={"itemtype": re.compile("Organization")})),
#         "has_product": bool(soup.find(attrs={"itemtype": re.compile("Product")})),
#         "has_address": bool(soup.find(attrs={"itemprop": "address"})),
#         "has_telephone": bool(soup.find(attrs={"itemprop": "telephone"})),
#     }


# def extract_text_content(soup: BeautifulSoup) -> str:
#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()
#     text = " ".join(
#         chunk.strip()
#         for line in soup.get_text().splitlines()
#         for chunk in line.split("  ")
#         if chunk.strip()
#     )
#     return text[:2000]


# def extract_images(soup: BeautifulSoup) -> Dict[str, int]:
#     imgs = soup.find_all("img")
#     return {
#         "count": len(imgs),
#         "with_alt": sum(1 for i in imgs if i.get("alt")),
#         "without_alt": sum(1 for i in imgs if not i.get("alt")),
#     }


# def extract_links(soup: BeautifulSoup) -> Dict[str, int]:
#     links = soup.find_all("a", href=True)
#     return {
#         "total": len(links),
#         "internal": sum(1 for l in links if not l["href"].startswith("http")),
#         "external": sum(1 for l in links if l["href"].startswith("http")),
#     }


# def check_mobile_viewport(soup: BeautifulSoup) -> bool:
#     return bool(soup.find("meta", attrs={"name": "viewport"}))


# def analyze_page_structure(soup: BeautifulSoup) -> Dict[str, bool]:
#     return {
#         "has_header": bool(soup.find("header")),
#         "has_nav": bool(soup.find("nav")),
#         "has_main": bool(soup.find("main")),
#         "has_footer": bool(soup.find("footer")),
#         "has_semantic_html": bool(soup.find(["article", "section", "aside"])),
#     }







"""
Enhanced Website Scraping Service with Multi-Page Crawling
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List, Set
import re
import json
import asyncio
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

from app.utils import logger


async def scrape_website_deep(
    url: str,
    max_pages: int = 10,
    include_subpages: bool = True
) -> Dict[str, Any]:
    """
    Deep scrape with multi-page analysis
    
    Args:
        url: Base website URL
        max_pages: Maximum pages to crawl (default 10)
        include_subpages: Whether to crawl subpages
    
    Returns:
        Complete website analysis with page-by-page breakdown
    """
    try:
        logger.info(f"Starting deep analysis for: {url}")
        
        # Parse base domain
        parsed_url = urlparse(url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Step 1: Get all pages to analyze
        pages_to_analyze = await discover_pages(url, base_domain, max_pages)
        logger.info(f"Discovered {len(pages_to_analyze)} pages to analyze")
        
        # Step 2: Analyze each page
        page_results = []
        for page_url in pages_to_analyze[:max_pages]:
            page_data = await scrape_single_page(page_url)
            if page_data.get("success"):
                page_results.append(page_data)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Step 3: Aggregate results
        aggregated_analysis = aggregate_multi_page_results(
            base_url=url,
            base_domain=base_domain,
            page_results=page_results
        )
        
        logger.info(f"Deep analysis completed: {len(page_results)} pages analyzed")
        
        return aggregated_analysis
        
    except Exception as e:
        logger.error(f"Deep scraping failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def discover_pages(
    start_url: str,
    base_domain: str,
    max_pages: int
) -> List[str]:
    """
    Discover all pages on website
    
    Priority:
    1. Check sitemap.xml
    2. Crawl from homepage
    3. Check robots.txt
    """
    discovered_pages = set([start_url])
    
    # Try sitemap first
    sitemap_pages = await get_sitemap_urls(base_domain)
    if sitemap_pages:
        discovered_pages.update(sitemap_pages[:max_pages])
        logger.info(f"Found {len(sitemap_pages)} pages in sitemap")
    
    # If not enough pages, crawl from homepage
    if len(discovered_pages) < max_pages:
        crawled_pages = await crawl_internal_links(
            start_url,
            base_domain,
            max_pages - len(discovered_pages)
        )
        discovered_pages.update(crawled_pages)
    
    return list(discovered_pages)[:max_pages]


async def get_sitemap_urls(base_domain: str) -> List[str]:
    """Extract URLs from sitemap.xml"""
    try:
        sitemap_urls = [
            f"{base_domain}/sitemap.xml",
            f"{base_domain}/sitemap_index.xml",
            f"{base_domain}/sitemap-index.xml"
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for sitemap_url in sitemap_urls:
                try:
                    response = await client.get(sitemap_url)
                    if response.status_code == 200:
                        return parse_sitemap_xml(response.text)
                except:
                    continue
        
        return []
        
    except Exception as e:
        logger.warning(f"Sitemap fetch failed: {str(e)}")
        return []


def parse_sitemap_xml(xml_content: str) -> List[str]:
    """Parse sitemap XML and extract URLs"""
    try:
        root = ElementTree.fromstring(xml_content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = []
        for loc in root.findall('.//ns:loc', namespace):
            if loc.text:
                urls.append(loc.text)
        
        return urls
        
    except Exception as e:
        logger.warning(f"Sitemap parsing failed: {str(e)}")
        return []


async def crawl_internal_links(
    start_url: str,
    base_domain: str,
    max_links: int
) -> Set[str]:
    """Crawl internal links from a page"""
    try:
        discovered = set()
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(start_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code != 200:
                return discovered
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Convert relative to absolute URL
                absolute_url = urljoin(start_url, href)
                parsed = urlparse(absolute_url)
                
                # Only internal links from same domain
                if parsed.netloc == urlparse(base_domain).netloc:
                    # Clean URL (remove fragments and query params)
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    discovered.add(clean_url)
                    
                    if len(discovered) >= max_links:
                        break
        
        return discovered
        
    except Exception as e:
        logger.warning(f"Link crawling failed: {str(e)}")
        return set()


async def scrape_single_page(url: str) -> Dict[str, Any]:
    """Scrape a single page (same as original scrape_website but with more data)"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return {"success": False, "url": url, "error": f"HTTP {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        return {
            "success": True,
            "url": url,
            "title": extract_title(soup),
            "meta_description": extract_meta_description(soup),
            "headings": extract_headings(soup),
            "schema_markup": extract_schema_markup(soup),
            "meta_tags": extract_meta_tags(soup),
            "structured_data": extract_structured_data(soup),
            "content_text": extract_text_content(soup),
            "images": extract_images(soup),
            "links": extract_links(soup),
            "mobile_viewport": check_mobile_viewport(soup),
            "page_structure": analyze_page_structure(soup),
            "word_count": count_words(soup),
            "internal_links_count": count_internal_links(soup, url),
            "external_links_count": count_external_links(soup),
            "canonical_url": extract_canonical(soup),
            "og_tags": extract_og_tags(soup),
            "response_time": response.elapsed.total_seconds()
        }
        
    except Exception as e:
        logger.error(f"Single page scraping failed for {url}: {str(e)}")
        return {"success": False, "url": url, "error": str(e)}


def aggregate_multi_page_results(
    base_url: str,
    base_domain: str,
    page_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregate results from multiple pages into comprehensive analysis
    """
    total_pages = len(page_results)
    successful_pages = [p for p in page_results if p.get("success")]
    
    # Calculate aggregate scores
    pages_with_schema = sum(1 for p in successful_pages if p.get("schema_markup", {}).get("count", 0) > 0)
    pages_with_viewport = sum(1 for p in successful_pages if p.get("mobile_viewport"))
    pages_with_meta_desc = sum(1 for p in successful_pages if p.get("meta_description"))
    
    # Aggregate issues
    all_issues = []
    if pages_with_schema < total_pages * 0.5:
        all_issues.append(f"Only {pages_with_schema}/{total_pages} pages have schema markup")
    if pages_with_viewport < total_pages:
        all_issues.append(f"{total_pages - pages_with_viewport} pages missing mobile viewport")
    if pages_with_meta_desc < total_pages * 0.8:
        all_issues.append(f"Only {pages_with_meta_desc}/{total_pages} pages have meta descriptions")
    
    return {
        "success": True,
        "url": base_url,
        "domain": base_domain,
        "total_pages_analyzed": total_pages,
        "successful_scrapes": len(successful_pages),
        "failed_scrapes": total_pages - len(successful_pages),
        
        # Page-by-page breakdown
        "pages": successful_pages,
        
        # Aggregate statistics
        "aggregate_stats": {
            "schema_coverage": round((pages_with_schema / total_pages) * 100, 1),
            "mobile_optimization": round((pages_with_viewport / total_pages) * 100, 1),
            "meta_description_coverage": round((pages_with_meta_desc / total_pages) * 100, 1),
            "avg_word_count": sum(p.get("word_count", 0) for p in successful_pages) / len(successful_pages) if successful_pages else 0
        },
        
        # Critical issues found across all pages
        "critical_issues": all_issues,
        
        # Original homepage data (for backward compatibility)
        "title": successful_pages[0].get("title") if successful_pages else None,
        "meta_description": successful_pages[0].get("meta_description") if successful_pages else None,
        "schema_markup": successful_pages[0].get("schema_markup") if successful_pages else {},
        "structured_data": successful_pages[0].get("structured_data") if successful_pages else {},
        "headings": successful_pages[0].get("headings") if successful_pages else {},
        "content_text": successful_pages[0].get("content_text") if successful_pages else ""
    }


# Additional extraction helpers
def count_words(soup: BeautifulSoup) -> int:
    """Count words on page"""
    text = extract_text_content(soup)
    return len(text.split())


def count_internal_links(soup: BeautifulSoup, base_url: str) -> int:
    """Count internal links"""
    base_domain = urlparse(base_url).netloc
    count = 0
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.startswith('http') or base_domain in href:
            count += 1
    return count


def count_external_links(soup: BeautifulSoup) -> int:
    """Count external links"""
    return len([l for l in soup.find_all('a', href=True) if l['href'].startswith('http')])


def extract_canonical(soup: BeautifulSoup) -> Optional[str]:
    """Extract canonical URL"""
    canon = soup.find('link', rel='canonical')
    return canon.get('href') if canon else None


def extract_og_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract Open Graph tags"""
    og = {}
    for meta in soup.find_all('meta', property=re.compile(r'^og:')):
        og[meta.get('property')] = meta.get('content', '')
    return og


# Keep all original extraction functions
def extract_title(soup: BeautifulSoup) -> Optional[str]:
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else None

def extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
    tag = soup.find("meta", attrs={"name": "description"})
    return tag.get("content", "").strip() if tag else None

def extract_headings(soup: BeautifulSoup) -> Dict[str, list]:
    return {
        "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
        "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
        "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
    }

def extract_schema_markup(soup: BeautifulSoup) -> Dict[str, Any]:
    schemas = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            schemas.append(json.loads(script.string))
        except:
            continue
    return {
        "json_ld": schemas,
        "has_microdata": bool(soup.find(attrs={"itemtype": True})),
        "count": len(schemas),
    }

def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    meta = {}
    for tag in soup.find_all("meta"):
        if tag.get("property", "").startswith("og:"):
            meta[tag["property"]] = tag.get("content", "")
        if tag.get("name", "").startswith("twitter:"):
            meta[tag["name"]] = tag.get("content", "")
    return meta

def extract_structured_data(soup: BeautifulSoup) -> Dict[str, bool]:
    return {
        "has_local_business": bool(soup.find(attrs={"itemtype": re.compile("LocalBusiness")})),
        "has_organization": bool(soup.find(attrs={"itemtype": re.compile("Organization")})),
        "has_product": bool(soup.find(attrs={"itemtype": re.compile("Product")})),
        "has_address": bool(soup.find(attrs={"itemprop": "address"})),
        "has_telephone": bool(soup.find(attrs={"itemprop": "telephone"})),
    }

def extract_text_content(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(
        chunk.strip()
        for line in soup.get_text().splitlines()
        for chunk in line.split("  ")
        if chunk.strip()
    )
    return text[:2000]

def extract_images(soup: BeautifulSoup) -> Dict[str, int]:
    imgs = soup.find_all("img")
    return {
        "count": len(imgs),
        "with_alt": sum(1 for i in imgs if i.get("alt")),
        "without_alt": sum(1 for i in imgs if not i.get("alt")),
    }

def extract_links(soup: BeautifulSoup) -> Dict[str, int]:
    links = soup.find_all("a", href=True)
    return {
        "total": len(links),
        "internal": sum(1 for l in links if not l["href"].startswith("http")),
        "external": sum(1 for l in links if l["href"].startswith("http")),
    }

def check_mobile_viewport(soup: BeautifulSoup) -> bool:
    return bool(soup.find("meta", attrs={"name": "viewport"}))

def analyze_page_structure(soup: BeautifulSoup) -> Dict[str, bool]:
    return {
        "has_header": bool(soup.find("header")),
        "has_nav": bool(soup.find("nav")),
        "has_main": bool(soup.find("main")),
        "has_footer": bool(soup.find("footer")),
        "has_semantic_html": bool(soup.find(["article", "section", "aside"])),
    }


# Backward compatibility: keep original function name
async def scrape_website(url: str) -> Dict[str, Any]:
    """Original single-page scrape for backward compatibility"""
    return await scrape_single_page(url)