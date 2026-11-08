"""Immutable v1 contracts for bounded, local research assurance."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from typing import Optional, Tuple


def text(value):
    """Require explicit nonblank identifiers and descriptions."""
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError('nonblank, trimmed text required')


def number(value, minimum=0.0, maximum=1.0):
    """Reject booleans, NaN and infinities as measurements."""
    if type(value) not in (int, float) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError('finite numeric value outside permitted range')


def timestamp(value):
    """Require timezone-aware timestamps; normalize for comparisons."""
    if not isinstance(value, str):
        raise ValueError('timestamp string required')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result.astimezone(timezone.utc)


def window(observed_at, expires_at):
    if timestamp(observed_at) >= timestamp(expires_at):
        raise ValueError('expiry must follow observation')


def digest(value):
    """Canonical content fingerprint, not an authenticity certificate."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Capability:
    id: str
    state: str = 'unmeasured'
    value: Optional[float] = None

    def __post_init__(self):
        text(self.id)
        if self.state not in {'observed', 'unmeasured', 'unavailable', 'failed'}:
            raise ValueError('unknown capability state')
        if self.state == 'observed':
            number(self.value)
        elif self.value is not None:
            raise ValueError('only observed capabilities carry measurements')


@dataclass(frozen=True)
class Artifact:
    id: str
    sha256: str
    source: str
    scope: str
    observed_at: str
    expires_at: str
    schema_version: int = 1

    def __post_init__(self):
        for value in (self.id, self.source, self.scope):
            text(value)
        if not isinstance(self.sha256, str) or not re.fullmatch('[0-9a-f]{64}', self.sha256):
            raise ValueError('lowercase SHA256 required')
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int) or self.schema_version != 1:
            raise ValueError('unsupported artifact schema')
        window(self.observed_at, self.expires_at)


@dataclass(frozen=True)
class Claim:
    id: str
    domain: str
    statement: str
    scope: str
    owner: str
    assumptions: Tuple[str, ...] = ()
    schema_version: int = 1

    def __post_init__(self):
        for value in (self.id, self.domain, self.statement, self.scope, self.owner):
            text(value)
        if not isinstance(self.assumptions, tuple):
            raise ValueError('immutable assumption tuple required')
        for assumption in self.assumptions:
            text(assumption)
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int) or self.schema_version != 1:
            raise ValueError('unsupported claim schema')


@dataclass(frozen=True)
class Dependency:
    source: str
    target: str
    relation: str = 'depends_on'

    def __post_init__(self):
        text(self.source)
        text(self.target)
        if self.source == self.target or self.relation not in {'depends_on', 'supports', 'contradicts'}:
            raise ValueError('invalid relationship')


@dataclass(frozen=True)
class VerificationResult:
    subject: str
    snapshot: str
    reviewer: str
    scope: str
    reviewed_at: str
    expires_at: str

    def __post_init__(self):
        for value in (self.subject, self.reviewer, self.scope):
            text(value)
        if not isinstance(self.snapshot, str) or not re.fullmatch('[0-9a-f]{64}', self.snapshot):
            raise ValueError('snapshot fingerprint required')
        window(self.reviewed_at, self.expires_at)


@dataclass(frozen=True)
class Authorization:
    principal: str
    subject: str
    action: str
    snapshot: str
    granted_at: str
    expires_at: str
    max_cost: float

    def __post_init__(self):
        for value in (self.principal, self.subject, self.action):
            text(value)
        if not isinstance(self.snapshot, str) or not re.fullmatch('[0-9a-f]{64}', self.snapshot):
            raise ValueError('snapshot fingerprint required')
        window(self.granted_at, self.expires_at)
        number(self.max_cost, maximum=1e12)


def record(value):
    """Retain contract type with its versioned fields during exchange."""
    if not isinstance(value, (Artifact, Authorization, Capability, Claim, Dependency, VerificationResult)):
        raise ValueError('known contract required')
    return {'schema_version': 1, 'type': type(value).__name__, 'fields': asdict(value)}


def from_record(envelope):
    """Reconstruct an exact v1 exchange record; never import registry trust state."""
    from dataclasses import fields
    if (not isinstance(envelope, dict) or set(envelope) != {'schema_version', 'type', 'fields'}
            or isinstance(envelope['schema_version'], bool)
            or not isinstance(envelope['schema_version'], int) or envelope['schema_version'] != 1):
        raise ValueError('exact v1 record envelope required')
    classes = {cls.__name__: cls for cls in (Artifact, Authorization, Capability, Claim,
                                            Dependency, VerificationResult)}
    kind = envelope['type']
    if not isinstance(kind, str) or kind not in classes:
        raise ValueError('unknown record type')
    cls = classes[kind]
    values = envelope['fields']
    if not isinstance(values, dict) or set(values) != {field.name for field in fields(cls)}:
        raise ValueError('exact contract fields required')
    values = dict(values)
    if cls is Claim:
        if not isinstance(values['assumptions'], (list, tuple)):
            raise ValueError('assumption array required')
        values['assumptions'] = tuple(values['assumptions'])
    try:
        return cls(**values)
    except (TypeError, KeyError) as error:
        raise ValueError('invalid contract field types') from error
