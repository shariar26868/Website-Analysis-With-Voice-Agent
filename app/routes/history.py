"""
Analysis History API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.config import get_db
from app.utils import logger

router = APIRouter()


@router.get("/")
async def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    industry: Optional[str] = None,
    min_score: Optional[int] = None
):
    """
    Get analysis history with pagination and filters
    
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum records to return
    - industry: Filter by industry
    - min_score: Minimum AI visibility score
    """
    try:
        db = get_db()
        
        # Build query filter
        query_filter = {}
        
        if industry:
            query_filter["industry"] = {"$regex": industry, "$options": "i"}
        
        if min_score is not None:
            query_filter["ai_visibility_score"] = {"$gte": min_score}
        
        # Get total count
        total = await db.leads.count_documents(query_filter)
        
        # Get paginated results
        cursor = db.leads.find(query_filter).sort("created_at", -1).skip(skip).limit(limit)
        leads = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for lead in leads:
            lead["_id"] = str(lead["_id"])
        
        logger.info(f"Retrieved {len(leads)} analysis records")
        
        return {
            "success": True,
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(leads),
            "analyses": leads
        }
        
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """Get overall statistics"""
    try:
        db = get_db()
        
        # Total leads
        total_leads = await db.leads.count_documents({})
        
        # Average scores
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_ai_score": {"$avg": "$ai_visibility_score"},
                    "avg_seo_score": {"$avg": "$seo_score"}
                }
            }
        ]
        
        cursor = db.leads.aggregate(pipeline)
        stats = await cursor.to_list(length=1)
        
        avg_scores = stats[0] if stats else {
            "avg_ai_score": 0,
            "avg_seo_score": 0
        }
        
        # Calls statistics
        total_calls = await db.call_logs.count_documents({})
        completed_calls = await db.call_logs.count_documents({"status": "completed"})
        
        # Top industries
        industry_pipeline = [
            {"$match": {"industry": {"$ne": None}}},
            {"$group": {"_id": "$industry", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        cursor = db.leads.aggregate(industry_pipeline)
        top_industries = await cursor.to_list(length=5)
        
        return {
            "success": True,
            "total_leads": total_leads,
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "average_ai_score": round(avg_scores.get("avg_ai_score", 0), 2),
            "average_seo_score": round(avg_scores.get("avg_seo_score", 0), 2),
            "top_industries": top_industries
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    


from pydantic import BaseSettings
from typing import Optional 