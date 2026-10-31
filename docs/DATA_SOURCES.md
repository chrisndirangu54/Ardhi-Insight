# Data provenance and integration boundaries

- **HassConsult land indices:** Published historical regional price reports. Use only with appropriate licensing, dated sources, geographic normalization and correct units. Not transaction-level parcel evidence.
- **KNBS and KBA:** Property/housing and socioeconomic indices; residential housing prices must not be represented as vacant land transaction prices.
- **Official Ardhisasa:** Ownership verification via authorized official land searches; this repository does not access private registry records or assert ownership.
- **OpenStreetMap:** Streets and amenities; observe ODbL and service use policies, cache responsibly. Road-network travel time is not equivalent to Haversine proximity.
- **WorldPop, Digital Earth Africa, CHIRPS:** Public population, EO, rainfall and geospatial indicators; ingest with licenses, temporal provenance and geographic accuracy tracked.
- **Regen Insight:** Configure REGEN_INSIGHT_URL (HTTPS only) and optionally REGEN_INSIGHT_TOKEN. The connector assumes a JSON POST with latitude and longitude; confirm the real service schema before production. No risk score is fabricated when the service is unavailable.

Before machine learning training: acquire sufficient historical parcel-level observations, segment by land use and tenure, remove temporal/spatial leakage, validate against independent time and geographic holdouts, estimate uncertainty, and audit potential bias. All demo listings are illustrative.
