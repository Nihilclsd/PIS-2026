from dataclasses import dataclass


@dataclass
class FormAggregatesDto:
    """Read DTO: Агрегированные метрики формы"""
    
    form_id: str
    total_responses: int
    quality_responses: int
    suspect_responses: int
    average_rating: float
    quality_rate: float
    suspect_rate: float
    
    @classmethod
    def from_domain(cls, aggregates) -> "FormAggregatesDto":
        """Создаёт DTO из доменного Value Object FormAggregates"""
        if aggregates is None:
            return None
        return cls(
            form_id=aggregates.form_id,
            total_responses=aggregates.total_responses,
            quality_responses=aggregates.quality_responses,
            suspect_responses=aggregates.suspect_responses,
            average_rating=aggregates.average_rating,
            quality_rate=aggregates.quality_rate,
            suspect_rate=aggregates.suspect_rate,
        )