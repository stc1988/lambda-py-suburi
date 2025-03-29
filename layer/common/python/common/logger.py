from aws_lambda_powertools.logging import Logger

logger = Logger(utc=False)

def init_logger_from_api_event(headers: dict) -> None:
    transaction_id = headers.get("x-transaction-id")
    if transaction_id:
        logger.append_keys(transaction_id=transaction_id)