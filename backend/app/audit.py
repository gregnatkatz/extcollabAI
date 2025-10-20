"""
Audit logging middleware for ContosoHealth Research Platform.
Logs all API requests for compliance (7-year retention).
"""

from fastapi import Request
from datetime import datetime
from typing import Optional
import json
import uuid

class AuditLogger:
    """
    Audit logger for tracking all API requests.
    In production, this should write to Azure SQL Database and Azure Blob Storage.
    """
    
    def __init__(self):
        self.logs = []  # In-memory storage for development
    
    async def log_request(
        self,
        request: Request,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        activity_type: str = "APIRequest",
        resource_id: Optional[str] = None,
        activity_details: Optional[dict] = None,
        result: str = "Success"
    ):
        """
        Log an API request or activity.
        
        Args:
            request: FastAPI Request object
            user_id: Entra ID user object ID
            user_email: User email address
            activity_type: Type of activity (APIRequest, DatasetAccessed, ExportRequested, etc.)
            resource_id: ID of resource being accessed
            activity_details: Additional details as JSON
            result: Result of the activity (Success, Failed, Denied)
        """
        log_entry = {
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "user_email": user_email,
            "activity_type": activity_type,
            "method": request.method,
            "path": request.url.path,
            "resource_id": resource_id,
            "activity_details": json.dumps(activity_details) if activity_details else None,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logs.append(log_entry)
        
        
        
        return log_entry
    
    def get_logs(
        self,
        user_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ):
        """
        Retrieve audit logs with filters.
        In production, this should query Azure SQL Database.
        """
        filtered_logs = self.logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
        
        if activity_type:
            filtered_logs = [log for log in filtered_logs if log["activity_type"] == activity_type]
        
        if start_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
        
        return filtered_logs[:limit]

audit_logger = AuditLogger()

async def audit_middleware(request: Request, call_next):
    """
    Middleware to automatically log all API requests.
    Add this to FastAPI app: app.middleware("http")(audit_middleware)
    """
    user_id = None
    user_email = None
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from app.auth import verify_token
            token = auth_header.replace("Bearer ", "")
            payload = verify_token(token)
            user_id = payload.get("oid")
            user_email = payload.get("preferred_username")
        except:
            pass  # Continue without user info if token is invalid
    
    try:
        response = await call_next(request)
        
        await audit_logger.log_request(
            request=request,
            user_id=user_id,
            user_email=user_email,
            activity_type="APIRequest",
            result="Success" if response.status_code < 400 else "Failed"
        )
        
        return response
    
    except Exception as e:
        await audit_logger.log_request(
            request=request,
            user_id=user_id,
            user_email=user_email,
            activity_type="APIRequest",
            result="Error",
            activity_details={"error": str(e)}
        )
        raise

def log_activity(activity_type: str, resource_id: Optional[str] = None, details: Optional[dict] = None):
    """
    Decorator to log specific activities.
    Usage:
        @log_activity("DatasetAccessed", resource_id="ds-001")
        async def get_dataset(dataset_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            request = kwargs.get("request")
            user = kwargs.get("user")
            
            if request and user:
                await audit_logger.log_request(
                    request=request,
                    user_id=user.user_id,
                    user_email=user.email,
                    activity_type=activity_type,
                    resource_id=resource_id or kwargs.get("dataset_id") or kwargs.get("project_id"),
                    activity_details=details,
                    result="Success"
                )
            
            return result
        
        return wrapper
    return decorator
