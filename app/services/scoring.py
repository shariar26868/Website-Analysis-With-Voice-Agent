# """
# AI Visibility and SEO Scoring Service
# """
# import httpx
# from typing import Dict, Any
# from openai import AsyncOpenAI

# from app.config import settings
# from app.utils import logger

# # Initialize OpenAI client
# openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# async def analyze_ai_visibility(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Analyze AI visibility using ChatGPT
    
#     Checks:
#     - Schema markup quality
#     - Structured data completeness
#     - Content clarity for AI
#     - Local business information
#     """
#     try:
#         logger.info("Analyzing AI visibility with ChatGPT...")
        
#         # Prepare analysis prompt
#         prompt = f"""
# Analyze this website for AI visibility and structured data quality.

# Website Data:
# - Title: {scraped_data.get('title')}
# - Meta Description: {scraped_data.get('meta_description')}
# - Has Schema Markup: {scraped_data.get('schema_markup', {}).get('count', 0) > 0}
# - Schema Types Found: {scraped_data.get('schema_markup', {}).get('json_ld', [])}
# - Structured Data: {scraped_data.get('structured_data')}
# - Headings: {scraped_data.get('headings')}
# - Content Sample: {scraped_data.get('content_text', '')[:500]}

# Provide a JSON response with:
# {{
#   "score": (0-100, integer),
#   "critical_issues": ["list of critical issues"],
#   "warnings": ["list of warnings"],
#   "recommendations": ["list of recommendations"],
#   "schema_quality": "poor|fair|good|excellent",
#   "ai_readability": "poor|fair|good|excellent",
#   "strengths": ["list of strengths"],
#   "missing_elements": ["list of missing elements"]
# }}

# Focus on:
# 1. Schema.org markup presence and quality
# 2. Local business structured data
# 3. Content clarity for AI understanding
# 4. Missing critical information
# """

#         # Call ChatGPT
#         response = await openai_client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are an AI visibility expert. Analyze websites for how well they can be understood by AI assistants like ChatGPT, Google's AI, and voice assistants. Return only valid JSON."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],
#             temperature=0.3,
#             response_format={"type": "json_object"}
#         )
        
#         # Parse response
#         import json
#         analysis = json.loads(response.choices[0].message.content)
        
#         logger.info(f"AI visibility score: {analysis.get('score', 0)}")
        
#         return {
#             "score": analysis.get("score", 0),
#             "critical_issues": analysis.get("critical_issues", []),
#             "warnings": analysis.get("warnings", []),
#             "recommendations": analysis.get("recommendations", []),
#             "schema_markup": {
#                 "quality": analysis.get("schema_quality", "poor"),
#                 "has_markup": scraped_data.get('schema_markup', {}).get('count', 0) > 0
#             },
#             "readability": {
#                 "level": analysis.get("ai_readability", "fair")
#             },
#             "strengths": analysis.get("strengths", []),
#             "missing_elements": analysis.get("missing_elements", [])
#         }
        
#     except Exception as e:
#         logger.error(f"AI visibility analysis failed: {str(e)}")
#         return {
#             "score": 0,
#             "critical_issues": ["Analysis failed"],
#             "warnings": [],
#             "recommendations": []
#         }


# async def analyze_seo(url: str) -> Dict[str, Any]:
#     """
#     Analyze SEO using PageSpeed Insights API
    
#     Metrics:
#     - Performance score
#     - Mobile optimization
#     - Page speed
#     - Core Web Vitals
#     """
#     try:
#         logger.info(f"Analyzing SEO with PageSpeed Insights: {url}")
        
#         api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
#         params = {
#             "url": url,
#             "key": settings.PAGESPEED_API_KEY,
#             "strategy": "mobile",  # or "desktop"
#             "category": ["performance", "seo", "accessibility"]
#         }
        
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             response = await client.get(api_url, params=params)
            
#             if response.status_code != 200:
#                 logger.warning(f"PageSpeed API returned {response.status_code}")
#                 return {
#                     "score": 50,  # Default neutral score
#                     "mobile": {"score": 50},
#                     "page_speed": {"score": 50}
#                 }
            
#             data = response.json()
#             logger.debug(f"PageSpeed API response received")
        
#         # Extract scores with proper None handling
#         lighthouse = data.get("lighthouseResult", {})
#         categories = lighthouse.get("categories", {})
        
#         logger.debug(f"Categories found: {list(categories.keys())}")
        
#         # Safe score extraction
#         def get_score(category_name):
#             category = categories.get(category_name, {})
#             score = category.get("score")
#             if score is None:
#                 return 0
#             return int(score * 100)
        
