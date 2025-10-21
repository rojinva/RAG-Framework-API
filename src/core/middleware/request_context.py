from src.core.context.vars import user_email_var, access_token_var, ms_user_object_id_var
from src.core.utils.decoder import decode_jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os
from dotenv import load_dotenv

load_dotenv()


class RequestSpanMiddleware(BaseHTTPMiddleware):
    """Middleware to manage the request-specific span of data such as access token and user email.

    Args:
        BaseHTTPMiddleware: Base class for creating middleware.
    """

    async def dispatch(self, request: Request, call_next):
        """Method to dispatch the request to the next middleware or the endpoint.

        Args:
            request (Request): FastAPI request object.
            call_next: Next middleware or endpoint.

        Returns:
            Response: Response object.
        """

        # List of whitelisted routes
        HEALTH_CHECK_ROUTE = "/health"
        WHITELISTED_ROUTES = ["/openapi.json", "/docs"]

        if request.url.path == HEALTH_CHECK_ROUTE:
            # If the request is for the healthcheck route, skip authentication
            return await call_next(request)

        def is_dev_environment() -> bool:
            """Check if the current environment is a development environment.

            Returns:
                bool: True if the environment is development, False otherwise.
            """
            azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_USE", "")
            return "dev" in azure_openai_endpoint

        # Check if the request path is in the whitelist and if it's a dev environment
        if is_dev_environment() and request.url.path in WHITELISTED_ROUTES:
            return await call_next(request)

        try:
            # Check for a graph-token header first
            graph_token = request.headers.get("graph-token")
            if graph_token:
                # Use graph-token directly
                access_token = graph_token
            else:
                # Fall back to Authorization: Bearer <token>
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    raise HTTPException(
                        status_code=401, detail="Authorization header missing"
                    )
                access_token = auth_header.split(" ")[1]

            access_token_var.set(access_token)

            decoded_token = decode_jwt(access_token)
            user_email = decoded_token.get("unique_name")
            user_id = decoded_token.get("oid")  # Microsoft Object ID
            user_email_var.set(user_email)
            ms_user_object_id_var.set(user_id)

            response = await call_next(request)
            return response       

        except Exception as e:
            print(f"Exception occurred: {e}")
            raise e
        finally:
            # Clear context variables after the request is processed
            user_email_var.set(None)
            access_token_var.set(None)
            ms_user_object_id_var.set(None)
