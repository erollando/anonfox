from fastapi import APIRouter, Depends

from app.api.dependencies import get_depseudonymizer
from app.reversal.depseudonymizer import TextDepseudonymizer
from app.schemas.requests import DepseudonymizeRequest
from app.schemas.responses import DepseudonymizeResponse

router = APIRouter(tags=["depseudonymize"])


@router.post("/depseudonymize", response_model=DepseudonymizeResponse)
def depseudonymize(
    payload: DepseudonymizeRequest,
    depseudonymizer: TextDepseudonymizer = Depends(get_depseudonymizer),
) -> DepseudonymizeResponse:
    return DepseudonymizeResponse(
        text=depseudonymizer.depseudonymize(payload.text, payload.mapping)
    )