#         performance_score = get_score("performance")
#         seo_score = get_score("seo")
#         accessibility_score = get_score("accessibility")
        
#         # Core Web Vitals
#         audits = lighthouse.get("audits", {})
        
#         return {
#             "score": seo_score,
#             "performance": {
#                 "score": performance_score,
#                 "fcp": audits.get("first-contentful-paint", {}).get("displayValue", "N/A"),
#                 "lcp": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
#                 "cls": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
#             },
#             "mobile": {
#                 "score": performance_score,
#                 "friendly": audits.get("viewport", {}).get("score", 0) == 1
#             },
#             "page_speed": {
#                 "score": performance_score,
#                 "load_time": audits.get("speed-index", {}).get("displayValue", "N/A")
#             },
#             "accessibility": {
#                 "score": accessibility_score
#             },
#             "opportunities": [
#                 audit.get("title", "Unknown") 
#                 for audit_key, audit in audits.items() 
#                 if isinstance(audit, dict) and audit.get("score", 1) is not None and audit.get("score", 1) < 0.9
#             ][:5]
#         }
        
#     except httpx.TimeoutException:
#         logger.error("PageSpeed API timeout")
#         return {"score": 50, "mobile": {"score": 50}, "page_speed": {"score": 50}}
#     except Exception as e:
#         logger.error(f"SEO analysis failed: {str(e)}")
#         return {"score": 50, "mobile": {"score": 50}, "page_speed": {"score": 50}}





"""
Enhanced AI Visibility and SEO Scoring with Multi-Page Analysis
"""
import httpx
from typing import Dict, Any, List
from openai import AsyncOpenAI
import asyncio

