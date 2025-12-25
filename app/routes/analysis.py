# """
# Website Analysis API Routes
# """
# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from datetime import datetime
# from bson import ObjectId

# from app.models import AnalyzeRequest, AnalyzeResponse, AnalysisResult, Lead, CallStatus
# from app.config import get_db
# from app.services.scraper import scrape_website
# from app.services.scoring import analyze_ai_visibility, analyze_seo
# from app.utils import logger, calculate_overall_score, normalize_phone

# router = APIRouter()


# @router.post("/", response_model=AnalyzeResponse)
# async def analyze_website(request: AnalyzeRequest, background_tasks: BackgroundTasks):
#     """
#     Analyze a website and return AI visibility score
    
#     Flow:
#     1. Scrape website
#     2. Analyze AI visibility (ChatGPT)
#     3. Analyze SEO (PageSpeed)
#     4. Save lead to database
#     5. Return instant preview score
#     """
#     try:
#         logger.info(f"Starting analysis for: {request.website_url}")
        
#         # Step 1: Scrape website
#         logger.info("Scraping website...")
#         scraped_data = await scrape_website(str(request.website_url))
        
#         if not scraped_data.get("success"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to scrape website. Please check the URL."
#             )
        
#         # Step 2: Analyze AI Visibility (ChatGPT)
#         logger.info("Analyzing AI visibility...")
#         ai_analysis = await analyze_ai_visibility(scraped_data)
        
#         # Step 3: Analyze SEO (PageSpeed)
#         logger.info("Analyzing SEO...")
#         seo_analysis = await analyze_seo(str(request.website_url))
        
#         # Calculate overall score
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )
        
#         # Step 4: Create analysis result
#         analysis_result = AnalysisResult(
#             website_url=request.website_url,
#             ai_visibility_score=ai_analysis.get("score", 0),
#             seo_score=seo_analysis.get("score", 0),
#             overall_score=overall_score,
#             critical_issues=ai_analysis.get("critical_issues", []),
#             warnings=ai_analysis.get("warnings", []),
#             recommendations=ai_analysis.get("recommendations", []),
#             schema_markup=ai_analysis.get("schema_markup", {}),
#             mobile_optimization=seo_analysis.get("mobile", {}),
#             page_speed=seo_analysis.get("page_speed", {}),
#             ai_readability=ai_analysis.get("readability", {}),
#             analyzed_at=datetime.utcnow()
#         )
        
#         # Step 5: Save lead to database
#         db = get_db()
#         lead_data = Lead(
#             business_name=request.business_name,
#             website_url=request.website_url,
#             phone_number=normalize_phone(request.phone_number),
#             city=request.city,
#             state=request.state,
#             industry=request.industry,
#             ai_visibility_score=analysis_result.ai_visibility_score,
#             seo_score=analysis_result.seo_score,
#             top_issues=analysis_result.critical_issues[:5],
#             analysis_data=analysis_result.model_dump(),
#             call_status=CallStatus.PENDING,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )
        
#         # Convert Pydantic models to dict and handle URL serialization
#         lead_dict = lead_data.model_dump()
        
#         # Convert all URL objects to strings
#         def convert_urls(obj):
#             if isinstance(obj, dict):
#                 return {k: convert_urls(v) for k, v in obj.items()}
#             elif isinstance(obj, list):
#                 return [convert_urls(item) for item in obj]
#             elif hasattr(obj, '__class__') and 'Url' in obj.__class__.__name__:
#                 return str(obj)
#             else:
#                 return obj
        
#         lead_dict = convert_urls(lead_dict)
        
#         result = await db.leads.insert_one(lead_dict)
#         lead_id = str(result.inserted_id)
        
#         logger.info(f"Analysis completed. Lead ID: {lead_id}")
        
#         return AnalyzeResponse(
#             success=True,
#             message="Analysis completed successfully",
#             lead_id=lead_id,
#             analysis=analysis_result
#         )
        
#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         logger.error(f"Analysis failed: {str(e)}")
#         logger.error(f"Full traceback: {error_details}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Analysis failed: {str(e)}"
#         )


# @router.get("/{lead_id}")
# async def get_analysis(lead_id: str):
#     """Get analysis results for a specific lead"""
#     try:
#         db = get_db()
#         lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
#         if not lead:
#             raise HTTPException(status_code=404, detail="Lead not found")
        
#         return {
#             "success": True,
#             "lead_id": lead_id,
#             "business_name": lead.get("business_name"),
#             "website_url": lead.get("website_url"),
#             "analysis": lead.get("analysis_data", {})
#         }
        
#     except Exception as e:
#         logger.error(f"Failed to get analysis: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))







# """
# Enhanced Website Analysis API Routes with Multi-Page Analysis
# """
# from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
# from datetime import datetime
# from bson import ObjectId
# from typing import Optional

