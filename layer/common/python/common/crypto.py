import boto3
import base64
import os
from common.tracer import tracer

kms = boto3.client('kms')

KMS_KEY_ID = os.environ.get("KMS_KEY_ID")

@tracer.capture_method
def encrypt_text(plaintext: str) -> str:
    response = kms.encrypt(
        KeyId=KMS_KEY_ID,
        Plaintext=plaintext.encode("utf-8")
    )
    ciphertext_blob = response['CiphertextBlob']
    return base64.b64encode(ciphertext_blob).decode("utf-8")

@tracer.capture_method
def decrypt_text(ciphertext_b64: str) -> str:
    ciphertext_blob = base64.b64decode(ciphertext_b64.encode("utf-8"))
    response = kms.decrypt(
        CiphertextBlob=ciphertext_blob
    )
    return response['Plaintext'].decode("utf-8")