from app.config import settings
from app.utils import logger

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def analyze_ai_visibility_deep(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep AI visibility analysis across multiple pages
    
    Analyzes:
    - Overall site structure
    - Page-by-page AI readability
    - Schema consistency
    - Content quality across pages
    """
    try:
        logger.info("Starting deep AI visibility analysis...")
        
        # Get page-level data
        pages = scraped_data.get("pages", [scraped_data])
        total_pages = len(pages)
        
        # Analyze homepage first (detailed)
        homepage_analysis = await analyze_single_page_ai(pages[0] if pages else scraped_data)
        
        # Quick analysis for other pages
        other_pages_analysis = []
        if total_pages > 1:
            for page in pages[1:min(5, total_pages)]:  # Analyze up to 5 pages
                page_score = await quick_page_analysis(page)
                other_pages_analysis.append(page_score)
                await asyncio.sleep(0.5)  # Rate limiting
        
        # Calculate aggregate scores
        avg_page_score = sum([p.get("score", 0) for p in other_pages_analysis]) / len(other_pages_analysis) if other_pages_analysis else homepage_analysis.get("score", 0)
        
        # Aggregate statistics
        aggregate_stats = scraped_data.get("aggregate_stats", {})
        
        # Build comprehensive analysis
        comprehensive_analysis = {
            "score": int((homepage_analysis.get("score", 0) * 0.6) + (avg_page_score * 0.4)),
            "homepage_score": homepage_analysis.get("score", 0),
            "average_page_score": int(avg_page_score),
            
            # Detailed issues
            "critical_issues": homepage_analysis.get("critical_issues", []) + aggregate_site_issues(scraped_data),
            "warnings": homepage_analysis.get("warnings", []),
            "recommendations": homepage_analysis.get("recommendations", []) + generate_site_recommendations(scraped_data),
            
            # Quality metrics
            "schema_markup": {
                "quality": homepage_analysis.get("schema_quality", "poor"),
                "has_markup": scraped_data.get("schema_markup", {}).get("count", 0) > 0,
                "coverage": aggregate_stats.get("schema_coverage", 0),
                "consistency": "high" if aggregate_stats.get("schema_coverage", 0) > 80 else "low"
            },
            
            "readability": {
                "level": homepage_analysis.get("ai_readability", "fair"),
                "consistency": calculate_consistency(other_pages_analysis)
            },
            
            # Site-wide metrics
            "site_metrics": {
                "total_pages_analyzed": total_pages,
                "mobile_optimization": aggregate_stats.get("mobile_optimization", 0),
                "meta_coverage": aggregate_stats.get("meta_description_coverage", 0),
                "avg_word_count": int(aggregate_stats.get("avg_word_count", 0))
            },
            
            "strengths": homepage_analysis.get("strengths", []),
            "missing_elements": homepage_analysis.get("missing_elements", []),
            
            # Page-by-page breakdown
            "page_scores": [
                {
                    "url": p.get("url"),
                    "score": p.get("score", 0),
                    "has_schema": p.get("has_schema", False)
                }
                for p in other_pages_analysis
            ]
        }
        
        logger.info(f"Deep AI visibility analysis complete. Score: {comprehensive_analysis['score']}")
        
        return comprehensive_analysis
        
    except Exception as e:
        logger.error(f"Deep AI visibility analysis failed: {str(e)}")
        # Fallback to simple analysis
        return await analyze_single_page_ai(scraped_data)


async def analyze_single_page_ai(page_data: Dict[str, Any]) -> Dict[str, Any]:
    """Detailed AI analysis for a single page using GPT-4"""
    try:
        prompt = f"""
Analyze this webpage for AI visibility and structured data quality.

Website Data:
- Title: {page_data.get('title')}
- Meta Description: {page_data.get('meta_description')}
- URL: {page_data.get('url', 'N/A')}
- Has Schema Markup: {page_data.get('schema_markup', {}).get('count', 0) > 0}
- Schema Types: {page_data.get('schema_markup', {}).get('json_ld', [])}
- Structured Data: {page_data.get('structured_data')}
- Headings: {page_data.get('headings')}
- Word Count: {page_data.get('word_count', 0)}
- Has Mobile Viewport: {page_data.get('mobile_viewport', False)}
- Content Sample: {page_data.get('content_text', '')[:500]}

Provide a JSON response with:
{{
  "score": (0-100, integer),
  "critical_issues": ["list of critical issues"],
  "warnings": ["list of warnings"],
  "recommendations": ["list of specific actionable recommendations"],
  "schema_quality": "poor|fair|good|excellent",
  "ai_readability": "poor|fair|good|excellent",
  "strengths": ["list of strengths"],
  "missing_elements": ["list of missing critical elements"],
  "content_quality": "poor|fair|good|excellent",
  "technical_score": (0-100, integer)
}}

Focus on:
1. Schema.org markup presence and implementation quality
2. Local business structured data (if applicable)
3. Content clarity and structure for AI understanding
4. Missing critical metadata and structured information
5. Mobile optimization indicators
6. Content depth and quality
"""

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI visibility expert. Analyze websites for how well AI assistants (ChatGPT, Google AI, voice assistants) can understand and extract information. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        analysis = json.loads(response.choices[0].message.content)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Single page AI analysis failed: {str(e)}")
        return {
            "score": 0,
            "critical_issues": ["Analysis failed"],
            "warnings": [],
            "recommendations": []
        }


async def quick_page_analysis(page_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick scoring for additional pages without GPT"""
    score = 50  # Base score
    
    # Add points for good practices
    if page_data.get("schema_markup", {}).get("count", 0) > 0:
        score += 20
    if page_data.get("meta_description"):
        score += 10
    if page_data.get("mobile_viewport"):
        score += 10
    if page_data.get("headings", {}).get("h1"):
        score += 5
    if page_data.get("word_count", 0) > 300:
        score += 5
    
    return {
        "url": page_data.get("url"),
        "score": min(score, 100),
        "has_schema": page_data.get("schema_markup", {}).get("count", 0) > 0,
        "has_meta": bool(page_data.get("meta_description")),
        "mobile_ready": page_data.get("mobile_viewport", False)
    }


def aggregate_site_issues(scraped_data: Dict[str, Any]) -> List[str]:
    """Generate site-wide issues based on aggregate data"""
    issues = []
    stats = scraped_data.get("aggregate_stats", {})
    total_pages = scraped_data.get("total_pages_analyzed", 1)
    
    # Schema markup issues
    schema_coverage = stats.get("schema_coverage", 0)
    if schema_coverage < 30:
        issues.append(f"Critical: Only {schema_coverage}% of pages have schema markup")
    elif schema_coverage < 70:
        issues.append(f"Warning: {schema_coverage}% schema markup coverage (should be 100%)")
    
    # Mobile optimization
    mobile_opt = stats.get("mobile_optimization", 0)
    if mobile_opt < 100:
        issues.append(f"{100 - mobile_opt}% of pages missing mobile viewport meta tag")
    
    # Meta descriptions
    meta_coverage = stats.get("meta_description_coverage", 0)
    if meta_coverage < 80:
        issues.append(f"Only {meta_coverage}% of pages have meta descriptions")
    
    return issues


def generate_site_recommendations(scraped_data: Dict[str, Any]) -> List[str]:
    """Generate site-wide recommendations"""
    recommendations = []
    stats = scraped_data.get("aggregate_stats", {})
    
    if stats.get("schema_coverage", 0) < 100:
        recommendations.append("Implement schema markup on all pages for better AI visibility")
    
    if stats.get("mobile_optimization", 0) < 100:
        recommendations.append("Add mobile viewport meta tags to all pages")
    
    if stats.get("meta_description_coverage", 0) < 90:
        recommendations.append("Write unique meta descriptions for all pages")
    
    if stats.get("avg_word_count", 0) < 300:
        recommendations.append("Increase content depth - aim for 500+ words per page")
    
    recommendations.append("Implement consistent structured data across all pages")
    recommendations.append("Consider adding FAQ schema for better voice search visibility")
    
    return recommendations


def calculate_consistency(page_analyses: List[Dict[str, Any]]) -> str:
    """Calculate consistency score across pages"""
    if not page_analyses:
        return "unknown"
    
    scores = [p.get("score", 0) for p in page_analyses]
    if not scores:
        return "unknown"
    
    avg_score = sum(scores) / len(scores)
    variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5
    
    if std_dev < 10:
        return "high"
    elif std_dev < 20:
        return "medium"
    else:
        return "low"


async def analyze_seo_enhanced(url: str, page_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Enhanced SEO analysis with additional metrics
    """
    try:
        logger.info(f"Enhanced SEO analysis for: {url}")
        
        # Get PageSpeed data
        pagespeed_data = await get_pagespeed_data(url)
        
        # Add technical SEO metrics from scraped data
        technical_seo = {}
        if page_data:
            technical_seo = {
                "canonical_url": page_data.get("canonical_url"),
                "og_tags_present": len(page_data.get("og_tags", {})) > 0,
                "internal_links": page_data.get("internal_links_count", 0),
                "external_links": page_data.get("external_links_count", 0),
                "images_with_alt": page_data.get("images", {}).get("with_alt", 0),
                "images_without_alt": page_data.get("images", {}).get("without_alt", 0),
                "has_sitemap": page_data.get("has_sitemap", False)
            }
        
        # Merge PageSpeed and technical data
        combined_analysis = {
            **pagespeed_data,
            "technical_seo": technical_seo,
            "seo_health_score": calculate_seo_health(pagespeed_data, technical_seo)
        }
        
        return combined_analysis
        
    except Exception as e:
        logger.error(f"Enhanced SEO analysis failed: {str(e)}")
        return await analyze_seo(url)


async def get_pagespeed_data(url: str) -> Dict[str, Any]:
    """Get PageSpeed Insights data"""
    try:
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": settings.PAGESPEED_API_KEY,
            "strategy": "mobile",
            "category": ["performance", "seo", "accessibility", "best-practices"]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(api_url, params=params)
            
            if response.status_code != 200:
                logger.warning(f"PageSpeed API returned {response.status_code}")
                return get_default_seo_scores()
            
            data = response.json()
        
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        
        def get_score(cat_name):
            cat = categories.get(cat_name, {})
            score = cat.get("score")
            return int(score * 100) if score is not None else 0
        
        return {
            "score": get_score("seo"),
            "performance": {"score": get_score("performance")},
            "accessibility": {"score": get_score("accessibility")},
            "best_practices": {"score": get_score("best-practices")},
            "mobile": {"score": get_score("performance"), "friendly": True},
            "page_speed": {"score": get_score("performance")}
        }
        
    except Exception as e:
        logger.error(f"PageSpeed fetch failed: {str(e)}")
        return get_default_seo_scores()


def get_default_seo_scores() -> Dict[str, Any]:
    """Default scores when PageSpeed fails"""
    return {
        "score": 50,
        "performance": {"score": 50},
        "accessibility": {"score": 50},
        "mobile": {"score": 50, "friendly": True},
        "page_speed": {"score": 50}
    }


def calculate_seo_health(pagespeed: Dict, technical: Dict) -> int:
    """Calculate overall SEO health score"""
    score = 0
    
    # PageSpeed scores (50% weight)
    score += pagespeed.get("score", 0) * 0.3
    score += pagespeed.get("performance", {}).get("score", 0) * 0.2
    
    # Technical SEO (50% weight)
    if technical.get("canonical_url"):
        score += 10
    if technical.get("og_tags_present"):
        score += 10
    if technical.get("internal_links", 0) > 5:
        score += 10
    
    images_total = technical.get("images_with_alt", 0) + technical.get("images_without_alt", 0)
    if images_total > 0:
        alt_ratio = technical.get("images_with_alt", 0) / images_total
        score += int(alt_ratio * 20)
    
    return int(min(score, 100))


# Keep backward compatibility
async def analyze_ai_visibility(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """Original function for backward compatibility"""
    return await analyze_single_page_ai(scraped_data)


async def analyze_seo(url: str) -> Dict[str, Any]:
    """Original function for backward compatibility"""
    return await get_pagespeed_data(url)