import warnings

from src.core.utils.auth_helpers import get_entra_id_security_groups
from src.core.tools.community.etch_sharepoint_sg_retriever.constants import (
    ETCH_SHAREPOINT_SITE_NAME_SG_ID_MAPPING,
)


def get_accessible_sharepoint_site_names(access_token: str) -> list:
    """Returns a list of sharepoint site names that the user has access to based on their security group memberships.

    Args:
        access_token (str): The access token of the user.

    Returns:
        List[str]: A list of sharepoint site names that the user has access to.
    """

    user_security_groups = get_entra_id_security_groups(access_token)
    accessible_site_names = []

    # Find accessible sites based on user's security group memberships
    for site_name, required_sg_id in ETCH_SHAREPOINT_SITE_NAME_SG_ID_MAPPING.items():
        if required_sg_id in user_security_groups:
            accessible_site_names.append(site_name)

    if not accessible_site_names:
        warnings.warn(
            "No accessible sharepoint site names found for the user based on their security group memberships."
        )

    return accessible_site_names