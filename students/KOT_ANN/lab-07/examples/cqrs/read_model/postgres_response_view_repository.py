import json
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from cqrs.read_model.response_view import ResponseView
from cqrs.read_model.response_view_repository import ResponseViewRepository
from infrastructure.config.models import ResponseViewModel


logger = logging.getLogger(__name__)


class PostgresResponseViewRepository(ResponseViewRepository):
    """PostgreSQL реализация Read Model репозитория"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, view: ResponseView) -> None:
        """Сохраняет Read Model в отдельную таблицу"""
        db_view = ResponseViewModel(
            response_id=view.response_id,
            form_id=view.form_id,
            form_title=view.form_title,
            answers=json.dumps(view.answers),
            rating=view.rating,
            comment=view.comment,
            started_at=view.started_at,
            submitted_at=view.submitted_at,
            filling_time_sec=view.filling_time_sec,
            ip_address=view.ip_address,
            country=view.country,
            city=view.city,
            device_type=view.device_type,
            is_suspect=view.is_suspect,
            quality_score=view.quality_score,
            created_at=view.created_at,
            updated_at=view.updated_at
        )
        self.session.merge(db_view)
        self.session.commit()
        logger.info(f"ResponseView saved for {view.response_id}")
    
    def find_by_id(self, response_id: str) -> Optional[ResponseView]:
        """Находит ответ по ID"""
        db_view = self.session.query(ResponseViewModel).filter(
            ResponseViewModel.response_id == response_id
        ).first()
        if not db_view:
            return None
        return self._to_domain(db_view)
    
    def find_by_form_id(
        self, 
        form_id: str, 
        limit: int = 100, 
        offset: int = 0,
        only_quality: bool = False
    ) -> List[ResponseView]:
        """Находит ответы по форме с пагинацией"""
        query = self.session.query(ResponseViewModel).filter(
            ResponseViewModel.form_id == form_id
        )
        if only_quality:
            query = query.filter(ResponseViewModel.is_suspect == False)
        
        db_views = query.order_by(
            desc(ResponseViewModel.submitted_at)
        ).offset(offset).limit(limit).all()
        
        return [self._to_domain(v) for v in db_views]
    
    def find_low_rating_responses(self, form_id: str, threshold: int = 3) -> List[ResponseView]:
        """Находит ответы с низкой оценкой"""
        db_views = self.session.query(ResponseViewModel).filter(
            ResponseViewModel.form_id == form_id,
            ResponseViewModel.rating <= threshold,
            ResponseViewModel.rating.isnot(None)
        ).order_by(ResponseViewModel.rating).all()
        
        return [self._to_domain(v) for v in db_views]
    
    def get_statistics(self, form_id: str) -> dict:
        """Возвращает агрегированную статистику"""
        stats = self.session.query(
            func.count(ResponseViewModel.response_id).label("total"),
            func.sum(func.cast(ResponseViewModel.is_suspect == False, int)).label("quality"),
            func.sum(func.cast(ResponseViewModel.is_suspect == True, int)).label("suspect"),
            func.avg(ResponseViewModel.quality_score).label("avg_quality"),
            func.avg(ResponseViewModel.rating).label("avg_rating")
        ).filter(ResponseViewModel.form_id == form_id).first()
        
        return {
            "form_id": form_id,
            "total_responses": stats.total or 0,
            "quality_responses": stats.quality or 0,
            "suspect_responses": stats.suspect or 0,
            "average_quality_score": float(stats.avg_quality) if stats.avg_quality else 0.0,
            "average_rating": float(stats.avg_rating) if stats.avg_rating else 0.0
        }
    
    def _to_domain(self, db_view: ResponseViewModel) -> ResponseView:
        """Преобразует ORM модель в ResponseView"""
        return ResponseView(
            response_id=db_view.response_id,
            form_id=db_view.form_id,
            form_title=db_view.form_title,
            answers=json.loads(db_view.answers) if db_view.answers else {},
            rating=db_view.rating,
            comment=db_view.comment,
            started_at=db_view.started_at,
            submitted_at=db_view.submitted_at,
            filling_time_sec=db_view.filling_time_sec,
            ip_address=db_view.ip_address,
            country=db_view.country,
            city=db_view.city,
            device_type=db_view.device_type,
            is_suspect=db_view.is_suspect,
            quality_score=db_view.quality_score,
            created_at=db_view.created_at,
            updated_at=db_view.updated_at
        )