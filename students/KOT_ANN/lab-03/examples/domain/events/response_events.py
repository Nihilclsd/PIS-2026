from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ResponseClassifiedEvent:
    response_id: str
    form_id: str
    is_suspect: bool
    quality_score: float
    suspect_reason: Optional[str]
    occurred_at: datetime

@dataclass
class ResponseEnrichedEvent:
    """Событие: ответ обогащён гео-данными и данными об устройстве"""
    response_id: str
    form_id: str
    geo_country: Optional[str]
    geo_city: Optional[str]
    device_type: Optional[str]
    occurred_at: datetime