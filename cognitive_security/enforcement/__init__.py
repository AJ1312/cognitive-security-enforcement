"""Enforcement and friction injection components."""

from cognitive_security.enforcement.friction import SecurityIntervention, CognitiveFrictionEngine
from cognitive_security.enforcement.sandbox import ActionSandbox

__all__ = ["SecurityIntervention", "CognitiveFrictionEngine", "ActionSandbox"]
