"""
Authentication and authorization middleware for ContosoHealth Research Platform.
Implements Entra ID token validation and RBAC.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, List
from datetime import datetime
import os

security = HTTPBearer()

ENTRA_TENANT_ID = os.getenv("ENTRA_TENANT_ID", "mock-tenant-id")
ENTRA_CLIENT_ID = os.getenv("ENTRA_CLIENT_ID", "mock-client-id")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mock-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

MOCK_AUTH_MODE = os.getenv("MOCK_AUTH_MODE", "true").lower() == "true"

class User:
    """User model from Entra ID token"""
    def __init__(self, user_id: str, email: str, name: str, roles: List[str], institution: str = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.roles = roles
        self.institution = institution
        self.is_pi = "PI" in roles
        self.is_admin = "Admin" in roles
        self.can_export = "PI" in roles or "Admin" in roles

def verify_token(token: str) -> dict:
    """
    Verify Entra ID JWT token.
    In production, this should validate against Entra ID public keys.
    """
    if MOCK_AUTH_MODE:
        return {
            "oid": "user-001",
            "preferred_username": "dr.smith@contosohealth.com",
            "name": "Dr. Sarah Smith",
            "roles": ["PI", "Researcher"],
            "institution": "ContosoHealth Orlando"
        }
    
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            audience=ENTRA_CLIENT_ID
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    Use this on protected endpoints: @app.get("/endpoint", dependencies=[Depends(get_current_user)])
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    user = User(
        user_id=payload.get("oid"),
        email=payload.get("preferred_username"),
        name=payload.get("name"),
        roles=payload.get("roles", []),
        institution=payload.get("institution")
    )
    
    return user

async def get_current_user_optional(
    request: Request
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided.
    Use for endpoints that work with or without authentication.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    try:
        payload = verify_token(token)
        return User(
            user_id=payload.get("oid"),
            email=payload.get("preferred_username"),
            name=payload.get("name"),
            roles=payload.get("roles", []),
            institution=payload.get("institution")
        )
    except HTTPException:
        return None

def require_role(required_roles: List[str]):
    """
    Dependency to require specific roles.
    Usage: @app.get("/admin", dependencies=[Depends(require_role(["Admin"]))])
    """
    async def role_checker(user: User = Depends(get_current_user)):
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return user
    return role_checker

def require_pi():
    """
    Dependency to require PI role.
    Usage: @app.post("/approve", dependencies=[Depends(require_pi())])
    """
    return require_role(["PI", "Admin"])

def require_export_permission():
    """
    Dependency to check if user can request exports.
    """
    async def export_checker(user: User = Depends(get_current_user)):
        if not user.can_export:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to request data exports"
            )
        return user
    return export_checker

def check_project_access(project_id: str):
    """
    Dependency to check if user has access to specific project.
    In production, this should query the database.
    """
    async def project_access_checker(user: User = Depends(get_current_user)):
        if MOCK_AUTH_MODE:
            return user
        
        
        
        return user
    return project_access_checker
