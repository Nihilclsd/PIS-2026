from dataclasses import dataclass


@dataclass(frozen=True)
class GetFormQuery:
    form_id: str