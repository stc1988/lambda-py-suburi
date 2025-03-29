from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from pydantic import BaseModel, Field, ValidationError, constr, conint
from typing import Optional
from common.logger import logger, init_logger_from_api_event
from common.exception_handlers import register_exception_handlers

app = APIGatewayRestResolver()
register_exception_handlers(app)
tracer = Tracer()
metrics = Metrics(namespace="Powertools")

class RequestPathParams(BaseModel):
   userid: constr(min_length=1, max_length=10, pattern="^[a-zA-Z0-9]+$")


class RequestHeader(BaseModel):
   x_transaction_id: constr(min_length=10) = Field(..., alias="x-transaction-id")

class RequestBody(BaseModel):
    name: constr(min_length=1, max_length=10)
    age: conint(strict=True)
    birthday: Optional[constr(min_length=8, max_length=8)] = None

@app.post("/user/<userid>")
@tracer.capture_method
def post_user(userid: str):
    init_logger_from_api_event(app.current_event.headers)
    
    # validate path paramter
    validated_path = RequestPathParams(userid=userid)
    
    # validate header
    headers = app.current_event.headers
    user_headers = RequestHeader(**headers)

    # validate body
    body = app.current_event.json_body
    user_request = RequestBody(**body)

    logger.info("POST /user/<userid> called", extra={
        "userid": userid,
        "request_body": body
    })

    metrics.add_metric(name="UserPostInvocations", unit=MetricUnit.Count, value=1)

    return {
        "message": f"User ID received: {userid}",
        "validated_data": user_request.dict()
    }


@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)