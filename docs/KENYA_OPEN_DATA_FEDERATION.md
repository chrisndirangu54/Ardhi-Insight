# Ardhi Insight — Kenya Open Data federation

New routes: GET /api/open-data/kenya/datasets and GET /api/open-data/kenya/{dataset_id}.
Requests require the X-Ardhi-Data-Key header matching the server-only
ARDHI_OPEN_DATA_API_KEY environment variable. Never put this secret in the
Flutter/web client or a mobile app. Use backend authorization when product
user accounts are available. The route returns *context*, not valuations.

Deployment environment:
- KENYA_DATA_GATEWAY_URL: HTTPS URL of the deployed TeknTandao Workspace
  kenyaOpenDataFederation HTTP function.
- KENYA_DATA_GATEWAY_AUDIENCE: exact Google OIDC audience of that function.
- ARDHI_OPEN_DATA_API_KEY: private authorization secret for current Ardhi
  research routes. This is a temporary admin API access measure; replace
  with your existing authenticated user/role permissions before public launch.

Run the Ardhi API using a dedicated Google Cloud workload service account,
registered in Workspace KENYA_DATA_CLIENTS_JSON as app=ardhi_insight.
The backend retrieves short-lived identity tokens via the Google Cloud
metadata server. Local runs or non-GCP hosting without workload identity
fail with 503; no service account key material is stored in the repo.

Example: GET /api/open-data/kenya/population?from_year=2015&to_year=2024
Header: X-Ardhi-Data-Key: <server-side-only-key>

Supported: World Bank Kenya national indicators, geoBoundaries county
boundary *metadata*. National growth/urbanization cannot be used to
estimate a specific parcel or county. Boundary metadata is not an
authoritative land parcel register. Never use this endpoint for ownership
verification, a trained property appraisal, or fraud/risk scoring.

Tests: python -m unittest backend.test_kenya_open_data_client
Prerequisite PR: TeknTandao Workspace PR #37; gateway must be deployed
and an identity allowlist configured separately.
