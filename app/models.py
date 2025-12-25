# """
# MongoDB Models and Schemas
# """
# from pydantic import BaseModel, Field, HttpUrl
# from typing import Optional, List, Dict, Any
# from datetime import datetime
# from enum import Enum


# # Enums
# class CallStatus(str, Enum):
#     PENDING = "pending"
#     IN_PROGRESS = "in_progress"
#     COMPLETED = "completed"
#     FAILED = "failed"
#     NO_ANSWER = "no_answer"


# class CallOutcome(str, Enum):
#     SUCCESS = "success"
#     CALLBACK_NEEDED = "callback_needed"
#     NOT_INTERESTED = "not_interested"
#     NO_ANSWER = "no_answer"


# # Lead Model
# class Lead(BaseModel):
#     business_name: str
#     website_url: HttpUrl
#     phone_number: str
#     city: Optional[str] = None
#     state: Optional[str] = None
#     industry: Optional[str] = None
    
#     # Analysis data
#     ai_visibility_score: Optional[int] = None
#     seo_score: Optional[int] = None
#     top_issues: Optional[List[str]] = []
#     analysis_data: Optional[Dict[str, Any]] = {}
    
#     # Call tracking
#     call_status: CallStatus = CallStatus.PENDING
#     call_attempts: int = 0
#     last_call_date: Optional[datetime] = None
    
#     # Timestamps
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "business_name": "ABC Plumbing",
#                 "website_url": "https://abcplumbing.com",
#                 "phone_number": "+1234567890",
#                 "city": "Miami",
#                 "state": "FL",
#                 "industry": "Plumbing"
#             }
#         }
    
#     def to_mongo_dict(self):
#         """Convert to MongoDB-compatible dict"""
#         data = self.model_dump()
#         # Convert Pydantic URL to string
#         if 'website_url' in data:
#             data['website_url'] = str(data['website_url'])
#         return data


# # Analysis Result Model
# class AnalysisResult(BaseModel):
#     lead_id: Optional[str] = None
#     website_url: HttpUrl
    
#     # Scores
#     ai_visibility_score: int = 0
#     seo_score: int = 0
#     overall_score: int = 0
    
#     # Issues
#     critical_issues: List[str] = []
#     warnings: List[str] = []
#     recommendations: List[str] = []
    
#     # Detailed analysis
#     schema_markup: Optional[Dict[str, Any]] = {}
#     mobile_optimization: Optional[Dict[str, Any]] = {}
#     page_speed: Optional[Dict[str, Any]] = {}
#     ai_readability: Optional[Dict[str, Any]] = {}
    
#     # Metadata
#     analyzed_at: datetime = Field(default_factory=datetime.utcnow)
#     analysis_duration: Optional[float] = None
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "website_url": "https://example.com",
#                 "ai_visibility_score": 45,
#                 "seo_score": 62,
#                 "overall_score": 54,
#                 "critical_issues": [
#                     "Missing schema markup",
#                     "No local business structured data"
#                 ]
#             }
#         }


# # Call Log Model
# class CallLog(BaseModel):
#     lead_id: str
#     call_sid: Optional[str] = None
    
#     # Call details
#     phone_number: str
#     status: CallStatus = CallStatus.PENDING
#     outcome: Optional[CallOutcome] = None
    
#     # Recording
#     recording_url: Optional[str] = None
#     recording_s3_url: Optional[str] = None
#     transcript: Optional[str] = None
    
#     # Conversation
#     conversation_summary: Optional[str] = None
#     key_points: Optional[List[str]] = []
#     objections: Optional[List[str]] = []
    
#     # Timestamps
#     started_at: Optional[datetime] = None
#     ended_at: Optional[datetime] = None
#     duration: Optional[int] = None  # seconds
#     created_at: datetime = Field(default_factory=datetime.utcnow)
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "lead_id": "507f1f77bcf86cd799439011",
#                 "phone_number": "+1234567890",
#                 "status": "completed",
#                 "outcome": "success"
#             }
#         }


# # API Request/Response Schemas
# class AnalyzeRequest(BaseModel):
#     business_name: str
#     website_url: HttpUrl
#     phone_number: str
#     city: Optional[str] = None
#     state: Optional[str] = None
#     industry: Optional[str] = None


