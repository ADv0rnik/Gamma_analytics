import uvicorn
import logging.config
from fastapi import FastAPI

from src.config import ApiSettings
from src.config import LOGGING_CONFIG
from src.api.api import analytics_router


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("gamma")


def start_application(config: ApiSettings):
    application = FastAPI(
        debug=True,
        title=config.PROJECT_NAME,
        version=config.PROJECT_VERSION,
        description="Bayesian simulator for gamma-radiation measurements",
        docs_url=f"{config.API_V1_STR}/docs",
        redoc_url=f"{config.API_V1_STR}/redoc",
    )
    return application


settings = ApiSettings()
app = start_application(settings)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host=settings.PROJECT_HOST,
        port=int(settings.PROJECT_PORT),
        reload=True
    )
