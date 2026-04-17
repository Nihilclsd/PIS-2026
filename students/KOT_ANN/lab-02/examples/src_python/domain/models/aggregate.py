"""
Value Object: Агрегированные метрики формы.
"""


class FormAggregates:
    """Агрегированные данные по форме"""
    
    def __init__(
        self,
        form_id: str,
        total_responses: int = 0,
        quality_responses: int = 0,
        suspect_responses: int = 0,
        average_rating: float = 0.0
    ):
        self.form_id = form_id
        self.total_responses = total_responses
        self.quality_responses = quality_responses
        self.suspect_responses = suspect_responses
        self.average_rating = average_rating
    
    def increment_total(self) -> None:
        """Увеличивает счётчик всех ответов"""
        self.total_responses += 1
    
    def increment_quality(self) -> None:
        """Увеличивает счётчик качественных ответов"""
        self.quality_responses += 1
    
    def increment_suspect(self) -> None:
        """Увеличивает счётчик подозрительных ответов"""
        self.suspect_responses += 1
    
    def update_average_rating(self, new_rating: float, current_total: int) -> None:
        """Обновляет средний рейтинг"""
        # TODO: полная реализация в Lab #3
        pass