# Ardhi Insight

An early-stage Kenyan land marketplace prototype with geospatial proximity, investment scenarios, ownership due-diligence guidance, and a configurable Regen Insight environmental connector.

## Local setup

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000 . Swagger docs: http://127.0.0.1:8000/docs .

## API routes

- `GET /api/listings` – illustrative listing catalog (not genuine sales offers)
- `GET /api/listings/{id}/intelligence` – major Kenyan urban-centre distances, ownership caveats, regional observations, and environmental screening availability
- `POST /api/intelligence/environment` – Regen Insight JSON connector, disabled safely until configured
- `POST /api/investment/simulate` – hypothetical scenario calculations, **not predictions**
- `GET /api/market/observations` – sourced historical market observations registry (currently empty pending verified licensed data)

For Regen integration set `REGEN_INSIGHT_URL=https://your-authorized-service/assessment` and `REGEN_INSIGHT_TOKEN` using deployment secrets. The endpoint's contract must match `{latitude,longitude}` input; do not commit credentials. The adapter does not verify Regen's actual API contract or authentication scheme.

The map, historical price ingestion, ownership-record verification, learned land appreciation model and virtual drone simulation discussed in planning have **not** been fully integrated into this GitHub version. See [Data sources and constraints](docs/DATA_SOURCES.md).

## Key boundaries

- Public land market indicators are not property-level valuations.
- Ardhisasa searches require official authorization and are not silently performed.
- Environment requests without a configured upstream return `not_configured`, not a zero-risk assertion.
- No actual model has been trained on transaction records.
- Production security, privacy, tests and hosting are still required.
