import os
import warnings
from dotenv import load_dotenv

load_dotenv(override=True)

from src.core.utils.auth_helpers import get_entra_id_security_groups


def get_accessible_account_names(access_token: str) -> list:
    """Returns a list of account names that the user has access to based on their security group memberships.

    Args:
        access_token (str): The access token of the user.

    Returns:
        List[str]: A list of account names that the user has access to.
    """

    account_name_security_group_id_mapping = {
        "A": os.getenv("ETCH_ACCOUNT_A_SECURITY_GROUP_ID", None),
        "B": os.getenv("ETCH_ACCOUNT_B_SECURITY_GROUP_ID", None),
        "C": os.getenv("ETCH_ACCOUNT_C_SECURITY_GROUP_ID", None),
        "D": os.getenv("ETCH_ACCOUNT_D_SECURITY_GROUP_ID", None),
        "E": os.getenv("ETCH_ACCOUNT_E_SECURITY_GROUP_ID", None),
        "F": os.getenv("ETCH_ACCOUNT_F_SECURITY_GROUP_ID", None),
        "G": os.getenv("ETCH_ACCOUNT_G_SECURITY_GROUP_ID", None),
    }

    user_security_groups = get_entra_id_security_groups(access_token)
    accessible_account_names = []

    for account, security_group_id in account_name_security_group_id_mapping.items():
        if security_group_id in user_security_groups:
            accessible_account_names.append(account)

    if not accessible_account_names:
        warnings.warn(
            "No accessible accounts found for the user based on their security group memberships."
        )

    return accessible_account_names
