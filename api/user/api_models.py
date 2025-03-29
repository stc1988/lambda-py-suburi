from pydantic import BaseModel, Field, constr, conint
from typing import Optional

class RequestPathParams(BaseModel):
   userid: constr(min_length=1, max_length=10, pattern="^[a-zA-Z0-9]+$")

class RequestHeader(BaseModel):
   x_transaction_id: constr(min_length=10) = Field(..., alias="x-transaction-id")

class RequestBody(BaseModel):
    name: constr(min_length=1, max_length=10)
    age: conint(strict=True)
    birthday: Optional[constr(min_length=8, max_length=8)] = None
