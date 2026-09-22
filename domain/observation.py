from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EpistemicStatus(str, Enum):
    DECLARED = "DECLARED"
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    ASSUMED = "ASSUMED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"
    AGING = "AGING"
    STALE = "STALE"


class FreshnessPolicy(BaseModel):
    provider_id: str | None = None
    fresh_max_age_seconds: int | None = None
    aging_max_age_seconds: int | None = None
    stale_max_age_seconds: int | None = None


class PrinterObservation(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    printer_identity: str
    printer_state: str
    job_state: str | None = None
    consumables: dict[str, Any] | None = None
    media_state: dict[str, Any] | None = None
    error_state: dict[str, Any] | None = None
    source: str | None = None
    provider: str | None = None
    provider_version: str | None = None
    retrieval_timestamp: datetime | None = None
    raw_provider_data: dict[str, Any] | None = None
    normalized_data: dict[str, Any] | None = None
    epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED
    provenance: dict[str, Any] = Field(default_factory=dict)


def observation_age_seconds(observation: PrinterObservation, now: datetime) -> float:
    retrieval = observation.retrieval_timestamp or observation.timestamp
    return (now - retrieval).total_seconds()


def qualify_observation(observation: PrinterObservation, policy: FreshnessPolicy, now: datetime) -> PrinterObservation:
    if observation.epistemic_status in (EpistemicStatus.UNKNOWN, EpistemicStatus.STALE, EpistemicStatus.CONTRADICTED):
        return observation
    age = observation_age_seconds(observation, now)
    updated = observation.model_copy()
    if policy.stale_max_age_seconds is not None and age > policy.stale_max_age_seconds:
        updated.epistemic_status = EpistemicStatus.STALE
    elif policy.aging_max_age_seconds is not None and age > policy.aging_max_age_seconds or policy.fresh_max_age_seconds is not None and age > policy.fresh_max_age_seconds:
        updated.epistemic_status = EpistemicStatus.AGING
    return updated
