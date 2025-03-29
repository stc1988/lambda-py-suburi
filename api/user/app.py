from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from pydantic import BaseModel, Field, ValidationError, constr, conint
from typing import Optional

app = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger(utc=False)
metrics = Metrics(namespace="Powertools")


# ✅ Pydanticモデルでバリデーション定義
class UserRequest(BaseModel):
    name: constr(min_length=1, max_length=10)
    age: conint(strict=True)  # 厳密に数値
    birthday: Optional[constr(min_length=8, max_length=8)] = None


@app.post("/user/<userid>")
@tracer.capture_method
def post_user(userid: str):
    body = app.current_event.json_body
    transaction_id = app.current_event.headers.get("x-transaction-id")
    logger.append_keys(transaction_id=transaction_id)

    try:
        # ✅ バリデーション実行
        user_request = UserRequest(**body)
    except ValidationError as e:
        logger.warning("Validation failed", extra={"errors": e.errors()})
        return {
            "statusCode": 400,
            "body": {
                "message": "Bad Request",
                "errors": e.errors()
            }
        }

    logger.info("POST /usre/<userid> called", extra={
        "userid": userid,
        "request_body": body
    })

    metrics.add_metric(name="UserPostInvocations", unit=MetricUnit.Count, value=1)

    return {
        "message": f"User ID received: {userid}",
        "validated_data": user_request.dict()
    }


# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)