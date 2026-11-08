"""Domain-neutral local assurance, separate from equipment and trading control."""
from .contracts import Artifact, Authorization, Capability, Claim, Dependency, VerificationResult, from_record, record
from .gaps import analyze_capabilities
from .registry import Registry

__all__ = ['Artifact', 'Authorization', 'Capability', 'Claim', 'Dependency',
           'VerificationResult', 'Registry', 'analyze_capabilities', 'record', 'from_record']
