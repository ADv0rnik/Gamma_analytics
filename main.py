import uvicorn
import logging.config
from fastapi import FastAPI

from src.settings.config import ApiSettings
from src.settings.config import LOGGING_CONFIG
from src.api.api import analytics_router
from src.exceptions.error_handlers import (
    WrongFileFormatException,
    wrong_file_format_exception_handler,
    generic_exception_handler
)


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

app.add_exception_handler(WrongFileFormatException, wrong_file_format_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


if __name__ == "__main__":
    logger.info(f"Starting uvicorn server on {settings.PROJECT_HOST}:{settings.PROJECT_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.PROJECT_HOST,
        port=int(settings.PROJECT_PORT),
        reload=True
    )
