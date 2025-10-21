import logging
from typing import Optional, Dict, Any

from src.core.utils.ms_graph_utils import get_user_graph_info

logger = logging.getLogger(__name__)


def enhance_system_message_with_user_context(system_message: Optional[str], user_info: Optional[Dict[str, Any]] = None) -> str:
    """
    Enhance system message with user context information.
    
    Args:
        system_message: The original system message to enhance
        user_info: User information dictionary (as returned by get_user_graph_info)
        
    Returns:
        str: System message with appended user context
    """
    
    if not system_message:
        return ""
    
        
    if not user_info:
        return system_message
    
    # Build user context section
    user_context_lines = ["User Context:"]
    
    # Add user information in a clean format
    if user_info.get("displayName"):
        user_context_lines.append(f"Name: {user_info['displayName']}")
    
    if user_info.get("jobTitle"):
        user_context_lines.append(f"Role: {user_info['jobTitle']}")
    
    if user_info.get("department"):
        user_context_lines.append(f"Department: {user_info['department']}")
    
    if user_info.get("companyName"):
        user_context_lines.append(f"Company: {user_info['companyName']}")
    
    if user_info.get("officeLocation"):
        user_context_lines.append(f"Office Location: {user_info['officeLocation']}")
    
    if user_info.get("city") or user_info.get("state") or user_info.get("country"):
        location_parts = []
        if user_info.get("city"):
            location_parts.append(user_info["city"])
        if user_info.get("state"):
            location_parts.append(user_info["state"])
        if user_info.get("country"):
            location_parts.append(user_info["country"])
        if location_parts:
            user_context_lines.append(f"Location: {', '.join(location_parts)}")
    
    if user_info.get("mail"):
        user_context_lines.append(f"Email: {user_info['mail']}")
    
    # Add manager information if available
    if user_info.get("manager") and user_info["manager"]:
        manager = user_info["manager"]
        manager_parts = []
        if manager.get("displayName"):
            manager_parts.append(manager["displayName"])
        if manager.get("jobTitle"):
            manager_parts.append(f"({manager['jobTitle']})")
        if manager.get("officeLocation"):
            manager_parts.append(f"[{manager['officeLocation']}]")
        
        # Add manager location if available
        if manager.get("city") or manager.get("state") or manager.get("country"):
            location_parts = []
            if manager.get("city"):
                location_parts.append(manager["city"])
            if manager.get("state"):
                location_parts.append(manager["state"])
            if manager.get("country"):
                location_parts.append(manager["country"])
            if location_parts:
                manager_parts.append(f"({', '.join(location_parts)})")
        
        if manager.get("mail"):
            manager_parts.append(f"<{manager['mail']}>")
        
        if manager_parts:
            user_context_lines.append(f"Manager: {' '.join(manager_parts)}")
    
    # Only add user context if we have meaningful information
    if len(user_context_lines) > 1:  # More than just "User Context:"
        user_context = "\n".join(user_context_lines)
        enhanced_message = f"{system_message}\n\n{user_context}"
        return enhanced_message
    
    return system_message