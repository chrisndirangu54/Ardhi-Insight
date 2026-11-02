"""Read-only, authenticated Kenya Open Data federation client.

The client obtains an OIDC identity token from the Google Cloud metadata server.
No API key or service-account JSON file is accepted. Local runs fail closed.
Only the explicitly configured Workspace gateway is contacted.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

DATASET_IDS = frozenset({
    "population", "urban_population_pct", "gdp_growth_pct",
    "agriculture_gdp_pct", "electricity_access_pct", "health_expenditure_pct",
    "county_boundaries",
})
METADATA_IDENTITY = (
    "http://metadata.google.internal/computeMetadata/v1/"
    "instance/service-accounts/default/identity"
)


class HubUnavailable(Exception):
    """The shared hub is unconfigured or temporarily unavailable."""


class HubPermissionDenied(Exception):
    """The calling service is not allowlisted for this dataset."""


def get_configuration() -> tuple[str, str]:
    endpoint = os.getenv("KENYA_DATA_GATEWAY_URL", "").strip()
    audience = os.getenv("KENYA_DATA_GATEWAY_AUDIENCE", "").strip()
    if not endpoint or not audience:
        raise HubUnavailable("Kenya Open Data federation is not configured")
    parsed = httpx.URL(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.host
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.port not in (None, 443)
    ):
        raise HubUnavailable("Invalid federation endpoint configuration")
    if not audience.startswith("https://"):
        raise HubUnavailable("Federation audience must be HTTPS")
    return endpoint, audience


async def fetch_public_context(
    dataset_id: str,
    *,
    from_year: int | None = None,
    to_year: int | None = None,
    max_points: int = 30,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    if dataset_id not in DATASET_IDS:
        raise ValueError("Unknown or disallowed public dataset")
    if not isinstance(max_points, int) or not 1 <= max_points <= 100:
        raise ValueError("max_points outside supported range")
    for year in (from_year, to_year):
        if year is not None and (not isinstance(year, int) or not 1960 <= year <= 2100):
            raise ValueError("Invalid reference year")
    if from_year is not None and to_year is not None and from_year > to_year:
        raise ValueError("Invalid reference year range")
    endpoint, audience = get_configuration()

    async with httpx.AsyncClient(
        transport=transport, trust_env=False, timeout=12.0, follow_redirects=False
    ) as client:
        try:
            token_response = await client.get(
                METADATA_IDENTITY,
                params={"audience": audience, "format": "full"},
                headers={"Metadata-Flavor": "Google"},
                timeout=5.0,
            )
            token_response.raise_for_status()
            token = token_response.text.strip()
            if len(token) < 20 or len(token) > 20000:
                raise HubUnavailable("Cloud service identity unavailable")
            payload: dict[str, Any] = {
                "datasetId": dataset_id,
                "maxPoints": max_points,
            }
            if from_year is not None:
                payload["fromYear"] = from_year
            if to_year is not None:
                payload["toYear"] = to_year
            response = await client.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            raise HubUnavailable("Public-data gateway unreachable") from exc

    if response.status_code in (401, 403):
        raise HubPermissionDenied("Service identity is not authorized")
    if response.status_code != 200:
        raise HubUnavailable("Public-data gateway returned an unavailable response")
    try:
        result = response.json()
    except ValueError as exc:
        raise HubUnavailable("Malformed data response") from exc
    if (
        not isinstance(result, dict)
        or result.get("ok") is not True
        or not isinstance(result.get("data"), dict)
        or result["data"].get("datasetId") != dataset_id
        or not isinstance(result["data"].get("sourceId"), str)
        or not isinstance(result["data"].get("fetchedAt"), str)
    ):
        raise HubUnavailable("Invalid dataset provenance")
    record = result["data"]
    return {
        "source": "tekntandao_kenya_open_data_hub",
        "usage": "context_only",
        "data": record,
        "caveat": (
            "National indicators are not county-level or parcel-level estimates. "
            "The county boundary layer does not verify cadastral ownership."
        ),
    }
