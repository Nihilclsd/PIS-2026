from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ReclassifyResponseCommand:
    """Команда: ручная переклассификация ответа"""
    
    response_id: str
    quality_score: float
    is_suspect: bool
    suspect_reason: Optional[str] = None
    
    def __post_init__(self):
        if not self.response_id or not self.response_id.strip():
            raise ValueError("response_id cannot be empty")
        if not 0 <= self.quality_score <= 1:
            raise ValueError("quality_score must be between 0 and 1")
        if self.is_suspect and not self.suspect_reason:
            raise ValueError("suspect_reason is required when is_suspect=True")