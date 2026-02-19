from pywebpush import webpush, WebPushException
import base64
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_vapid_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    return {
        "private_key": base64.urlsafe_b64encode(private_bytes).decode('utf-8').strip("="),
        "public_key": base64.urlsafe_b64encode(public_bytes).decode('utf-8').strip("=")
    }

if __name__ == "__main__":
    keys = generate_vapid_keys()
    print(f"VAPID_PUBLIC_KEY={keys['public_key']}")
    print(f"VAPID_PRIVATE_KEY={keys['private_key']}")
