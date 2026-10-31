# State-of-the-art roadmap and evidence gates

## Delivered
- Evidence-aware property research and map UI.
- Comparable sales abstention when insufficient independently documented transactions exist.
- Ownership due-diligence checklist (not an official search).
- Regen Insight HTTPS adapter (requires actual authorized endpoint).
- Time-split experimental regression with independent parcel filtering.
- Transaction source and license validation, spatial holdout diagnostics, interval coverage and drift utilities.
- CI unit tests.

## Not yet implemented or validated
1. **Actual historical sales ingestion:** obtain authorized machine-readable transactions; record provenance, sale date, parcel tenure and legal permitted use. Regional published asking-price indices are contextual data only.
2. **Geospatial ETL:** Overture/OSM roads, WorldPop population, Dynamic World or ESA WorldCover land cover, Sentinel-2/Landsat imagery, CHIRPS rainfall and DEM-derived flood features. Check licenses and data currency.
3. **Remote-sensing inference:** cloud masking, co-registration, seasonal comparison, segmentation and independent labeled change-detection evaluation.
4. **Environmental integration:** agree Regen Insight contract, schema, authentication, hazard methodology, confidence, versioning and data staleness checks. Never treat no response as low risk.
5. **Model comparison:** hedonic baseline, CatBoost/LightGBM, spatial-temporal gradient boosting, uncertainty intervals and geographically blocked validation. Add fairness and shift analysis by county, tenure and price bracket.
6. **Ownership workflows:** integrate only official authorized land-search documents; redact private identities; secure storage and audit access. Never scrape restricted title-holder records.
7. **Property tours:** licensed Cesium 3D Tiles / terrain with a visible simulated-tour label, not purported real drone footage.
8. **Production controls:** user auth, authorization, rate limits, encryption, secrets, audit logs, disaster recovery, consent and legal review.
9. **Delivery:** stage deployment, penetration testing, performance/load tests, accessibility review and monitoring.

Do not label a model 'SOTA' solely based on architecture. Require independently reproduced accuracy and calibration against representative Kenya market benchmarks.
