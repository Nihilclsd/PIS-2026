from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ProcessResponseCommand:
    """Команда: обработка ответа"""
    
    response_id: str
    form_id: str
    answers: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    started_at: datetime
    submitted_at: datetime
    
    def __post_init__(self):
        if not self.response_id or not self.response_id.strip():
            raise ValueError("response_id cannot be empty")
        if not self.form_id or not self.form_id.strip():
            raise ValueError("form_id cannot be empty")
        if not self.answers:
            raise ValueError("answers cannot be empty")
        if self.started_at > self.submitted_at:
            raise ValueError("started_at cannot be after submitted_at")