# from app.models import AnalyzeRequest, AnalyzeResponse, AnalysisResult, Lead, CallStatus
# from app.config import get_db
# from app.services.scraper import scrape_website, scrape_website_deep
# from app.services.scoring import (
#     analyze_ai_visibility,
#     analyze_ai_visibility_deep,
#     analyze_seo,
#     analyze_seo_enhanced
# )
# from app.utils import logger, calculate_overall_score, normalize_phone

# router = APIRouter()


# @router.post("/", response_model=AnalyzeResponse)
# async def analyze_website_quick(
#     request: AnalyzeRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     Quick website analysis (homepage only)
#     Fast preview for immediate user feedback
#     """
#     try:
#         logger.info(f"Starting quick analysis for: {request.website_url}")
        
#         # Scrape homepage only
#         scraped_data = await scrape_website(str(request.website_url))
        
#         if not scraped_data.get("success"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to scrape website. Please check the URL."
#             )
        
#         # AI visibility analysis
#         ai_analysis = await analyze_ai_visibility(scraped_data)
        
#         # SEO analysis
#         seo_analysis = await analyze_seo(str(request.website_url))
        
#         # Calculate scores
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )
        
#         # Create analysis result
#         analysis_result = AnalysisResult(
#             website_url=request.website_url,
#             ai_visibility_score=ai_analysis.get("score", 0),
#             seo_score=seo_analysis.get("score", 0),
#             overall_score=overall_score,
#             critical_issues=ai_analysis.get("critical_issues", []),
#             warnings=ai_analysis.get("warnings", []),
#             recommendations=ai_analysis.get("recommendations", []),
#             schema_markup=ai_analysis.get("schema_markup", {}),
#             mobile_optimization=seo_analysis.get("mobile", {}),
#             page_speed=seo_analysis.get("page_speed", {}),
#             ai_readability=ai_analysis.get("readability", {}),
#             analyzed_at=datetime.utcnow()
#         )
        
#         # Save to database
#         lead_id = await save_lead_to_db(request, analysis_result)
        
#         logger.info(f"Quick analysis completed. Lead ID: {lead_id}")
        
#         return AnalyzeResponse(
#             success=True,
#             message="Quick analysis completed successfully",
#             lead_id=lead_id,
#             analysis=analysis_result
#         )
        
#     except Exception as e:
#         logger.error(f"Quick analysis failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# @router.post("/deep")
# async def analyze_website_deep_route(
#     request: AnalyzeRequest,
#     max_pages: int = Query(10, ge=1, le=50, description="Maximum pages to analyze"),
#     background_tasks: BackgroundTasks = None
# ):
#     """
#     Deep website analysis (multi-page crawling)
    
#     Analyzes:
#     - Multiple pages (up to max_pages)
#     - Site-wide SEO health
#     - Page-by-page breakdown
#     - Comprehensive recommendations
    
#     Takes longer but provides complete site audit
#     """
#     try:
#         logger.info(f"Starting DEEP analysis for: {request.website_url} (max {max_pages} pages)")
        
#         # Deep scrape with multi-page crawling
#         scraped_data = await scrape_website_deep(
#             str(request.website_url),
#             max_pages=max_pages,
#             include_subpages=True
#         )
        
#         if not scraped_data.get("success"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to scrape website. Please check the URL."
#             )
        
#         logger.info(f"Scraped {scraped_data.get('total_pages_analyzed', 0)} pages")
        
#         # Deep AI visibility analysis
#         ai_analysis = await analyze_ai_visibility_deep(scraped_data)
        
#         # Enhanced SEO analysis
#         first_page = scraped_data.get("pages", [{}])[0] if scraped_data.get("pages") else {}
#         seo_analysis = await analyze_seo_enhanced(
#             str(request.website_url),
#             page_data=first_page
#         )
        
#         # Calculate comprehensive scores
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )
        
#         # Build comprehensive analysis result
#         analysis_result = {
#             "website_url": str(request.website_url),
#             "analysis_type": "deep",
#             "total_pages_analyzed": scraped_data.get("total_pages_analyzed", 0),
            
#             # Scores
#             "ai_visibility_score": ai_analysis.get("score", 0),
#             "homepage_ai_score": ai_analysis.get("homepage_score", 0),
#             "average_page_score": ai_analysis.get("average_page_score", 0),
#             "seo_score": seo_analysis.get("score", 0),
#             "seo_health_score": seo_analysis.get("seo_health_score", 0),
#             "overall_score": overall_score,
            
#             # Issues and recommendations
#             "critical_issues": ai_analysis.get("critical_issues", []),
#             "warnings": ai_analysis.get("warnings", []),
#             "recommendations": ai_analysis.get("recommendations", []),
            
#             # Detailed metrics
#             "schema_markup": ai_analysis.get("schema_markup", {}),
#             "site_metrics": ai_analysis.get("site_metrics", {}),
#             "mobile_optimization": seo_analysis.get("mobile", {}),
#             "page_speed": seo_analysis.get("page_speed", {}),
#             "technical_seo": seo_analysis.get("technical_seo", {}),
            
