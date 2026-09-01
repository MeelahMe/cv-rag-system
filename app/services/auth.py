import os
from typing import Optional

from fastapi import Header, HTTPException, status


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    expected_api_key = os.getenv("API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API_KEY not set",
        )

    if x_api_key is None or x_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key.",
        )
