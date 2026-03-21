import time
from abc import ABC, abstractmethod

import httpx

import re

from app.config import HTTP_TIMEOUT, HTTP_USER_AGENT
from app.models import SourceResult


class BaseAdapter(ABC):
    name: str
    timeout: float = HTTP_TIMEOUT

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.timeout,
            headers={'User-Agent': HTTP_USER_AGENT},
        )

    async def search(self, query: str, **kwargs) -> SourceResult:
        start = time.monotonic()
        try:
            result = await self._search(query, **kwargs)
            result.duration_ms = int((time.monotonic() - start) * 1000)
            return result
        except Exception as e:
            return SourceResult(
                source=self.name,
                query=query,
                duration_ms=int((time.monotonic() - start) * 1000),
                error=re.sub(r'api_token=[^&\s]+', 'api_token=***', str(e)),
            )

    @abstractmethod
    async def _search(self, query: str, **kwargs) -> SourceResult:
        pass

    async def enrich(self, matches: list) -> list:
        return matches
