from __future__ import annotations

from fastapi import Query


class PageParams:
    """Shared pagination query params: page (1-indexed) / page_size.

    Each router defines its own typed `XxxListResponse` (items/total/
    page/page_size) rather than a shared generic response model, since
    FastAPI/Pydantic response_model resolution works best with concrete
    types -- this class only factors out the query-parameter parsing.
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=200),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
