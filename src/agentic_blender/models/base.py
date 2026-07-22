"""Shared configuration for serialized Pydantic models."""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


def utc_now() -> datetime.datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


class FrozenModel(BaseModel):
    """Base for validated models with attribute-level immutability."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
    )
