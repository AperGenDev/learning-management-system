"""gRPC-клиент сервиса рекомендаций. API Service вызывает удалённый метод
GetRecommendations как обычная функция Python.

Модуль зависит только от grpc и сгенерированного контракта  без БД и FastAPI.
"""
from dataclasses import dataclass

import grpc

from grpc_contracts import recommendation_pb2 as pb2
from grpc_contracts import recommendation_pb2_grpc as pb2_grpc


class RecommendationUnavailable(Exception):
    """gRPC-сервис не ответил (не запущен, упал, таймаут)."""


@dataclass(frozen=True)
class CourseInfo:
    id: int
    category_id: int | None
    students_count: int


@dataclass(frozen=True)
class RecommendedItem:
    course_id: int
    score: float
    reason: str


class RecommendationClient:
    def __init__(self, host: str, port: int, timeout: float = 3.0):
        self.target = f"{host}:{port}"
        self.timeout = timeout

    @staticmethod
    def _to_proto(course: CourseInfo) -> pb2.CourseInfo:
        return pb2.CourseInfo(
            id=course.id,
            category_id=course.category_id or 0,
            students_count=course.students_count,
        )

    def get_recommendations(
        self, student_id: int, enrolled: list[CourseInfo], candidates: list[CourseInfo], limit: int
    ) -> list[RecommendedItem]:
        request = pb2.RecommendationRequest(
            student_id=student_id,
            enrolled=[self._to_proto(c) for c in enrolled],
            candidates=[self._to_proto(c) for c in candidates],
            limit=limit,
        )
        try:
            #Канал соединение с сервером по адресу self.target, insecure - без шифров-я
            with grpc.insecure_channel(self.target) as channel:
                stub = pb2_grpc.RecommendationServiceStub(channel)
                response = stub.GetRecommendations(request, timeout=self.timeout)
        except grpc.RpcError as exc:
            raise RecommendationUnavailable(f"{exc.code().name}: {exc.details()}") from exc

        return [RecommendedItem(i.course_id, i.score, i.reason) for i in response.items]
