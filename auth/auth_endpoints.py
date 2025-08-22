#!/usr/bin/env python3
"""
🔐 Authentication API Endpoints
FastAPI endpoints for user authentication and activity management
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import logging

try:
    from auth.auth_service import auth_service
except ImportError:
    auth_service = None

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# Request/Response models
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: str
    last_login: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    session_id: Optional[str] = None
    expires_at: Optional[str] = None

class ActivityResponse(BaseModel):
    activity_type: str
    activity_data: Optional[Dict[str, Any]] = None
    created_at: str
    ip_address: Optional[str] = None

class QueryResponse(BaseModel):
    query_id: int
    question: str
    agent_used: str
    response_preview: str
    edges_traversed: List[str]
    processing_time: Optional[float] = None
    created_at: str

# Router
router = APIRouter(prefix="/auth", tags=["authentication"])

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Dependency to get current authenticated user"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, req: Request):
    """Register a new user"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Get client IP
    ip_address = get_client_ip(req)
    
    # Register user
    result = auth_service.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        ip_address=ip_address
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return AuthResponse(
        success=True,
        message=f"User {request.username} registered successfully",
        user=UserResponse(
            user_id=result['user_id'],
            username=result['username'],
            email=result['email'],
            created_at=result['expires_at']  # Using expires_at as a timestamp
        ),
        token=result['token'],
        session_id=result['session_id'],
        expires_at=result['expires_at']
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, req: Request):
    """Login user"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Get client IP
    ip_address = get_client_ip(req)
    
    # Login user
    result = auth_service.login_user(
        username=request.username,
        password=request.password,
        ip_address=ip_address
    )
    
    if not result['success']:
        raise HTTPException(status_code=401, detail=result['error'])
    
    return AuthResponse(
        success=True,
        message=f"User {request.username} logged in successfully",
        user=UserResponse(
            user_id=result['user_id'],
            username=result['username'],
            email=result['email'],
            created_at=result['expires_at']  # Using expires_at as a timestamp
        ),
        token=result['token'],
        session_id=result['session_id'],
        expires_at=result['expires_at']
    )

@router.post("/logout")
async def logout(req: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Logout user"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Get session ID from token if available
    session_id = None
    if credentials:
        token_data = auth_service._verify_session_token(credentials.credentials)
        if token_data and hasattr(req, 'session'):
            session_id = getattr(req.session, 'session_id', None)
    
    # Get client IP
    ip_address = get_client_ip(req)
    
    # Note: In a real implementation, we'd need to track session_id in the token or request
    # For now, we'll just return success (the JWT token becomes invalid on client side)
    
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        user_id=current_user['id'],
        username=current_user['username'],
        email=current_user['email'],
        created_at=current_user['created_at'].isoformat() if current_user['created_at'] else None,
        last_login=current_user['last_login'].isoformat() if current_user['last_login'] else None
    )

@router.get("/activity", response_model=List[ActivityResponse])
async def get_activity(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user activity history"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    activities = auth_service.get_user_activity(current_user['id'], limit)
    
    return [
        ActivityResponse(
            activity_type=activity['activity_type'],
            activity_data=activity.get('activity_data', {}),
            created_at=activity['created_at'].isoformat() if activity['created_at'] else None,
            ip_address=activity.get('ip_address')
        )
        for activity in activities
    ]

@router.get("/queries", response_model=List[QueryResponse])
async def get_queries(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user query history"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    queries = auth_service.get_user_queries(current_user['id'], limit)
    
    return [
        QueryResponse(
            query_id=query['query_id'],
            question=query['question'],
            agent_used=query['agent_used'],
            response_preview=query.get('response_preview', query['response_text'][:200]),
            edges_traversed=query.get('edges_traversed', []),
            processing_time=float(query['processing_time']) if query['processing_time'] else None,
            created_at=query['created_at'].isoformat() if query['created_at'] else None
        )
        for query in queries
    ]

@router.get("/stats")
async def get_user_stats(current_user: Dict = Depends(get_current_user)):
    """Get user statistics"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Get recent activity and queries
    activities = auth_service.get_user_activity(current_user['id'], 1000)
    queries = auth_service.get_user_queries(current_user['id'], 1000)
    
    # Calculate statistics
    total_queries = len(queries)
    total_activities = len(activities)
    
    # Count queries by agent
    agent_usage = {}
    for query in queries:
        agent = query.get('agent_used', 'Unknown')
        agent_usage[agent] = agent_usage.get(agent, 0) + 1
    
    # Activity types
    activity_types = {}
    for activity in activities:
        activity_type = activity.get('activity_type', 'unknown')
        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
    
    return {
        "user_id": current_user['id'],
        "username": current_user['username'],
        "total_queries": total_queries,
        "total_activities": total_activities,
        "agent_usage": agent_usage,
        "activity_types": activity_types,
        "member_since": current_user['created_at'].isoformat() if current_user['created_at'] else None,
        "last_login": current_user['last_login'].isoformat() if current_user['last_login'] else None
    }

# Export router and dependency
__all__ = ['router', 'get_current_user']
