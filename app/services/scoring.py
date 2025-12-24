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
        
#         # Extract scores
#         lighthouse = data.get("lighthouseResult", {})
#         categories = lighthouse.get("categories", {})
        
#         performance_score = int(categories.get("performance", {}).get("score", 0) * 100)
#         seo_score = int(categories.get("seo", {}).get("score", 0) * 100)
#         accessibility_score = int(categories.get("accessibility", {}).get("score", 0) * 100)
        
#         # Core Web Vitals
#         audits = lighthouse.get("audits", {})
        
#         return {
#             "score": seo_score,
#             "performance": {
#                 "score": performance_score,
#                 "fcp": audits.get("first-contentful-paint", {}).get("displayValue"),
#                 "lcp": audits.get("largest-contentful-paint", {}).get("displayValue"),
#                 "cls": audits.get("cumulative-layout-shift", {}).get("displayValue")
#             },
#             "mobile": {
#                 "score": performance_score,
#                 "friendly": audits.get("viewport", {}).get("score", 0) == 1
#             },
#             "page_speed": {
#                 "score": performance_score,
#                 "load_time": audits.get("speed-index", {}).get("displayValue")
#             },
#             "accessibility": {
#                 "score": accessibility_score
#             },
#             "opportunities": [
#                 audit.get("title") 
#                 for audit in audits.values() 
#                 if isinstance(audit, dict) and audit.get("score", 1) < 0.9
#             ][:5]
#         }
        
#     except httpx.TimeoutException:
#         logger.error("PageSpeed API timeout")
#         return {"score": 50, "mobile": {"score": 50}, "page_speed": {"score": 50}}
#     except Exception as e:
#         logger.error(f"SEO analysis failed: {str(e)}")
#         return {"score": 50, "mobile": {"score": 50}, "page_speed": {"score": 50}}


"""
AI Visibility and SEO Scoring Service
"""
import httpx
from typing import Dict, Any
from openai import AsyncOpenAI

from app.config import settings
from app.utils import logger

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def analyze_ai_visibility(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze AI visibility using ChatGPT
    
    Checks:
    - Schema markup quality
    - Structured data completeness
    - Content clarity for AI
    - Local business information
    """
    try:
        logger.info("Analyzing AI visibility with ChatGPT...")
        
        # Prepare analysis prompt
        prompt = f"""
Analyze this website for AI visibility and structured data quality.

Website Data:
- Title: {scraped_data.get('title')}
- Meta Description: {scraped_data.get('meta_description')}
- Has Schema Markup: {scraped_data.get('schema_markup', {}).get('count', 0) > 0}
- Schema Types Found: {scraped_data.get('schema_markup', {}).get('json_ld', [])}
- Structured Data: {scraped_data.get('structured_data')}
- Headings: {scraped_data.get('headings')}
- Content Sample: {scraped_data.get('content_text', '')[:500]}

Provide a JSON response with:
{{
  "score": (0-100, integer),
  "critical_issues": ["list of critical issues"],
  "warnings": ["list of warnings"],
  "recommendations": ["list of recommendations"],
  "schema_quality": "poor|fair|good|excellent",
  "ai_readability": "poor|fair|good|excellent",
  "strengths": ["list of strengths"],
  "missing_elements": ["list of missing elements"]
}}

Focus on:
1. Schema.org markup presence and quality
2. Local business structured data
3. Content clarity for AI understanding
4. Missing critical information
"""

        # Call ChatGPT
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI visibility expert. Analyze websites for how well they can be understood by AI assistants like ChatGPT, Google's AI, and voice assistants. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        import json
        analysis = json.loads(response.choices[0].message.content)
        
        logger.info(f"AI visibility score: {analysis.get('score', 0)}")
        
        return {
            "score": analysis.get("score", 0),
            "critical_issues": analysis.get("critical_issues", []),
            "warnings": analysis.get("warnings", []),
            "recommendations": analysis.get("recommendations", []),
            "schema_markup": {
                "quality": analysis.get("schema_quality", "poor"),
                "has_markup": scraped_data.get('schema_markup', {}).get('count', 0) > 0
            },
            "readability": {
                "level": analysis.get("ai_readability", "fair")
            },
            "strengths": analysis.get("strengths", []),
            "missing_elements": analysis.get("missing_elements", [])
        }
        
    except Exception as e:
        logger.error(f"AI visibility analysis failed: {str(e)}")
        return {
            "score": 0,
            "critical_issues": ["Analysis failed"],
            "warnings": [],
            "recommendations": []
        }


async def analyze_seo(url: str) -> Dict[str, Any]:
    """
    Analyze SEO using PageSpeed Insights API
    
    Metrics:
    - Performance score
    - Mobile optimization
    - Page speed
    - Core Web Vitals
    """
    try:
        logger.info(f"Analyzing SEO with PageSpeed Insights: {url}")
        
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": settings.PAGESPEED_API_KEY,
            "strategy": "mobile",  # or "desktop"
            "category": ["performance", "seo", "accessibility"]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(api_url, params=params)
            
            if response.status_code != 200:
                logger.warning(f"PageSpeed API returned {response.status_code}")
                return {
                    "score": 50,  # Default neutral score
                    "mobile": {"score": 50},
                    "page_speed": {"score": 50}
                }
            
            data = response.json()
            logger.debug(f"PageSpeed API response received")
        
        # Extract scores with proper None handling
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        
        logger.debug(f"Categories found: {list(categories.keys())}")
        
        # Safe score extraction
        def get_score(category_name):
            category = categories.get(category_name, {})
            score = category.get("score")
            if score is None:
                return 0
            return int(score * 100)
        
        performance_score = get_score("performance")
        seo_score = get_score("seo")
        accessibility_score = get_score("accessibility")
        
        # Core Web Vitals
        audits = lighthouse.get("audits", {})
        
        return {
            "score": seo_score,
            "performance": {
                "score": performance_score,
                "fcp": audits.get("first-contentful-paint", {}).get("displayValue", "N/A"),
                "lcp": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
                "cls": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
            },
            "mobile": {
                "score": performance_score,
                "friendly": audits.get("viewport", {}).get("score", 0) == 1
            },
            "page_speed": {
                "score": performance_score,
                "load_time": audits.get("speed-index", {}).get("displayValue", "N/A")
            },
            "accessibility": {
                "score": accessibility_score
            },
            "opportunities": [
                audit.get("title", "Unknown") 
                for audit_key, audit in audits.items() 
                if isinstance(audit, dict) and audit.get("score", 1) is not None and audit.get("score", 1) < 0.9
            ][:5]
        }
        
    except httpx.TimeoutException:
        logger.error("PageSpeed API timeout")
        return {"score": 50, "mobile": {"score": 50}, "page_speed": {"score": 50}}
    except Exception as e:
        logger.error(f"SEO analysis failed: {str(e)}")
        return {"score": 50, "mobile": {"score": 50}, "page_speed": {"score": 50}}