from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class CreateFormCommand:
    form_id: str
    fields: List[Dict[str, Any]]
    anti_spam_settings: Dict[str, Any]