#             # Page breakdown
#             "page_scores": ai_analysis.get("page_scores", []),
#             "pages_detail": scraped_data.get("pages", [])[:5],  # First 5 pages detail
            
#             "analyzed_at": datetime.utcnow().isoformat()
#         }
        
#         # Save enhanced lead data
#         db = get_db()
#         lead_data = {
#             "business_name": request.business_name,
#             "website_url": str(request.website_url),
#             "phone_number": normalize_phone(request.phone_number),
#             "city": request.city,
#             "state": request.state,
#             "industry": request.industry,
#             "ai_visibility_score": ai_analysis.get("score", 0),
#             "seo_score": seo_analysis.get("score", 0),
#             "overall_score": overall_score,
#             "top_issues": ai_analysis.get("critical_issues", [])[:5],
#             "analysis_data": analysis_result,
#             "analysis_type": "deep",
#             "call_status": CallStatus.PENDING,
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
        
#         result = await db.leads.insert_one(lead_data)
#         lead_id = str(result.inserted_id)
        
#         logger.info(f"Deep analysis completed. Lead ID: {lead_id}")
        
#         return {
#             "success": True,
#             "message": f"Deep analysis completed - {scraped_data.get('total_pages_analyzed', 0)} pages analyzed",
#             "lead_id": lead_id,
#             "analysis": analysis_result
#         }
        
#     except Exception as e:
#         import traceback
#         logger.error(f"Deep analysis failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Deep analysis failed: {str(e)}")


# @router.get("/{lead_id}")
# async def get_analysis(lead_id: str):
#     """Get analysis results for a specific lead"""
#     try:
#         db = get_db()
#         lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
#         if not lead:
#             raise HTTPException(status_code=404, detail="Lead not found")
        
#         # Convert ObjectId to string
#         lead["_id"] = str(lead["_id"])
        
#         return {
#             "success": True,
#             "lead_id": lead_id,
#             "business_name": lead.get("business_name"),
#             "website_url": lead.get("website_url"),
#             "analysis_type": lead.get("analysis_type", "quick"),
#             "scores": {
#                 "ai_visibility": lead.get("ai_visibility_score"),
#                 "seo": lead.get("seo_score"),
#                 "overall": lead.get("overall_score")
#             },
#             "top_issues": lead.get("top_issues", []),
#             "analysis": lead.get("analysis_data", {})
#         }
        
#     except Exception as e:
#         logger.error(f"Failed to get analysis: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{lead_id}/pages")
# async def get_page_breakdown(lead_id: str):
#     """Get page-by-page analysis breakdown"""
#     try:
#         db = get_db()
#         lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
#         if not lead:
#             raise HTTPException(status_code=404, detail="Lead not found")
        
#         analysis_data = lead.get("analysis_data", {})
        
#         return {
#             "success": True,
#             "lead_id": lead_id,
#             "total_pages": analysis_data.get("total_pages_analyzed", 1),
#             "page_scores": analysis_data.get("page_scores", []),
#             "pages_detail": analysis_data.get("pages_detail", [])
#         }
        
#     except Exception as e:
#         logger.error(f"Failed to get page breakdown: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# async def save_lead_to_db(request: AnalyzeRequest, analysis_result: AnalysisResult) -> str:
#     """Helper function to save lead to database"""
#     db = get_db()
#     lead_data = Lead(
#         business_name=request.business_name,
#         website_url=request.website_url,
#         phone_number=normalize_phone(request.phone_number),
#         city=request.city,
#         state=request.state,
#         industry=request.industry,
#         ai_visibility_score=analysis_result.ai_visibility_score,
#         seo_score=analysis_result.seo_score,
#         top_issues=analysis_result.critical_issues[:5],
#         analysis_data=analysis_result.model_dump(),
#         call_status=CallStatus.PENDING,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
    
#     lead_dict = lead_data.model_dump()
    
#     # Convert URLs to strings
#     def convert_urls(obj):
#         if isinstance(obj, dict):
#             return {k: convert_urls(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [convert_urls(item) for item in obj]
#         elif hasattr(obj, '__class__') and 'Url' in obj.__class__.__name__:
#             return str(obj)
#         else:
#             return obj
    
#     lead_dict = convert_urls(lead_dict)
    
#     result = await db.leads.insert_one(lead_dict)
#     return str(result.inserted_id)








# """
# Enhanced Website Analysis API Routes with Multi-Page Analysis
# """
# from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
# from datetime import datetime
# from bson import ObjectId
# from typing import Optional

# from app.models import AnalyzeRequest, AnalyzeResponse, AnalysisResult, Lead, CallStatus
# from app.config import get_db
# from app.services.scraper import scrape_website, scrape_website_deep
# from app.services.scoring import (
#     analyze_ai_visibility,
#     analyze_ai_visibility_deep,
#     analyze_seo,
#     analyze_seo_enhanced
# )
# from app.utils import logger, calculate_overall_score, normalize_phone

# router = APIRouter()


