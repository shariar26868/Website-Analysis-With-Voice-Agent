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
        
#         result = await db.leads.insert_one(lead_data.model_dump())
#         lead_id = str(result.inserted_id)
        
#         logger.info(f"Analysis completed. Lead ID: {lead_id}")
        
#         return AnalyzeResponse(
#             success=True,
#             message="Analysis completed successfully",
#             lead_id=lead_id,
#             analysis=analysis_result
#         )
        
#     except Exception as e:
#         logger.error(f"Analysis failed: {str(e)}")
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
# Website Analysis API Routes
# """
# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from datetime import datetime
# from bson import ObjectId

# from app.models import (
#     AnalyzeRequest,
#     AnalyzeResponse,
#     AnalysisResult,
#     Lead,
#     CallStatus
# )
# from app.config import get_db
# from app.services.scraper import scrape_website
# from app.services.scoring import analyze_ai_visibility, analyze_seo
# from app.utils import logger, calculate_overall_score, normalize_phone

# router = APIRouter()


# @router.post("/", response_model=AnalyzeResponse)
# async def analyze_website(
#     request: AnalyzeRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     Analyze a website and return AI visibility + SEO score
#     """
#     try:
#         logger.info(f"Starting analysis for: {request.website_url}")

#         # --------------------------------------------------
#         # STEP 1: SCRAPE WEBSITE (async)
#         # --------------------------------------------------
#         logger.info("Scraping website...")
#         scraped_data = await scrape_website(str(request.website_url))

#         if not scraped_data or not isinstance(scraped_data, dict):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Scraper returned invalid response"
#             )

#         if scraped_data.get("success") is not True:
#             raise HTTPException(
#                 status_code=400,
#                 detail=scraped_data.get("error", "Failed to scrape website")
#             )

#         # --------------------------------------------------
#         # STEP 2: AI VISIBILITY ANALYSIS
#         # --------------------------------------------------
#         try:
#             logger.info("Analyzing AI visibility...")
#             ai_analysis = await analyze_ai_visibility(scraped_data)
#         except Exception as e:
#             logger.error(f"AI visibility failed: {repr(e)}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"AI visibility analysis failed: {repr(e)}"
#             )

#         # --------------------------------------------------
#         # STEP 3: SEO ANALYSIS
#         # --------------------------------------------------
#         try:
#             logger.info("Analyzing SEO...")
#             seo_analysis = await analyze_seo(str(request.website_url))
#         except Exception as e:
#             logger.error(f"SEO analysis failed: {repr(e)}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"SEO analysis failed: {repr(e)}"
#             )

#         # --------------------------------------------------
#         # STEP 4: CALCULATE OVERALL SCORE
#         # --------------------------------------------------
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )

#         # --------------------------------------------------
#         # STEP 5: BUILD ANALYSIS RESULT
#         # --------------------------------------------------
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

#         # --------------------------------------------------
#         # STEP 6: SAVE LEAD TO DATABASE
#         # --------------------------------------------------
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

#         result = await db.leads.insert_one(lead_data.model_dump())
#         lead_id = str(result.inserted_id)

#         logger.info(f"Analysis completed successfully. Lead ID: {lead_id}")

#         return AnalyzeResponse(
#             success=True,
#             message="Analysis completed successfully",
#             lead_id=lead_id,
#             analysis=analysis_result
#         )

#     except HTTPException:
#         raise

#     except Exception as e:
#         import traceback
#         logger.error("Unhandled analysis error")
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=500,
#             detail=f"Analysis failed: {repr(e)}"
#         )


# @router.get("/{lead_id}")
# async def get_analysis(lead_id: str):
#     """Get saved analysis by lead ID"""
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

#     except HTTPException:
#         raise

#     except Exception as e:
#         logger.error(f"Failed to fetch analysis: {repr(e)}")
#         raise HTTPException(status_code=500, detail="Failed to fetch analysis")


# @router.get("/test")
# async def test_analysis():
#     """Quick scraper test"""
#     try:
#         result = await scrape_website("https://example.com")
#         return {
#             "success": True,
#             "scraper_working": result.get("success", False),
#             "result": result
#         }
#     except Exception as e:
#         import traceback
#         return {
#             "success": False,
#             "error": repr(e),
#             "traceback": traceback.format_exc()
#         }





# """
# Website Analysis API Routes
# """
# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from datetime import datetime
# from bson import ObjectId

# from app.models import (
#     AnalyzeRequest,
#     AnalyzeResponse,
#     AnalysisResult,
#     Lead,
#     CallStatus
# )
# from app.config import get_db
# from app.services.scraper import scrape_website
# from app.services.scoring import analyze_ai_visibility, analyze_seo
# from app.utils import logger, calculate_overall_score, normalize_phone

# router = APIRouter()


# @router.post("/", response_model=AnalyzeResponse)
# async def analyze_website(
#     request: AnalyzeRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     Analyze a website and return AI visibility + SEO score
#     """
#     try:
#         website_url_str = str(request.website_url)
#         logger.info(f"Starting analysis for: {website_url_str}")

#         # --------------------------------------------------
#         # STEP 1: SCRAPE WEBSITE (async)
#         # --------------------------------------------------
#         logger.info("Scraping website...")
#         scraped_data = await scrape_website(website_url_str)

#         if not scraped_data or not isinstance(scraped_data, dict):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Scraper returned invalid response"
#             )

#         if scraped_data.get("success") is not True:
#             raise HTTPException(
#                 status_code=400,
#                 detail=scraped_data.get("error", "Failed to scrape website")
#             )

