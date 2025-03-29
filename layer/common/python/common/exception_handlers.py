from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.logging.logger import Logger
from pydantic import ValidationError
from common.logger import logger


def register_exception_handlers(app):
    @app.exception_handler(ValidationError)
    def handle_validation_error(ex: ValidationError):
        logger.warning("Validation failed", extra={"errors": ex.errors()})
        return Response(
            status_code=400,
            content_type="application/json",
            body={
                "message": "Bad Request",
                "errors": ex.errors()
            }
        )

    @app.exception_handler(Exception)
    def handle_general_exception(ex: Exception):
        logger.exception("Unexpected error occurred")
        return Response(
            status_code=500,
            content_type="application/json",
            body={
                "message": "Internal Server Error",
                "error": str(ex)
            }
        )