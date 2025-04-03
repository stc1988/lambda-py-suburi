from typing import Optional
from pydantic import BaseModel, Field, constr, conint
from common.logger import logger
from common.crypto import encrypt_text, decrypt_text
from common.tracer import tracer

class RequestPathParams(BaseModel):
   userid: constr(min_length=1, max_length=10, pattern="^[a-zA-Z0-9]+$")

class RequestHeaders(BaseModel):
   x_transaction_id: constr(min_length=10) = Field(..., alias="x-transaction-id")

class RequestBody(BaseModel):
    name: constr(min_length=1, max_length=10)
    age: conint(strict=True)
    birthday: Optional[constr(min_length=8, max_length=8)] = None

def validate_request(userid: str, request_headers: dict, request_body: dict):
    path_params = RequestPathParams(userid=userid)
    headers = RequestHeaders(**request_headers)
    body = RequestBody(**request_body)

    return path_params, headers, body

@tracer.capture_method
def do_process(userid: str, request_headers: dict, request_body: dict) -> dict:
    
    path_params, headers, body = validate_request(userid, request_headers, request_body)
 
    logger.info("POST /user/<userid> called", extra={
        "userid": path_params.userid,
        "request_body": body
    })
    
    secret = "my-secret-password"
    
    encrypted = encrypt_text(secret)
    logger.info(encrypted)
    decrypted = decrypt_text(encrypted)
    logger.info(decrypted)
    
    return {
        "message": f"User ID received: {path_params.userid}",
        "validated_data": body.model_dump()
    }
