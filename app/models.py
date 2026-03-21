from dataclasses import dataclass, field


@dataclass
class SourceMatch:
    name: str
    type: str
    summary: str
    url: str
    data: dict = field(default_factory=dict)
    confidence: str | None = None
    rationale: str | None = None


@dataclass
class SourceResult:
    source: str
    query: str
    matches: list[SourceMatch] = field(default_factory=list)
    duration_ms: int = 0
    error: str | None = None
