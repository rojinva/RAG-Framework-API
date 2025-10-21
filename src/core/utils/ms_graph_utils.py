from src.core.context.vars import user_email_var, access_token_var
import requests
import logging
from src.core.cache.decorators import cache_user

logger = logging.getLogger(__name__)

@cache_user("copilot_access")
def has_copilot_access() -> bool:
    """
    Check if a user has Microsoft 365 Copilot license assigned.
    Returns True if the user has Copilot access, False otherwise.
    """

    email_address = user_email_var.get("user_email")
    access_token = access_token_var.get("access_token")
    
    # If not in cache, make the API call
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = f"https://graph.microsoft.com/v1.0/users/{email_address}/licenseDetails"
    
    response = requests.get(url, headers=headers)
        
    if response.status_code != 200:
        return False
    
    license_data = response.json()
    
    # Check for Microsoft 365 Copilot license
    has_copilot = False
    if license_data and 'value' in license_data:
        for lic in license_data['value']:
            if lic.get('skuPartNumber', '').lower() == "microsoft_365_copilot":
                has_copilot = True
                break
    
    return has_copilot


def is_valid_graph_email_address(email: str) -> bool:
    """
    Check if an email address is valid within the Active Directory.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if the email address exists in AD, False otherwise
    """
    
    access_token = access_token_var.get("access_token")
    
    if not access_token:
        logger.warning("No access token available for Graph API call")
        return False
    
    if not email or not email.strip():
        logger.warning("Empty or invalid email address provided")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Use the Graph API to check if the user exists
    url = f"https://graph.microsoft.com/v1.0/users/{email.strip()}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # User exists in AD
            logger.debug(f"Email {email} found in Active Directory")
            return True
        elif response.status_code == 404:
            # User not found
            logger.debug(f"Email {email} not found in Active Directory")
            return False
        else:
            # Other error (403 Forbidden, 401 Unauthorized, etc.)
            logger.warning(f"Graph API call failed with status {response.status_code} for email {email}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception while validating email {email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while validating email {email}: {str(e)}")
        return False

@cache_user("user_graph_info", ttl=14400)  # Cache for 4 hours (14400 seconds)
def get_user_graph_info() -> dict:
    """
    Get comprehensive user information from Microsoft Graph API.
    
    Returns:
        dict: User information including basic info, organizational info, and contact details.
              Returns empty dict if user not found or on error.
    """
    
    logger.info("get_user_graph_info called")
    
    email_address = user_email_var.get("user_email")
    access_token = access_token_var.get("access_token")
    
    logger.info(f"Email address from context: {email_address}")
    logger.info(f"Access token available: {bool(access_token)}")
    
    if not access_token:
        logger.warning("No access token available for Graph API call")
        return {}
    
    if not email_address or not email_address.strip():
        logger.warning("No user email available from context")
        return {}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Select specific fields to retrieve from Graph API
    select_fields = [
        "id",
        "displayName", 
        "givenName",
        "surname",
        "userPrincipalName",
        "mail",
        "jobTitle",
        "department", 
        "companyName",
        "officeLocation",
        "city",
        "state",
        "country",
        "employeeId",
        "businessPhones",
        "mobilePhone",
        "manager"
    ]
    
    url = f"https://graph.microsoft.com/v1.0/users/{email_address.strip()}?$select={','.join(select_fields)}&$expand=manager($select=displayName,jobTitle,mail,officeLocation,city,state,country)"
    logger.info(f"Making Graph API request to: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Graph API response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"User data keys received: {list(user_data.keys())}")
            
            # Extract manager information from expanded data
            manager_info = None
            if user_data.get("manager"):
                manager_data = user_data["manager"]
                manager_info = {
                    "displayName": manager_data.get("displayName"),
                    "jobTitle": manager_data.get("jobTitle"),
                    "mail": manager_data.get("mail"),
                    "officeLocation": manager_data.get("officeLocation"),
                    "city": manager_data.get("city"),
                    "state": manager_data.get("state"),
                    "country": manager_data.get("country")
                }
                logger.info(f"Manager info from expanded data: {manager_info}")
            
            # Structure the response with the requested fields
            user_info = {
                # Basic info
                "id": user_data.get("id"),
                "displayName": user_data.get("displayName"),
                "givenName": user_data.get("givenName"),
                "surname": user_data.get("surname"),
                "userPrincipalName": user_data.get("userPrincipalName"),
                "mail": user_data.get("mail"),
                
                # Organizational info
                "jobTitle": user_data.get("jobTitle"),
                "department": user_data.get("department"),
                "companyName": user_data.get("companyName"),
                "officeLocation": user_data.get("officeLocation"),
                "city": user_data.get("city"),
                "state": user_data.get("state"),
                "country": user_data.get("country"),
                "employeeId": user_data.get("employeeId"),
                "businessPhones": user_data.get("businessPhones", []),
                "mobilePhone": user_data.get("mobilePhone"),
                
                # Manager info
                "manager": manager_info
            }
            
            logger.info(f"Successfully retrieved user info for {email_address}. User info: {user_info}")
            return user_info
            
        elif response.status_code == 404:
            logger.warning(f"User {email_address} not found in Active Directory")
            return {}
        else:
            logger.warning(f"Graph API call failed with status {response.status_code} for user {email_address}")
            return {}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception while getting user info for {email_address}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error while getting user info for {email_address}: {str(e)}")
        return {}
