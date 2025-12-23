"""
AWS S3 Storage Service - Recording Storage
"""
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings
from app.utils import logger
from app.services.twilio_service import download_recording

# Initialize S3 client
s3_client = None

def get_s3_client():
    """Get or create S3 client"""
    global s3_client
    
    if s3_client is None and settings.AWS_ACCESS_KEY_ID:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    return s3_client


async def upload_recording(
    audio_data: bytes,
    call_sid: str,
    content_type: str = "audio/mpeg"
) -> Optional[str]:
    """
    Upload call recording to S3
    
    Args:
        audio_data: Audio file bytes
        call_sid: Twilio call SID
        content_type: MIME type
    
    Returns:
        S3 object key (path)
    """
    try:
        client = get_s3_client()
        
        if not client:
            logger.warning("S3 not configured, skipping upload")
            return None
        
        # Generate S3 key
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        s3_key = f"recordings/{timestamp}/{call_sid}.mp3"
        
        logger.info(f"Uploading recording to S3: {s3_key}")
        
        # Upload to S3
        client.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=s3_key,
            Body=audio_data,
            ContentType=content_type,
            Metadata={
                "call_sid": call_sid,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Recording uploaded successfully: {s3_key}")
        return s3_key
        
    except ClientError as e:
        logger.error(f"S3 upload failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Upload recording failed: {str(e)}")
        return None


async def get_recording_url(s3_key: str, expiration: int = 3600) -> Optional[str]:
    """
    Generate signed URL for recording playback
    
    Args:
        s3_key: S3 object key
        expiration: URL validity in seconds (default 1 hour)
    
    Returns:
        Signed URL for download/playback
    """
    try:
        client = get_s3_client()
        
        if not client:
            return None
        
        logger.info(f"Generating signed URL for: {s3_key}")
        
        url = client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        
        return url
        
    except ClientError as e:
        logger.error(f"Failed to generate signed URL: {str(e)}")
        return None


async def delete_recording(s3_key: str) -> bool:
    """
    Delete recording from S3
    
    Args:
        s3_key: S3 object key
    
    Returns:
        True if deleted successfully
    """
    try:
        client = get_s3_client()
        
        if not client:
            return False
        
        logger.info(f"Deleting recording: {s3_key}")
        
        client.delete_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=s3_key
        )
        
        logger.info(f"Recording deleted: {s3_key}")
        return True
        
    except ClientError as e:
        logger.error(f"Delete failed: {str(e)}")
        return False


async def list_recordings(prefix: str = "recordings/", max_keys: int = 100) -> list:
    """
    List recordings in S3
    
    Args:
        prefix: S3 key prefix
        max_keys: Maximum number of results
    
    Returns:
        List of recording keys
    """
    try:
        client = get_s3_client()
        
        if not client:
            return []
        
        response = client.list_objects_v2(
            Bucket=settings.AWS_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        recordings = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                recordings.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
        
        return recordings
        
    except ClientError as e:
        logger.error(f"List recordings failed: {str(e)}")
        return []


async def download_and_upload_recording(twilio_url: str, call_sid: str) -> Optional[str]:
    """
    Download recording from Twilio and upload to S3
    
    This is typically called from webhook after call ends
    
    Args:
        twilio_url: Twilio recording URL
        call_sid: Call SID
    
    Returns:
        S3 key if successful
    """
    try:
        logger.info(f"Downloading recording from Twilio for upload to S3...")
        
        # Download from Twilio
        audio_data = await download_recording(twilio_url)
        
        if not audio_data:
            logger.error("No audio data received from Twilio")
            return None
        
        # Upload to S3
        s3_key = await upload_recording(audio_data, call_sid)
        
        return s3_key
        
    except Exception as e:
        logger.error(f"Download and upload failed: {str(e)}")
        return None


def get_recording_metadata(s3_key: str) -> Optional[dict]:
    """
    Get recording metadata from S3
    
    Args:
        s3_key: S3 object key
    
    Returns:
        Metadata dictionary
    """
    try:
        client = get_s3_client()
        
        if not client:
            return None
        
        response = client.head_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=s3_key
        )
        
        return {
            "size": response['ContentLength'],
            "content_type": response['ContentType'],
            "last_modified": response['LastModified'].isoformat(),
            "metadata": response.get('Metadata', {})
        }
        
    except ClientError as e:
        logger.error(f"Get metadata failed: {str(e)}")
        return None