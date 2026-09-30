"""Simulated legacy data source.

This represents the shape of data COMPET LAB might receive from an old
historical system: flat records, string identifiers, inconsistent
casing, no notion of the modern domain's invariants.

This is intentionally NOT a real system -- it is a fixture used to
demonstrate the Anti-Corruption Layer pattern (see adapter.py).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LegacyCompetitionRecord:
    """Example shape of a record as it might come out of the legacy
    FFF-like system: no UUIDs, free-text status, string dates."""

    legacy_id: str
    label: str
    category_code: str  # e.g. "U15", not validated against any enum
    kind: str  # e.g. "CHAMPIONNAT", "COUPE" (French, legacy vocabulary)
    active_flag: str  # "O" / "N" -- legacy boolean encoding