#         # --------------------------------------------------
#         # STEP 2: AI VISIBILITY ANALYSIS
#         # --------------------------------------------------
#         try:
#             logger.info("Analyzing AI visibility...")
#             ai_analysis = await analyze_ai_visibility(scraped_data)
#         except Exception as e:
#             logger.error(f"AI visibility failed: {repr(e)}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"AI visibility analysis failed: {repr(e)}"
#             )

#         # --------------------------------------------------
#         # STEP 3: SEO ANALYSIS
#         # --------------------------------------------------
#         try:
#             logger.info("Analyzing SEO...")
#             seo_analysis = await analyze_seo(website_url_str)
#         except Exception as e:
#             logger.error(f"SEO analysis failed: {repr(e)}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"SEO analysis failed: {repr(e)}"
#             )

#         # --------------------------------------------------
#         # STEP 4: CALCULATE OVERALL SCORE
#         # --------------------------------------------------
#         overall_score = calculate_overall_score(
#             ai_analysis.get("score", 0),
#             seo_analysis.get("score", 0)
#         )

#         # --------------------------------------------------
#         # STEP 5: BUILD ANALYSIS RESULT
#         # --------------------------------------------------
#         analysis_result = AnalysisResult(
#             website_url=website_url_str,  # convert Url -> str
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

#         # --------------------------------------------------
#         # STEP 6: SAVE LEAD TO DATABASE
#         # --------------------------------------------------
#         db = get_db()

#         lead_data = Lead(
#             business_name=request.business_name,
#             website_url=website_url_str,
#             phone_number=normalize_phone(request.phone_number),
#             city=request.city,
#             state=request.state,
#             industry=request.industry,
#             ai_visibility_score=analysis_result.ai_visibility_score,
#             seo_score=analysis_result.seo_score,
#             top_issues=analysis_result.critical_issues[:5],
#             analysis_data=analysis_result.dict(),  # Pydantic dict
#             call_status=CallStatus.PENDING,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )

#         result = await db.leads.insert_one(lead_data.dict())
#         lead_id = str(result.inserted_id)

#         logger.info(f"Analysis completed successfully. Lead ID: {lead_id}")

#         return AnalyzeResponse(
#             success=True,
#             message="Analysis completed successfully",
#             lead_id=lead_id,
#             analysis=analysis_result
#         )

#     except HTTPException:
#         raise

#     except Exception as e:
#         import traceback
#         logger.error("Unhandled analysis error")
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=500,
#             detail=f"Analysis failed: {repr(e)}"
#         )


# @router.get("/{lead_id}")
# async def get_analysis(lead_id: str):
#     """Get saved analysis by lead ID"""
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

#     except HTTPException:
#         raise

#     except Exception as e:
#         logger.error(f"Failed to fetch analysis: {repr(e)}")
#         raise HTTPException(status_code=500, detail="Failed to fetch analysis")


# @router.get("/test")
# async def test_analysis():
#     """Quick scraper test"""
#     try:
#         result = await scrape_website("https://example.com")
#         return {
#             "success": True,
#             "scraper_working": result.get("success", False),
#             "result": result
#         }
#     except Exception as e:
#         import traceback
#         return {
#             "success": False,
#             "error": repr(e),
#             "traceback": traceback.format_exc()
#         }




"""
Website Analysis API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from bson import ObjectId

from app.models import AnalyzeRequest, AnalyzeResponse, AnalysisResult, Lead, CallStatus
from app.config import get_db
from app.services.scraper import scrape_website
from app.services.scoring import analyze_ai_visibility, analyze_seo
from app.utils import logger, calculate_overall_score, normalize_phone

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
async def analyze_website(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Analyze a website and return AI visibility score
    
    Flow:
    1. Scrape website
    2. Analyze AI visibility (ChatGPT)
    3. Analyze SEO (PageSpeed)
    4. Save lead to database
    5. Return instant preview score
    """
    try:
        logger.info(f"Starting analysis for: {request.website_url}")
        
        # Step 1: Scrape website
        logger.info("Scraping website...")
        scraped_data = await scrape_website(str(request.website_url))
        
        if not scraped_data.get("success"):
            raise HTTPException(
                status_code=400,
                detail="Failed to scrape website. Please check the URL."
            )
        
        # Step 2: Analyze AI Visibility (ChatGPT)
        logger.info("Analyzing AI visibility...")
        ai_analysis = await analyze_ai_visibility(scraped_data)
        
        # Step 3: Analyze SEO (PageSpeed)
        logger.info("Analyzing SEO...")
        seo_analysis = await analyze_seo(str(request.website_url))
        
        # Calculate overall score
        overall_score = calculate_overall_score(
            ai_analysis.get("score", 0),
            seo_analysis.get("score", 0)
        )
        
        # Step 4: Create analysis result
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
        
        # Step 5: Save lead to database
        db = get_db()
        lead_data = Lead(
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
        
        # Convert Pydantic models to dict and handle URL serialization
        lead_dict = lead_data.model_dump()
        
        # Convert all URL objects to strings
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
        lead_id = str(result.inserted_id)
        
        logger.info(f"Analysis completed. Lead ID: {lead_id}")
        
        return AnalyzeResponse(
            success=True,
            message="Analysis completed successfully",
            lead_id=lead_id,
            analysis=analysis_result
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Analysis failed: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{lead_id}")
async def get_analysis(lead_id: str):
    """Get analysis results for a specific lead"""
    try:
        db = get_db()
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "business_name": lead.get("business_name"),
            "website_url": lead.get("website_url"),
            "analysis": lead.get("analysis_data", {})
        }
        
    except Exception as e:
        logger.error(f"Failed to get analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))