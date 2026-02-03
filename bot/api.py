import os
import httpx
from typing import Any


DEFAULT_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


class APIError(Exception):
    def __init__(self, status_code: int, detail: str | None = None):
        self.status_code = status_code
        self.detail = detail or ""
        super().__init__(f"{status_code}: {self.detail}")


async def get_credential(
    credential_id: int,
    *,
    base_url: str = DEFAULT_BASE_URL,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    own_client = client is None
    if client is None:
        client = httpx.AsyncClient()
    try:
        r = await client.get(f"{base_url}/credentials/{credential_id}")
        if r.status_code == 404:
            raise APIError(404, r.json().get("detail"))
        r.raise_for_status()
        return r.json()
    finally:
        if own_client:
            await client.aclose()


async def create_valentine(
    text: str,
    track_link: str,
    recipient_id: int,
    sender: str | None = None,
    *,
    base_url: str = DEFAULT_BASE_URL,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    own_client = client is None
    if client is None:
        client = httpx.AsyncClient()
    try:
        body = {
            "text": text,
            "track_link": track_link,
            "recipient_id": recipient_id,
            "sender": sender,
        }
        r = await client.post(f"{base_url}/valentines", json=body)
        if r.status_code == 404:
            raise APIError(404, r.json().get("detail"))
        r.raise_for_status()
        return r.json()
    finally:
        if own_client:
            await client.aclose()


async def get_valentine(
    valentine_id: int,
    *,
    base_url: str = DEFAULT_BASE_URL,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    own_client = client is None
    if client is None:
        client = httpx.AsyncClient()
    try:
        r = await client.get(f"{base_url}/valentines/{valentine_id}")
        if r.status_code == 404:
            raise APIError(404, r.json().get("detail"))
        r.raise_for_status()
        return r.json()
    finally:
        if own_client:
            await client.aclose()


async def list_valentines_by_recipient(
    recipient_id: int,
    *,
    base_url: str = DEFAULT_BASE_URL,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    own_client = client is None
    if client is None:
        client = httpx.AsyncClient()
    try:
        r = await client.get(f"{base_url}/valentines/recipient/{recipient_id}")
        r.raise_for_status()
        return r.json()
    finally:
        if own_client:
            await client.aclose()
