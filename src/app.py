from fastapi import FastAPI
from src.core.middleware.request_context import RequestSpanMiddleware
from starlette.middleware import Middleware
from src.routes.chat_completion import chat_router
from src.routes.db_routes import db_router
from contextlib import asynccontextmanager
from src.clients import LifespanClients
from src.routes.chat_completion_external import chat_router_external
from src.routes.db_routes_external import db_router_external

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Get the lifespan services.
    
    Yields:
        LifespanServices: An instance of LifespanServices.
    """
    # Start the services when the app is starting up.

    # Instantiate LifespanServices.
    lifespan_clients = LifespanClients.get_instance()
    yield 

    # Gracefully shutdown the services when the app is shutting down.
    await lifespan_clients.shutdown()


__app_name__ = "LamBots REST API"
__version__ = "0.1.0"

middleware = [
    Middleware(RequestSpanMiddleware)
]

app = FastAPI(title="LamBots API", middleware=middleware, lifespan=lifespan)

@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"app": __app_name__, "version": __version__}


# create a healthcheck endpoint that doesn't require authentication
@app.get("/health", dependencies=[])
async def healthcheck():
    """
    Healthcheck endpoint.
    """
    return {"status": "ok"}

app.include_router(chat_router)
app.include_router(db_router)
app.include_router(chat_router_external)
app.include_router(db_router_external)

__all__ = ["app"]
