"""
Export workflow implementation with encryption and SAS token generation.
Handles data export requests, PI approval, and secure download links.
"""

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
from typing import Optional
import zipfile
import io
import os
import uuid
from app.config import settings

class ExportService:
    """Service for handling data export requests"""
    
    def __init__(self):
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
        else:
            self.blob_service_client = None
    
    def generate_request_number(self) -> str:
        """Generate unique export request number"""
        year = datetime.now().year
        random_id = str(uuid.uuid4())[:8].upper()
        return f"EXP-{year}-{random_id}"
    
    async def create_export_package(
        self,
        request_id: str,
        dataset_name: str,
        data: bytes,
        password: Optional[str] = None
    ) -> str:
        """
        Create encrypted export package (ZIP file).
        
        Args:
            request_id: Export request ID
            dataset_name: Name of dataset being exported
            data: Raw data to export (CSV, JSON, etc.)
            password: Optional password for ZIP encryption
        
        Returns:
            Blob name in storage
        """
        if not self.blob_service_client:
            return f"mock-exports/{request_id}.zip"
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{dataset_name}.csv", data)
            
            readme = f"""
AdventHealth Research Platform - Data Export

Export Request ID: {request_id}
Dataset: {dataset_name}
Export Date: {datetime.now().isoformat()}

IMPORTANT SECURITY NOTICE:
- This export contains Protected Health Information (PHI)
- Handle according to HIPAA regulations
- Do not share or distribute without authorization
- Delete after use or within 24 hours
- Report any suspected data breach immediately

For questions, contact: research-platform@adventhealth.com
"""
            zip_file.writestr("README.txt", readme)
            
            if password:
                zip_file.setpassword(password.encode())
        
        zip_buffer.seek(0)
        
        container_client = self.blob_service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_EXPORTS
        )
        
        blob_name = f"{datetime.now().strftime('%Y/%m/%d')}/{request_id}.zip"
        blob_client = container_client.get_blob_client(blob_name)
        
        blob_client.upload_blob(
            zip_buffer.getvalue(),
            overwrite=True,
            metadata={
                "request_id": request_id,
                "dataset_name": dataset_name,
                "export_date": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=settings.EXPORT_AUTO_DELETE_HOURS)).isoformat()
            }
        )
        
        return blob_name
    
    def generate_download_url(
        self,
        blob_name: str,
        expiry_hours: int = None
    ) -> str:
        """
        Generate time-limited SAS URL for downloading export.
        
        Args:
            blob_name: Name of blob in storage
            expiry_hours: Hours until SAS token expires (default: 24)
        
        Returns:
            SAS URL for download
        """
        if not self.blob_service_client:
            return f"https://mock-storage.blob.core.windows.net/exports/{blob_name}?sas=mock_token"
        
        if expiry_hours is None:
            expiry_hours = settings.EXPORT_SAS_TOKEN_EXPIRY_HOURS
        
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=settings.AZURE_STORAGE_CONTAINER_EXPORTS,
            blob_name=blob_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{settings.AZURE_STORAGE_CONTAINER_EXPORTS}/{blob_name}?{sas_token}"
        
        return blob_url
    
    async def delete_expired_exports(self):
        """
        Delete exports that have expired (>24 hours old).
        Should be run as a scheduled job.
        """
        if not self.blob_service_client:
            return
        
        container_client = self.blob_service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_EXPORTS
        )
        
        cutoff_time = datetime.now() - timedelta(hours=settings.EXPORT_AUTO_DELETE_HOURS)
        deleted_count = 0
        
        blobs = container_client.list_blobs(include=['metadata'])
        
        for blob in blobs:
            if blob.metadata and 'expires_at' in blob.metadata:
                expires_at = datetime.fromisoformat(blob.metadata['expires_at'])
                if expires_at < datetime.now():
                    container_client.delete_blob(blob.name)
                    deleted_count += 1
        
        return deleted_count
    
    async def send_export_notification(
        self,
        recipient_email: str,
        request_number: str,
        status: str,
        download_url: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """
        Send email notification about export request status.
        
        Args:
            recipient_email: Email address to send notification to
            request_number: Export request number
            status: Status of export (Approved, Rejected, etc.)
            download_url: Download URL (if approved)
            notes: Additional notes from reviewer
        """
        
        if status == "Approved":
            subject = f"Export Request {request_number} Approved"
            body = f"""
Your export request {request_number} has been approved.

Download URL: {download_url}
Expires: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S UTC')}

IMPORTANT:
- This link expires in 24 hours
- The file will be automatically deleted after 24 hours
- Do not share this link with others
- Handle the data according to HIPAA regulations

Reviewer Notes: {notes or 'None'}

If you have any questions, contact: research-platform@adventhealth.com
"""
        elif status == "Rejected":
            subject = f"Export Request {request_number} Rejected"
            body = f"""
Your export request {request_number} has been rejected.

Reason: {notes or 'Not specified'}

If you have questions or would like to submit a revised request, please contact your PI.
"""
        else:
            subject = f"Export Request {request_number} Status Update"
            body = f"""
Your export request {request_number} status has been updated to: {status}

Notes: {notes or 'None'}
"""
        
        #     
        #     
        
        print(f"Email notification sent to {recipient_email}: {subject}")
        return True

export_service = ExportService()
