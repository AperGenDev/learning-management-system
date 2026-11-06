from fastapi import APIRouter, Depends, Query

from backend.api.deps import get_recommendation_service, require_role
from backend.models import User
from backend.schemas.recommendation import RecommendationRead
from backend.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=list[RecommendationRead])
def recommendations(limit: int = Query(default=5, ge=1, le=20),
                    svc: RecommendationService = Depends(get_recommendation_service),
                    user: User = Depends(require_role("student"))):
    return svc.for_student(user, limit)
