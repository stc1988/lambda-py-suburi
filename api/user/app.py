from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from pydantic import BaseModel, Field, ValidationError, constr, conint
from typing import Optional
from common.logger import logger

app = APIGatewayRestResolver()
tracer = Tracer()
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

    # ✅ 例外は共通ハンドラーで処理される
    user_request = UserRequest(**body)

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