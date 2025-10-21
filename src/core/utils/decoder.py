import base64
import json


def decode_jwt(jwt_token):
    """
    Decodes a JSON Web Token (JWT) and returns the payload as a dictionary.

    Args:
        jwt_token (str): The JWT token to decode.

    Returns:
        dict: The decoded payload of the JWT token.

    Raises:
        ValueError: If the JWT token is not properly formatted or the payload cannot be decoded.
    """
    parts = jwt_token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")
    
    payload_encoded = parts[1]
    padding = "=" * (4 - (len(payload_encoded) % 4))
    payload_encoded += padding
    payload = base64.urlsafe_b64decode(payload_encoded)
    return json.loads(payload)