# @router.post("/", response_model=AnalyzeResponse)
# async def analyze_website_quick(
#     request: AnalyzeRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     Quick website analysis (homepage only)
#     Fast preview for immediate user feedback
#     """
#     try:
#         logger.info(f"Starting quick analysis for: {request.website_url}")
        
#         # Scrape homepage only
#         scraped_data = await scrape_website(str(request.website_url))
        
#         if not scraped_data.get("success"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to scrape website. Please check the URL."
#             )
        
#         # AI visibility analysis
#         ai_analysis = await analyze_ai_visibility(scraped_data)
        
#         # SEO analysis
#         seo_analysis = await analyze_seo(str(request.website_url))
        
#         # Calculate scores
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )
        
#         # Create analysis result
#         analysis_result = AnalysisResult(
#             website_url=request.website_url,
#             ai_visibility_score=ai_analysis.get("score", 0),
#             seo_score=seo_analysis.get("score", 0),
#             overall_score=overall_score,
#             critical_issues=ai_analysis.get("critical_issues", []),
#             warnings=ai_analysis.get("warnings", []),
#             recommendations=ai_analysis.get("recommendations", []),
#             schema_markup=ai_analysis.get("schema_markup", {}),
#             mobile_optimization=seo_analysis.get("mobile", {}),
#             page_speed=seo_analysis.get("page_speed", {}),
#             ai_readability=ai_analysis.get("readability", {}),
#             analyzed_at=datetime.utcnow()
#         )
        
#         # Save to database
#         lead_id = await save_lead_to_db(request, analysis_result)
        
#         logger.info(f"Quick analysis completed. Lead ID: {lead_id}")
        
#         return AnalyzeResponse(
#             success=True,
#             message="Quick analysis completed successfully",
#             lead_id=lead_id,
#             analysis=analysis_result
#         )
        
#     except Exception as e:
#         logger.error(f"Quick analysis failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# @router.post("/deep")
# async def analyze_website_deep_route(
#     request: AnalyzeRequest,
#     max_pages: int = Query(10, ge=1, le=50, description="Maximum pages to analyze"),
#     background_tasks: BackgroundTasks = None
# ):
#     """
#     Deep website analysis (multi-page crawling)
    
#     Analyzes:
#     - Multiple pages (up to max_pages)
#     - Site-wide SEO health
#     - Page-by-page breakdown
#     - Comprehensive recommendations
    
#     Takes longer but provides complete site audit
#     """
#     try:
#         logger.info(f"Starting DEEP analysis for: {request.website_url} (max {max_pages} pages)")
        
#         # Deep scrape with multi-page crawling
#         scraped_data = await scrape_website_deep(
#             str(request.website_url),
#             max_pages=max_pages,
#             include_subpages=True
#         )
        
#         if not scraped_data.get("success"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to scrape website. Please check the URL."
#             )
        
#         logger.info(f"Scraped {scraped_data.get('total_pages_analyzed', 0)} pages")
        
#         # Deep AI visibility analysis
#         ai_analysis = await analyze_ai_visibility_deep(scraped_data)
        
#         # Enhanced SEO analysis
#         first_page = scraped_data.get("pages", [{}])[0] if scraped_data.get("pages") else {}
#         seo_analysis = await analyze_seo_enhanced(
#             str(request.website_url),
#             page_data=first_page
#         )
        
#         # Calculate comprehensive scores
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )
        
#         # Build comprehensive analysis result
#         analysis_result = {
#             "website_url": str(request.website_url),
#             "analysis_type": "deep",
#             "total_pages_analyzed": scraped_data.get("total_pages_analyzed", 0),
            
#             # Scores
#             "ai_visibility_score": ai_analysis.get("score", 0),
#             "homepage_ai_score": ai_analysis.get("homepage_score", 0),
#             "average_page_score": ai_analysis.get("average_page_score", 0),
#             "seo_score": seo_analysis.get("score", 0),
#             "seo_health_score": seo_analysis.get("seo_health_score", 0),
#             "overall_score": overall_score,
            
#             # Issues and recommendations
#             "critical_issues": ai_analysis.get("critical_issues", []),
#             "warnings": ai_analysis.get("warnings", []),
#             "recommendations": ai_analysis.get("recommendations", []),
            
#             # Detailed metrics
#             "schema_markup": ai_analysis.get("schema_markup", {}),
#             "site_metrics": ai_analysis.get("site_metrics", {}),
#             "mobile_optimization": seo_analysis.get("mobile", {}),
#             "page_speed": seo_analysis.get("page_speed", {}),
#             "technical_seo": seo_analysis.get("technical_seo", {}),
            
#             # Page breakdown
#             "page_scores": ai_analysis.get("page_scores", []),
#             "pages_detail": scraped_data.get("pages", []),  # All pages detail
            
#             "analyzed_at": datetime.utcnow().isoformat()
#         }
        
