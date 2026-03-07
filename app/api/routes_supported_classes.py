from fastapi import APIRouter, Depends

from app.api.dependencies import get_detection_pipeline
from app.detection.pipeline import DetectionPipeline
from app.schemas.responses import SupportedClassesResponse

router = APIRouter(tags=["supported-classes"])


@router.get("/supported-classes", response_model=SupportedClassesResponse)
def supported_classes(
    pipeline: DetectionPipeline = Depends(get_detection_pipeline),
) -> SupportedClassesResponse:
    return SupportedClassesResponse(classes=pipeline.supported_classes())
