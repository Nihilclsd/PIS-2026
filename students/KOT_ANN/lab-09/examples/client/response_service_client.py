import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grpc
from datetime import datetime

from generated import response_service_pb2
from generated import response_service_pb2_grpc


class ResponseServiceClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = response_service_pb2_grpc.ResponseServiceStub(self.channel)
    
    def process_response(self, response_id, form_id, answers, ip_address, user_agent):
        request = response_service_pb2.ProcessResponseRequest(
            response_id=response_id,
            form_id=form_id,
            answers=answers,
            ip_address=ip_address,
            user_agent=user_agent,
            started_at=int(datetime.now().timestamp()),
            submitted_at=int(datetime.now().timestamp())
        )
        return self.stub.ProcessResponse(request)
    
    def get_response(self, response_id):
        request = response_service_pb2.GetResponseRequest(response_id=response_id)
        return self.stub.GetResponse(request)
    
    def reclassify_response(self, response_id, quality_score, is_suspect, suspect_reason):
        request = response_service_pb2.ReclassifyResponseRequest(
            response_id=response_id,
            quality_score=quality_score,
            is_suspect=is_suspect,
            suspect_reason=suspect_reason
        )
        return self.stub.ReclassifyResponse(request)
    
    def list_responses(self, form_id, limit=100, offset=0, only_quality=False):
        request = response_service_pb2.ListResponsesRequest(
            form_id=form_id,
            limit=limit,
            offset=offset,
            only_quality=only_quality
        )
        return self.stub.ListResponses(request)
    
    def get_form_stats(self, form_id):
        request = response_service_pb2.GetFormStatsRequest(form_id=form_id)
        return self.stub.GetFormStats(request)
    
    def stream_responses(self, form_id, interval_sec=2):
        request = response_service_pb2.StreamResponsesRequest(
            form_id=form_id,
            interval_sec=interval_sec
        )
        return self.stub.StreamResponses(request)


def main():
    client = ResponseServiceClient()
    
    print("\n=== ProcessResponse ===")
    response = client.process_response(
        response_id="RESP-001",
        form_id="FORM-42",
        answers={"name": "Иван", "rating": "5", "comment": "Отлично!"},
        ip_address="77.88.55.66",
        user_agent="Mozilla/5.0"
    )
    print(f"Is suspect: {response.is_suspect}")
    print(f"Quality score: {response.quality_score}")
    
    print("\n=== GetResponse ===")
    response_data = client.get_response("RESP-001")
    print(f"Response ID: {response_data.response_id}")
    print(f"Form ID: {response_data.form_id}")
    print(f"Is suspect: {response_data.is_suspect}")
    
    print("\n=== ListResponses ===")
    list_response = client.list_responses("FORM-42")
    print(f"Found {list_response.total} responses")
    
    print("\n=== GetFormStats ===")
    stats = client.get_form_stats("FORM-42")
    print(f"Total: {stats.total_responses}")
    print(f"Quality: {stats.quality_responses}")
    print(f"Suspect: {stats.suspect_responses}")
    
    print("\n=== StreamResponses ===")
    print("Streaming responses (press Ctrl+C to stop)...")
    try:
        for update in client.stream_responses("FORM-42", interval_sec=2):
            print(f"  -> {update.response_id} | is_suspect={update.is_suspect} | quality={update.quality_score}")
    except KeyboardInterrupt:
        print("\nStream stopped")


if __name__ == "__main__":
    main()