#         # Save enhanced lead data
#         db = get_db()
#         lead_data = {
#             "business_name": request.business_name,
#             "website_url": str(request.website_url),
#             "phone_number": normalize_phone(request.phone_number),
#             "city": request.city,
#             "state": request.state,
#             "industry": request.industry,
#             "ai_visibility_score": ai_analysis.get("score", 0),
#             "seo_score": seo_analysis.get("score", 0),
#             "overall_score": overall_score,
#             "top_issues": ai_analysis.get("critical_issues", [])[:5],
#             "analysis_data": analysis_result,
#             "analysis_type": "deep",
#             "call_status": CallStatus.PENDING,
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
        
#         result = await db.leads.insert_one(lead_data)
#         lead_id = str(result.inserted_id)
        
#         logger.info(f"Deep analysis completed. Lead ID: {lead_id}")
        
#         return {
#             "success": True,
#             "message": f"Deep analysis completed - {scraped_data.get('total_pages_analyzed', 0)} pages analyzed",
#             "lead_id": lead_id,
#             "analysis": analysis_result
#         }
        
#     except Exception as e:
#         import traceback
#         logger.error(f"Deep analysis failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Deep analysis failed: {str(e)}")


# @router.get("/{lead_id}")
# async def get_analysis(lead_id: str):
#     """Get analysis results for a specific lead"""
#     try:
#         db = get_db()
#         lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
#         if not lead:
#             raise HTTPException(status_code=404, detail="Lead not found")
        
#         # Convert ObjectId to string
#         lead["_id"] = str(lead["_id"])
        
#         return {
#             "success": True,
#             "lead_id": lead_id,
#             "business_name": lead.get("business_name"),
#             "website_url": lead.get("website_url"),
#             "analysis_type": lead.get("analysis_type", "quick"),
#             "scores": {
#                 "ai_visibility": lead.get("ai_visibility_score"),
#                 "seo": lead.get("seo_score"),
#                 "overall": lead.get("overall_score")
#             },
#             "top_issues": lead.get("top_issues", []),
#             "analysis": lead.get("analysis_data", {})
#         }
        
#     except Exception as e:
#         logger.error(f"Failed to get analysis: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{lead_id}/pages")
# async def get_page_breakdown(lead_id: str):
#     """Get page-by-page analysis breakdown"""
#     try:
#         db = get_db()
#         lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
#         if not lead:
#             raise HTTPException(status_code=404, detail="Lead not found")
        
#         analysis_data = lead.get("analysis_data", {})
        
#         return {
#             "success": True,
#             "lead_id": lead_id,
#             "total_pages": analysis_data.get("total_pages_analyzed", 1),
#             "page_scores": analysis_data.get("page_scores", []),
#             "pages_detail": analysis_data.get("pages_detail", [])
#         }
        
#     except Exception as e:
#         logger.error(f"Failed to get page breakdown: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# async def save_lead_to_db(request: AnalyzeRequest, analysis_result: AnalysisResult) -> str:
#     """Helper function to save lead to database"""
#     db = get_db()
#     lead_data = Lead(
#         business_name=request.business_name,
#         website_url=request.website_url,
#         phone_number=normalize_phone(request.phone_number),
#         city=request.city,
#         state=request.state,
#         industry=request.industry,
#         ai_visibility_score=analysis_result.ai_visibility_score,
#         seo_score=analysis_result.seo_score,
#         top_issues=analysis_result.critical_issues[:5],
#         analysis_data=analysis_result.model_dump(),
#         call_status=CallStatus.PENDING,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
    
#     lead_dict = lead_data.model_dump()
    
#     # Convert URLs to strings
#     def convert_urls(obj):
#         if isinstance(obj, dict):
#             return {k: convert_urls(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [convert_urls(item) for item in obj]
#         elif hasattr(obj, '__class__') and 'Url' in obj.__class__.__name__:
#             return str(obj)
#         else:
#             return obj
    
#     lead_dict = convert_urls(lead_dict)
    
#     result = await db.leads.insert_one(lead_dict)
#     return str(result.inserted_id)