# class AnalyzeResponse(BaseModel):
#     success: bool
#     message: str
#     lead_id: str
#     analysis: AnalysisResult


# class SaraCallRequest(BaseModel):
#     lead_id: str
#     phone_number: Optional[str] = None


# class SaraCallResponse(BaseModel):
#     success: bool
#     message: str
#     call_id: str
#     call_status: CallStatus


# class HistoryResponse(BaseModel):
#     total: int
#     analyses: List[AnalysisResult]


# class RecordingResponse(BaseModel):
#     success: bool
#     call_id: str
#     recording_url: Optional[str] = None
#     transcript: Optional[str] = None
#     duration: Optional[int] = None





"""
MongoDB Models and Schemas
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class CallStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"


class CallOutcome(str, Enum):
    SUCCESS = "success"
    CALLBACK_NEEDED = "callback_needed"
    NOT_INTERESTED = "not_interested"
    NO_ANSWER = "no_answer"


# Lead Model
class Lead(BaseModel):
    business_name: str
    website_url: HttpUrl
    phone_number: str
    city: Optional[str] = None
    state: Optional[str] = None
    industry: Optional[str] = None
    
    # Analysis data
    ai_visibility_score: Optional[int] = None
    seo_score: Optional[int] = None
    overall_score: Optional[int] = None  # New field
    top_issues: Optional[List[str]] = []
    analysis_data: Optional[Dict[str, Any]] = {}
    analysis_type: Optional[str] = "quick"  # New field: "quick" or "deep"
    
    # Call tracking
    call_status: CallStatus = CallStatus.PENDING
    call_attempts: int = 0
    last_call_date: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "ABC Plumbing",
                "website_url": "https://abcplumbing.com",
                "phone_number": "+1234567890",
                "city": "Miami",
                "state": "FL",
                "industry": "Plumbing"
            }
        }
    
    def to_mongo_dict(self):
        """Convert to MongoDB-compatible dict"""
        data = self.model_dump()
        # Convert Pydantic URL to string
        if 'website_url' in data:
            data['website_url'] = str(data['website_url'])
        return data


# Analysis Result Model
class AnalysisResult(BaseModel):
    lead_id: Optional[str] = None
    website_url: HttpUrl
    
    # Scores
    ai_visibility_score: int = 0
    seo_score: int = 0
    overall_score: int = 0
    
    # Issues
    critical_issues: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []
    
    # Detailed analysis
    schema_markup: Optional[Dict[str, Any]] = {}
    mobile_optimization: Optional[Dict[str, Any]] = {}
    page_speed: Optional[Dict[str, Any]] = {}
    ai_readability: Optional[Dict[str, Any]] = {}
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_duration: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "website_url": "https://example.com",
                "ai_visibility_score": 45,
                "seo_score": 62,
                "overall_score": 54,
                "critical_issues": [
                    "Missing schema markup",
                    "No local business structured data"
                ]
            }
        }


# Call Log Model
class CallLog(BaseModel):
    lead_id: str
    call_sid: Optional[str] = None
    
    # Call details
    phone_number: str
    status: CallStatus = CallStatus.PENDING
    outcome: Optional[CallOutcome] = None
    
    # Recording
    recording_url: Optional[str] = None
    recording_s3_url: Optional[str] = None
    transcript: Optional[str] = None
    
    # Conversation
    conversation_summary: Optional[str] = None
    key_points: Optional[List[str]] = []
    objections: Optional[List[str]] = []
    
    # Timestamps
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "507f1f77bcf86cd799439011",
                "phone_number": "+1234567890",
                "status": "completed",
                "outcome": "success"
            }
        }


# API Request/Response Schemas
class AnalyzeRequest(BaseModel):
    business_name: str
    website_url: HttpUrl
    phone_number: str
    city: Optional[str] = None
    state: Optional[str] = None
    industry: Optional[str] = None


class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    lead_id: str
    analysis: AnalysisResult


class SaraCallRequest(BaseModel):
    lead_id: str
    phone_number: Optional[str] = None


class SaraCallResponse(BaseModel):
    success: bool
    message: str
    call_id: str
    call_status: CallStatus


class HistoryResponse(BaseModel):
    total: int
    analyses: List[AnalysisResult]


class RecordingResponse(BaseModel):
    success: bool
    call_id: str
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    duration: Optional[int] = None