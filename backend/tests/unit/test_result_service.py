import uuid

import pytest

from app.application.results.use_cases import ResultService
from app.domain.shared.exceptions import NotFoundError


class _FakeResults:
    def __init__(self, items=None) -> None:
        self.items = items or []

    def list_by_pool(self, pool_id):
        return self.items


class _FakePools:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    def get(self, pool_id):
        return object() if self._exists else None


def test_list_by_pool_returns_results_when_pool_exists():
    service = ResultService(results=_FakeResults(items=["r1", "r2"]), matches=None, audit=None, pools=_FakePools(True))
    assert service.list_by_pool(uuid.uuid4()) == ["r1", "r2"]


def test_list_by_pool_raises_not_found_for_unknown_pool():
    service = ResultService(results=_FakeResults(), matches=None, audit=None, pools=_FakePools(False))
    with pytest.raises(NotFoundError):
        service.list_by_pool(uuid.uuid4())
