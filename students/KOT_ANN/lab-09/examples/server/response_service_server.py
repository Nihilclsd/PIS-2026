import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grpc
from concurrent import futures
import time
import logging
from datetime import datetime
from typing import Dict, List

from generated import response_service_pb2
from generated import response_service_pb2_grpc


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseServiceServicer(response_service_pb2_grpc.ResponseServiceServicer):
    
    def __init__(self):
        self._responses: Dict[str, dict] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        sample = {
            "response_id": "RESP-001",
            "form_id": "FORM-42",
            "answers": {"name": "Иван", "rating": "5", "comment": "Отлично!"},
            "started_at": int(datetime.now().timestamp()),
            "submitted_at": int(datetime.now().timestamp()),
            "ip_address": "77.88.55.66",
            "user_agent": "Mozilla/5.0",
            "geo_country": "Россия",
            "geo_city": "Москва",
            "device_type": "DESKTOP",
            "filling_time_sec": 150,
            "quality_score": 0.95,
            "is_suspect": False,
            "suspect_reason": None
        }
        self._responses["RESP-001"] = sample
    
    def ProcessResponse(self, request, context):
        logger.info(f"Processing response {request.response_id}")
        
        filling_time = request.submitted_at - request.started_at
        
        response_data = {
            "response_id": request.response_id,
            "form_id": request.form_id,
            "answers": dict(request.answers),
            "started_at": request.started_at,
            "submitted_at": request.submitted_at,
            "ip_address": request.ip_address,
            "user_agent": request.user_agent,
            "filling_time_sec": filling_time,
            "quality_score": 0.95,
            "is_suspect": False,
            "suspect_reason": None
        }
        
        if filling_time < 30:
            response_data["quality_score"] = 0.15
            response_data["is_suspect"] = True
            response_data["suspect_reason"] = "filling_time_too_short"
        
        self._responses[request.response_id] = response_data
        
        return response_service_pb2.ProcessResponseResponse(
            is_suspect=response_data["is_suspect"],
            quality_score=response_data["quality_score"],
            suspect_reason=response_data["suspect_reason"] or ""
        )
    
    def GetResponse(self, request, context):
        logger.info(f"Getting response {request.response_id}")
        
        data = self._responses.get(request.response_id)
        if not data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Response {request.response_id} not found")
            return response_service_pb2.ResponseDto()
        
        return response_service_pb2.ResponseDto(
            response_id=data["response_id"],
            form_id=data["form_id"],
            answers=data["answers"],
            started_at=data["started_at"],
            submitted_at=data["submitted_at"],
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
            geo_country=data.get("geo_country", ""),
            geo_city=data.get("geo_city", ""),
            device_type=data.get("device_type", ""),
            filling_time_sec=data.get("filling_time_sec", 0),
            quality_score=data.get("quality_score", 0.0),
            is_suspect=data.get("is_suspect", False),
            suspect_reason=data.get("suspect_reason", "")
        )
    
    def ReclassifyResponse(self, request, context):
        logger.info(f"Reclassifying response {request.response_id}")
        
        data = self._responses.get(request.response_id)
        if not data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return response_service_pb2.ReclassifyResponseResponse()
        
        data["quality_score"] = request.quality_score
        data["is_suspect"] = request.is_suspect
        data["suspect_reason"] = request.suspect_reason
        
        return response_service_pb2.ReclassifyResponseResponse(
            response_id=request.response_id,
            is_suspect=request.is_suspect,
            quality_score=request.quality_score
        )
    
    def ListResponses(self, request, context):
        logger.info(f"Listing responses for form {request.form_id}")
        
        responses = []
        for data in self._responses.values():
            if data["form_id"] == request.form_id:
                if request.only_quality and data["is_suspect"]:
                    continue
                responses.append(response_service_pb2.ResponseDto(
                    response_id=data["response_id"],
                    form_id=data["form_id"],
                    answers=data["answers"],
                    started_at=data["started_at"],
                    submitted_at=data["submitted_at"],
                    ip_address=data.get("ip_address", ""),
                    user_agent=data.get("user_agent", ""),
                    geo_country=data.get("geo_country", ""),
                    geo_city=data.get("geo_city", ""),
                    device_type=data.get("device_type", ""),
                    filling_time_sec=data.get("filling_time_sec", 0),
                    quality_score=data.get("quality_score", 0.0),
                    is_suspect=data.get("is_suspect", False),
                    suspect_reason=data.get("suspect_reason", "")
                ))
        
        total = len(responses)
        start = request.offset
        end = start + request.limit
        paginated = responses[start:end]
        
        return response_service_pb2.ListResponsesResponse(
            responses=paginated,
            total=total
        )
    
    def GetFormStats(self, request, context):
        logger.info(f"Getting stats for form {request.form_id}")
        
        total = 0
        quality = 0
        suspect = 0
        quality_sum = 0.0
        rating_sum = 0.0
        
        for data in self._responses.values():
            if data["form_id"] == request.form_id:
                total += 1
                if data["is_suspect"]:
                    suspect += 1
                else:
                    quality += 1
                    quality_sum += data["quality_score"]
                    rating = data["answers"].get("rating", "0")
                    try:
                        rating_sum += int(rating)
                    except ValueError:
                        pass
        
        avg_quality = quality_sum / quality if quality > 0 else 0.0
        avg_rating = rating_sum / total if total > 0 else 0.0
        
        return response_service_pb2.FormStatsDto(
            form_id=request.form_id,
            total_responses=total,
            quality_responses=quality,
            suspect_responses=suspect,
            average_quality=avg_quality,
            average_rating=avg_rating
        )
    
    def StreamResponses(self, request, context):
        logger.info(f"Starting stream for form {request.form_id}")
        
        interval = request.interval_sec if request.interval_sec > 0 else 2
        
        while context.is_active():
            for data in self._responses.values():
                if data["form_id"] == request.form_id:
                    yield response_service_pb2.StreamResponsesResponse(
                        response_id=data["response_id"],
                        form_id=data["form_id"],
                        is_suspect=data["is_suspect"],
                        quality_score=data["quality_score"],
                        submitted_at=data["submitted_at"]
                    )
            time.sleep(interval)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    response_service_pb2_grpc.add_ResponseServiceServicer_to_server(
        ResponseServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("gRPC Server started on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()