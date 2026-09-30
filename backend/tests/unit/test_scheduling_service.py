"""SchedulingService tested with in-memory fakes -- no database."""
import uuid

import pytest

from app.application.scheduling.use_cases import SchedulingService
from app.domain.shared.exceptions import NotFoundError


class _EmptyPoolRepo:
    def get(self, pool_id):
        return None  # simulates "no pool with this id"


class _EmptyMatchRepo:
    def list_by_pool(self, pool_id):
        raise AssertionError("should not be reached: pool existence must be checked first")


def test_list_matches_on_unknown_pool_raises_not_found():
    """Regression test: this used to silently return [] (200 OK)
    instead of a 404, which was inconsistent with every other
    pool_id-keyed endpoint (e.g. /standings)."""
    service = SchedulingService(_EmptyPoolRepo(), _EmptyMatchRepo(), None)

    with pytest.raises(NotFoundError):
        service.list_matches(uuid.uuid4())


def test_detect_conflicts_on_unknown_pool_raises_not_found():
    service = SchedulingService(_EmptyPoolRepo(), _EmptyMatchRepo(), None)

    with pytest.raises(NotFoundError):
        service.detect_conflicts(uuid.uuid4())
