"""
Session Manager for Blaxel Sandboxes

This module provides session-based access to Blaxel sandboxes as an alternative
to preview URLs. Sessions provide authenticated, time-limited access to sandbox
APIs without relying on preview URL routing.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from dataclasses import dataclass

from blaxel.core import SandboxInstance


@dataclass
class SessionInfo:
    """Session information for a sandbox"""
    sandbox_name: str
    session_url: str
    session_token: str
    created_at: datetime
    expires_at: datetime
    workspace: str
    status: str = "active"
    deployment_id: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid"""
        return (
            self.status == "active" and 
            datetime.now(UTC) < self.expires_at
        )
    
    @property
    def needs_refresh(self) -> bool:
        """Check if session needs refresh (< 10 minutes remaining)"""
        time_remaining = self.expires_at - datetime.now(UTC)
        return time_remaining.total_seconds() < 600  # 10 minutes
    
    @property
    def time_remaining(self) -> str:
        """Human-readable time remaining"""
        delta = self.expires_at - datetime.now(UTC)
        if delta.total_seconds() < 0:
            return "expired"
        minutes = int(delta.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes} minutes"
        hours = minutes // 60
        return f"{hours} hours"


class SessionManager:
    """
    Manages Blaxel sandbox sessions.
    
    Provides methods to create, retrieve, validate, and refresh sessions
    for accessing deployed applications in Blaxel sandboxes.
    """
    
    def __init__(self, qdrant_client=None, log_manager=None):
        """
        Initialize SessionManager.
        
        Args:
            qdrant_client: Optional Qdrant client for session storage
            log_manager: Optional log manager for operation logging
        """
        self.qdrant = qdrant_client
        self.log_manager = log_manager
    
    async def create_session(
        self, 
        sandbox: SandboxInstance, 
        duration_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Create a new session for a sandbox using Blaxel's native session API.
        
        This replaces preview URL creation and provides direct authenticated
        access to the sandbox API.
        
        Args:
            sandbox: The sandbox instance to create a session for
            duration_hours: Session validity duration in hours (default: 1)
            
        Returns:
            Dictionary containing session information:
            - sandbox_name: Name of the sandbox
            - session_url: URL for accessing the sandbox via session
            - session_token: Authentication token for the session
            - expires_at: When the session expires
            - created_at: When the session was created
            
        Raises:
            Exception: If session creation fails
        """
        try:
            # Calculate expiration time
            expires_at = datetime.now(UTC) + timedelta(hours=duration_hours)
            
            # Use Blaxel's session API (from documentation)
            # This is the key difference from preview URLs - sessions provide
            # direct authenticated access without routing issues
            session = await sandbox.sessions.create({
                "expires_at": expires_at
            })
            
            # Return session information
            session_info = {
                "sandbox_name": sandbox.metadata.name,
                "session_url": session.url,  # This replaces preview URLs!
                "session_token": session.token,
                "expires_at": expires_at,
                "created_at": datetime.now(UTC),
                "workspace": sandbox.metadata.workspace
            }
            
            # Log session creation if log_manager is available
            if self.log_manager:
                try:
                    await self.log_manager.log_blaxel_operation(
                        operation="session_create",
                        sandbox_name=sandbox.metadata.name,
                        details=f"Created session, expires at {expires_at.isoformat()}",
                        status="success"
                    )
                except Exception as log_error:
                    # Don't fail session creation if logging fails
                    print(f"Warning: Failed to log session creation: {log_error}")
            
            return session_info
            
        except Exception as e:
            # Log error if log_manager is available
            if self.log_manager:
                try:
                    await self.log_manager.log_blaxel_operation(
                        operation="session_create",
                        sandbox_name=sandbox.metadata.name,
                        details=f"Failed to create session: {str(e)}",
                        status="error"
                    )
                except:
                    pass
            
            raise Exception(f"Failed to create session for {sandbox.metadata.name}: {str(e)}")
    
    def is_session_valid(self, session_info: Dict[str, Any]) -> bool:
        """
        Check if a session is still valid.
        
        Args:
            session_info: Session information dictionary
            
        Returns:
            True if session is valid, False otherwise
        """
        if not session_info:
            return False
        
        expires_at = session_info.get("expires_at")
        if not expires_at:
            return False
        
        # Handle both datetime objects and ISO strings
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        return datetime.now(UTC) < expires_at
    
    def needs_refresh(self, session_info: Dict[str, Any]) -> bool:
        """
        Check if a session needs refresh (< 10 minutes remaining).
        
        Args:
            session_info: Session information dictionary
            
        Returns:
            True if session needs refresh, False otherwise
        """
        if not self.is_session_valid(session_info):
            return False
        
        expires_at = session_info.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        time_remaining = expires_at - datetime.now(UTC)
        return time_remaining.total_seconds() < 600  # 10 minutes
