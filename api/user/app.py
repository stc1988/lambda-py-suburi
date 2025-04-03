from aws_lambda_powertools import Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse
from common.logger import init_logger_from_api_event
from common.exception_handlers import register_exception_handlers
from common.tracer import tracer
from service import do_process

app = APIGatewayRestResolver()
register_exception_handlers(app)
metrics = Metrics(namespace="Powertools")

@app.post("/user/<userid>")
@tracer.capture_method
def handle_request(userid: str):
    init_logger_from_api_event(app.current_event.headers)
    
    response = do_process(
        userid=userid,
        request_headers=app.current_event.headers,
        request_body=app.current_event.json_body
    )
    return response

@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)