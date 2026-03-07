from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class DetectionResponse(BaseModel):
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    source: str
    placeholder: str | None = None


class PseudonymizeResponse(BaseModel):
    text: str
    mapping: dict[str, str] | None = None
    detections: list[DetectionResponse] | None = None


class DepseudonymizeResponse(BaseModel):
    text: str


class SupportedClassesResponse(BaseModel):
    classes: list[str]
