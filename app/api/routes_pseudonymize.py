from fastapi import APIRouter, Depends

from app.api.dependencies import get_detection_pipeline, get_pseudonymizer
from app.detection.pipeline import DetectionPipeline
from app.replacement.pseudonymizer import TextPseudonymizer
from app.schemas.requests import PseudonymizeRequest
from app.schemas.responses import DetectionResponse, PseudonymizeResponse

router = APIRouter(tags=["pseudonymize"])


@router.post("/pseudonymize", response_model=PseudonymizeResponse)
def pseudonymize(
    payload: PseudonymizeRequest,
    pipeline: DetectionPipeline = Depends(get_detection_pipeline),
    pseudonymizer: TextPseudonymizer = Depends(get_pseudonymizer),
) -> PseudonymizeResponse:
    detections = pipeline.analyze(
        text=payload.text,
        classes=payload.classes,
        language=payload.language.value,
    )
    # split_name mode is reserved for a future extension; v1 always applies full-span replacement
    result = pseudonymizer.pseudonymize(payload.text, detections)

    mapping = result.mapping if payload.options.return_mapping else None
    response_detections = None
    if payload.options.include_detections:
        response_detections = [
            DetectionResponse(
                entity_type=applied.detection.entity_type.value,
                text=applied.detection.text,
                start=applied.detection.start,
                end=applied.detection.end,
                confidence=applied.detection.confidence,
                source=applied.detection.source,
                placeholder=applied.placeholder,
            )
            for applied in result.applied_detections
        ]

    return PseudonymizeResponse(
        text=result.text,
        mapping=mapping,
        detections=response_detections,
    )
