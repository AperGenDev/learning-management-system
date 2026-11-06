"""gRPC-сервер сервиса рекомендаций
Запуск из корня проекта:
    python -m recommendation_service.server
"""
import logging
import os
from concurrent import futures

import grpc

from grpc_contracts import recommendation_pb2 as pb2
from grpc_contracts import recommendation_pb2_grpc as pb2_grpc
from recommendation_service.recommender import Course, recommend

logging.basicConfig(level=logging.INFO, format="%(asctime)s [gRPC] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("recommendation")


def _to_course(info: pb2.CourseInfo) -> Course:
    return Course(id=info.id, category_id=info.category_id, students_count=info.students_count)


class RecommendationServicer(pb2_grpc.RecommendationServiceServicer):
    """Реализация метода, описанного в recommendation.proto."""

    def GetRecommendations(self, request: pb2.RecommendationRequest, context) -> pb2.RecommendationResponse:
        log.info(
            "<-- запрос GetRecommendations: student_id=%s, записан на курсы %s, кандидатов в каталоге: %s, limit=%s",
            request.student_id, [c.id for c in request.enrolled], len(request.candidates), request.limit,
        )

        items = recommend(
            enrolled=[_to_course(c) for c in request.enrolled],
            candidates=[_to_course(c) for c in request.candidates],
            limit=request.limit,
        )

        response = pb2.RecommendationResponse(
            items=[pb2.RecommendedCourse(course_id=i.course_id, score=i.score, reason=i.reason) for i in items]
        )
        log.info("--> ответ: %s", [(i.course_id, i.score) for i in items])
        return response


def serve() -> None:
    port = int(os.getenv("RECOMMENDATION_PORT", "50051"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #
    pb2_grpc.add_RecommendationServiceServicer_to_server(RecommendationServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    log.info("Сервис рекомендаций запущен, слушает порт %s", port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
