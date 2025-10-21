from typing import Optional

from fastapi import Header, Request


async def get_client_header(request: Request, client: Optional[str] = Header(None)):
    if not client:
        client = request.path_params.get("agency")
    return client
