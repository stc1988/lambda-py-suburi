from api_models import RequestPathParams, RequestHeader, RequestBody
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.metrics import Metrics, MetricUnit

logger = Logger()
metrics = Metrics(namespace="Powertools")

def do_process(userid: str, headers: dict, body: dict) -> dict:
    # Validate path parameter
    path_params = RequestPathParams(userid=userid)

    # Validate headers
    request_headers = RequestHeader(**headers)

    # Validate body
    request_body = RequestBody(**body)

    logger.info("POST /user/<userid> called", extra={
        "userid": path_params.userid,
        "request_body": request_body
    })

    metrics.add_metric(name="UserPostInvocations", unit=MetricUnit.Count, value=1)

    return {
        "message": f"User ID received: {path_params.userid}",
        "validated_data": request_body.dict()
    }