"""
Enhanced Website Analysis API Routes with Multi-Page Analysis
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from datetime import datetime
from bson import ObjectId
from typing import Optional
from typing import Optional  # Add this if missing
from app.models import AnalyzeRequest, AnalyzeResponse, AnalysisResult, Lead, CallStatus
from app.config import get_db
from app.services.scraper import scrape_website, scrape_website_deep
from app.services.scoring import (
    analyze_ai_visibility,
    analyze_ai_visibility_deep,
    analyze_seo,
    analyze_seo_enhanced
)
from app.utils import logger, calculate_overall_score, normalize_phone

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
async def analyze_website_quick(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None
):
    """
    Quick website analysis (homepage only)
    Fast preview for immediate user feedback
    """
    try:
        logger.info(f"Starting quick analysis for: {request.website_url} (User: {user_id})")
        
        # Scrape homepage only
        scraped_data = await scrape_website(str(request.website_url))
        
        if not scraped_data.get("success"):
            raise HTTPException(
                status_code=400,
                detail="Failed to scrape website. Please check the URL."
            )
        
        # AI visibility analysis
        ai_analysis = await analyze_ai_visibility(scraped_data)
        
        # SEO analysis
        seo_analysis = await analyze_seo(str(request.website_url))
        
        # Calculate scores
        overall_score = calculate_overall_score(
            ai_analysis.get("score", 0),
            seo_analysis.get("score", 0)
        )
        
        # Create analysis result
        analysis_result = AnalysisResult(
            website_url=request.website_url,
            ai_visibility_score=ai_analysis.get("score", 0),
            seo_score=seo_analysis.get("score", 0),
            overall_score=overall_score,
            critical_issues=ai_analysis.get("critical_issues", []),
            warnings=ai_analysis.get("warnings", []),
            recommendations=ai_analysis.get("recommendations", []),
            schema_markup=ai_analysis.get("schema_markup", {}),
            mobile_optimization=seo_analysis.get("mobile", {}),
            page_speed=seo_analysis.get("page_speed", {}),
            ai_readability=ai_analysis.get("readability", {}),
            analyzed_at=datetime.utcnow()
        )
        
        # Save to database
        lead_id = await save_lead_to_db(request, analysis_result, user_id)
        
        logger.info(f"Quick analysis completed. Lead ID: {lead_id}")
        
        return AnalyzeResponse(
            success=True,
            message="Quick analysis completed successfully",
            lead_id=lead_id,
            analysis=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Quick analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/deep")
async def analyze_website_deep_route(
    request: AnalyzeRequest,
    max_pages: int = Query(10, ge=1, le=50, description="Maximum pages to analyze"),
    background_tasks: BackgroundTasks = None,
    user_id: Optional[str] = None
):
    """
    Deep website analysis (multi-page crawling)
    
    Analyzes:
    - Multiple pages (up to max_pages)
    - Site-wide SEO health
    - Page-by-page breakdown with detailed issues
    - Comprehensive recommendations per page
    
    Takes longer but provides complete site audit
    """
    try:
        logger.info(f"Starting DEEP analysis for: {request.website_url} (max {max_pages} pages, User: {user_id})")
        
        # Deep scrape with multi-page crawling
        scraped_data = await scrape_website_deep(
            str(request.website_url),
            max_pages=max_pages,
            include_subpages=True
        )
        
        if not scraped_data.get("success"):
            raise HTTPException(
                status_code=400,
                detail="Failed to scrape website. Please check the URL."
            )
        
        logger.info(f"Scraped {scraped_data.get('total_pages_analyzed', 0)} pages")
        
        # Deep AI visibility analysis
        ai_analysis = await analyze_ai_visibility_deep(scraped_data)
        
        # Enhanced SEO analysis
        first_page = scraped_data.get("pages", [{}])[0] if scraped_data.get("pages") else {}
        seo_analysis = await analyze_seo_enhanced(
            str(request.website_url),
            page_data=first_page
        )
        
        # Calculate comprehensive scores
        overall_score = calculate_overall_score(
            ai_analysis.get("score", 0),
            seo_analysis.get("score", 0)
        )
        
        # Generate detailed page-level issues
        pages_with_issues = generate_page_level_issues(scraped_data.get("pages", []))
        
        # Build comprehensive analysis result
        analysis_result = {
            "website_url": str(request.website_url),
            "analysis_type": "deep",
            "total_pages_analyzed": scraped_data.get("total_pages_analyzed", 0),
            
            # Scores
            "ai_visibility_score": ai_analysis.get("score", 0),
            "homepage_ai_score": ai_analysis.get("homepage_score", 0),
            "average_page_score": ai_analysis.get("average_page_score", 0),
            "seo_score": seo_analysis.get("score", 0),
            "seo_health_score": seo_analysis.get("seo_health_score", 0),
            "overall_score": overall_score,
            
            # Issues and recommendations
            "critical_issues": ai_analysis.get("critical_issues", []),
            "warnings": ai_analysis.get("warnings", []),
            "recommendations": ai_analysis.get("recommendations", []),
            
            # Detailed metrics
            "schema_markup": ai_analysis.get("schema_markup", {}),
            "site_metrics": ai_analysis.get("site_metrics", {}),
            "mobile_optimization": seo_analysis.get("mobile", {}),
            "page_speed": seo_analysis.get("page_speed", {}),
            "technical_seo": seo_analysis.get("technical_seo", {}),
            
            # Page breakdown with detailed issues
            "page_scores": ai_analysis.get("page_scores", []),
            "pages_detail": pages_with_issues,  # Enhanced with per-page issues
            
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        # Save enhanced lead data
        db = get_db()
        lead_data = {
            "user_id": user_id,
            "business_name": request.business_name,
            "website_url": str(request.website_url),
            "phone_number": normalize_phone(request.phone_number),
            "city": request.city,
            "state": request.state,
            "industry": request.industry,
            "ai_visibility_score": ai_analysis.get("score", 0),
            "seo_score": seo_analysis.get("score", 0),
            "overall_score": overall_score,
            "top_issues": ai_analysis.get("critical_issues", [])[:5],
            "analysis_data": analysis_result,
            "analysis_type": "deep",
            "call_status": CallStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.leads.insert_one(lead_data)
        lead_id = str(result.inserted_id)
        
        logger.info(f"Deep analysis completed. Lead ID: {lead_id}")
        
        return {
            "success": True,
            "message": f"Deep analysis completed - {scraped_data.get('total_pages_analyzed', 0)} pages analyzed",
            "lead_id": lead_id,
            "analysis": analysis_result
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Deep analysis failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Deep analysis failed: {str(e)}")


def generate_page_level_issues(pages):
    """Generate detailed issues for each page"""
    enhanced_pages = []
    
    for page in pages:
        # Safely extract all data
        page_url = page.get("url", "")
        page_title = page.get("title", "") or "Untitled"
        meta_desc = page.get("meta_description", "") or ""
        content = page.get("content", "") or ""
        headings = page.get("headings", {}) or {}
        images = page.get("images", []) or []
        links = page.get("links", []) or []
        schema = page.get("schema_markup", []) or []
        
        content_length = len(content)
        h1_list = headings.get("h1", []) or []
        h2_list = headings.get("h2", []) or []
        
        critical_issues = []
        warnings = []
        suggestions = []
        
        # CRITICAL ISSUES
        if not page_title or len(page_title) < 10:
            critical_issues.append({
                "type": "missing_title",
                "severity": "critical",
                "message": "Page title missing or too short",
                "impact": "AI cannot understand page content",
                "fix": "Add descriptive title (50-60 chars) with keywords"
            })
        
        if len(meta_desc) < 50:
            critical_issues.append({
                "type": "missing_meta_description",
                "severity": "critical",
                "message": "Meta description missing or too short",
                "impact": "Poor CTR and AI understanding",
                "fix": "Add meta description (150-160 chars)"
            })
        
        if content_length < 300:
            critical_issues.append({
                "type": "thin_content",
                "severity": "critical",
                "message": f"Very thin content ({content_length} chars)",
                "impact": "Insufficient content for AI extraction",
                "fix": "Expand to 800-1000 words minimum"
            })
        
        if len(h1_list) == 0:
            critical_issues.append({
                "type": "missing_h1",
                "severity": "critical",
                "message": "No H1 heading found",
                "impact": "Cannot identify main topic",
                "fix": "Add single H1 describing page topic"
            })
        
        if len(h1_list) > 1:
            critical_issues.append({
                "type": "multiple_h1",
                "severity": "critical",
                "message": f"Multiple H1 headings ({len(h1_list)})",
                "impact": "Confuses AI about page priority",
                "fix": "Use only ONE H1 per page"
            })
        
        if len(schema) == 0:
            critical_issues.append({
                "type": "missing_schema",
                "severity": "critical",
                "message": "No structured data found",
                "impact": "AI cannot extract structured info",
                "fix": "Add relevant schema markup"
            })
        
        # WARNINGS
        if len(page_title) > 60:
            warnings.append({
                "type": "long_title",
                "severity": "warning",
                "message": f"Title too long ({len(page_title)} chars)",
                "impact": "May be truncated in search results",
                "fix": "Reduce to 50-60 characters"
            })
        
        if len(meta_desc) > 160:
            warnings.append({
                "type": "long_meta_description",
                "severity": "warning",
                "message": f"Meta description too long ({len(meta_desc)} chars)",
                "impact": "Will be truncated",
                "fix": "Reduce to 150-160 characters"
            })
        
        if len(h2_list) == 0:
            warnings.append({
                "type": "missing_h2",
                "severity": "warning",
                "message": "No H2 headings found",
                "impact": "Poor content structure",
                "fix": "Add 3-5 H2 headings for sections"
            })
        
        images_no_alt = []
        for img in images:
            if isinstance(img, dict) and not img.get("alt"):
                images_no_alt.append(img)
            elif isinstance(img, str):
                # If image is just a URL string, it has no alt text
                images_no_alt.append(img)
        
        if len(images_no_alt) > 0:
            warnings.append({
                "type": "images_missing_alt",
                "severity": "warning",
                "message": f"{len(images_no_alt)} images missing alt text",
                "impact": "Reduced accessibility",
                "fix": "Add descriptive alt text to all images"
            })
        
        if 300 <= content_length < 800:
            warnings.append({
                "type": "short_content",
                "severity": "warning",
                "message": f"Content relatively short ({content_length} chars)",
                "impact": "May not be comprehensive enough",
                "fix": "Consider expanding to 800+ words"
            })
        
        # SUGGESTIONS
        if "faq" not in str(schema).lower():
            suggestions.append({
                "type": "add_faq_schema",
                "severity": "suggestion",
                "message": "Consider adding FAQ schema",
                "benefit": "Increases AI visibility",
                "implementation": "Add FAQ schema for common questions"
            })
        
        internal_links = []
        for lnk in links:
            if isinstance(lnk, dict) and lnk.get("type") == "internal":
                internal_links.append(lnk)
        
        if len(internal_links) < 3:
            suggestions.append({
                "type": "add_internal_links",
                "severity": "suggestion",
                "message": "Limited internal linking",
                "benefit": "Improves site navigation and authority",
                "implementation": f"Add 3-5 internal links (current: {len(internal_links)})"
            })
        
        if "video" not in content.lower():
            suggestions.append({
                "type": "add_video",
                "severity": "suggestion",
                "message": "No video content detected",
                "benefit": "Increases engagement and time on page",
                "implementation": "Add relevant video with transcript"
            })
        
        if len(images) < 2:
            suggestions.append({
                "type": "add_images",
                "severity": "suggestion",
                "message": "Limited visual content",
                "benefit": "Improves engagement",
                "implementation": f"Add 2-3 images (current: {len(images)})"
            })
        
        suggestions.append({
            "type": "related_content",
            "severity": "suggestion",
            "message": "Add related content section",
            "benefit": "Reduces bounce rate",
            "implementation": "Link to 3-5 related pages"
        })
        
        # Calculate page score
        page_score = 100.0
        page_score -= len(critical_issues) * 15
        page_score -= len(warnings) * 5
        page_score -= len(suggestions) * 2
        page_score = max(0.0, min(100.0, page_score))
        
        enhanced_page = {
            **page,
            "page_score": page_score,
            "total_issues": len(critical_issues) + len(warnings),
            "critical_issues": critical_issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "issue_summary": {
                "critical_count": len(critical_issues),
                "warning_count": len(warnings),
                "suggestion_count": len(suggestions)
            }
        }
        
        enhanced_pages.append(enhanced_page)
    
    return enhanced_pages


@router.get("/{lead_id}")
async def get_analysis(lead_id: str):
    """Get analysis results for a specific lead"""
    try:
        db = get_db()
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead["_id"] = str(lead["_id"])
        
        return {
            "success": True,
            "lead_id": lead_id,
            "user_id": lead.get("user_id"),
            "business_name": lead.get("business_name"),
            "website_url": lead.get("website_url"),
            "analysis_type": lead.get("analysis_type", "quick"),
            "scores": {
                "ai_visibility": lead.get("ai_visibility_score"),
                "seo": lead.get("seo_score"),
                "overall": lead.get("overall_score")
            },
            "top_issues": lead.get("top_issues", []),
            "analysis": lead.get("analysis_data", {})
        }
        
    except Exception as e:
        logger.error(f"Failed to get analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}/pages")
async def get_page_breakdown(lead_id: str):
    """Get page-by-page analysis breakdown with detailed issues"""
    try:
        db = get_db()
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        analysis_data = lead.get("analysis_data", {})
        pages_detail = analysis_data.get("pages_detail", [])
        
        total_critical = sum(p.get("issue_summary", {}).get("critical_count", 0) for p in pages_detail)
        total_warnings = sum(p.get("issue_summary", {}).get("warning_count", 0) for p in pages_detail)
        total_suggestions = sum(p.get("issue_summary", {}).get("suggestion_count", 0) for p in pages_detail)
        
        avg_score = 0
        if len(pages_detail) > 0:
            avg_score = sum(p.get("page_score", 0) for p in pages_detail) / len(pages_detail)
        
        return {
            "success": True,
            "lead_id": lead_id,
            "total_pages": analysis_data.get("total_pages_analyzed", 1),
            "summary": {
                "total_critical_issues": total_critical,
                "total_warnings": total_warnings,
                "total_suggestions": total_suggestions,
                "average_page_score": avg_score
            },
            "page_scores": analysis_data.get("page_scores", []),
            "pages_detail": pages_detail
        }
        
    except Exception as e:
        logger.error(f"Failed to get page breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def save_lead_to_db(request: AnalyzeRequest, analysis_result: AnalysisResult, user_id: Optional[str] = None) -> str:
    """Helper function to save lead to database"""
    db = get_db()
    lead_data = Lead(
        user_id=user_id,
        business_name=request.business_name,
        website_url=request.website_url,
        phone_number=normalize_phone(request.phone_number),
        city=request.city,
        state=request.state,
        industry=request.industry,
        ai_visibility_score=analysis_result.ai_visibility_score,
        seo_score=analysis_result.seo_score,
        top_issues=analysis_result.critical_issues[:5],
        analysis_data=analysis_result.model_dump(),
        call_status=CallStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    lead_dict = lead_data.model_dump()
    
    def convert_urls(obj):
        if isinstance(obj, dict):
            return {k: convert_urls(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_urls(item) for item in obj]
        elif hasattr(obj, '__class__') and 'Url' in obj.__class__.__name__:
            return str(obj)
        else:
            return obj
    
    lead_dict = convert_urls(lead_dict)
    
    result = await db.leads.insert_one(lead_dict)
    return str(result.inserted_id)