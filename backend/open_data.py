"""Licensed national background indicators for research, NOT parcel valuation."""
import os
from secrets import compare_digest

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from backend.kenya_open_data_client import (
    DATASET_IDS,
    HubPermissionDenied,
    HubUnavailable,
    fetch_public_context,
)

router = APIRouter(prefix="/api/open-data/kenya", tags=["kenya-open-data"])


def require_data_access(x_ardhi_data_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("ARDHI_OPEN_DATA_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Open data access not configured")
    if not x_ardhi_data_key or not compare_digest(x_ardhi_data_key, expected):
        raise HTTPException(status_code=401, detail="Restricted public-data research API")


@router.get("/datasets", dependencies=[Depends(require_data_access)])
def datasets() -> dict:
    return {
        "datasets": sorted(DATASET_IDS),
        "readiness": "gateway_configuration_required",
        "note": "National data is only contextual. This is not a land title check or valuation model.",
    }


@router.get("/{dataset_id}", dependencies=[Depends(require_data_access)])
async def kenya_data(
    dataset_id: str,
    from_year: int | None = Query(default=None, ge=1960, le=2100),
    to_year: int | None = Query(default=None, ge=1960, le=2100),
    max_points: int = Query(default=30, ge=1, le=100),
) -> dict:
    try:
        return await fetch_public_context(
            dataset_id, from_year=from_year, to_year=to_year, max_points=max_points
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HubPermissionDenied as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except HubUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
