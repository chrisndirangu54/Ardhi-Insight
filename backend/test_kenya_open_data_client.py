"""No live network: verifies fail-closed configuration and federation contract."""
import asyncio
import json
import os
import unittest
from unittest.mock import patch

import httpx

from backend.kenya_open_data_client import (
    HubPermissionDenied, HubUnavailable, fetch_public_context
)


class KenyaOpenDataFederationTests(unittest.TestCase):
    def test_unknown_dataset_rejected_before_network(self):
        with self.assertRaises(ValueError):
            asyncio.run(fetch_public_context("https://evil.example/dataset"))

    def test_missing_configuration_never_calls_upstream(self):
        with patch.dict(os.environ, {
            "KENYA_DATA_GATEWAY_URL": "",
            "KENYA_DATA_GATEWAY_AUDIENCE": "",
        }):
            with self.assertRaises(HubUnavailable):
                asyncio.run(fetch_public_context("population"))

    def test_authenticated_request_and_provenance(self):
        audience = "https://europe-west1-example.cloudfunctions.net/kenyaOpenDataFederation"
        observed = {"token": False, "payload": False}
        def transport(request: httpx.Request) -> httpx.Response:
            if request.url.host == "metadata.google.internal":
                self.assertEqual(request.headers["Metadata-Flavor"], "Google")
                self.assertEqual(request.url.params["audience"], audience)
                observed["token"] = True
                return httpx.Response(200, text="a" * 256)
            self.assertEqual(str(request.url), audience)
            self.assertEqual(request.headers["Authorization"], "Bearer " + "a" * 256)
            self.assertEqual(json.loads(request.content)["datasetId"], "population")
            observed["payload"] = True
            return httpx.Response(200, json={"ok": True, "data": {
                "datasetId": "population", "sourceId": "world_bank",
                "fetchedAt": "2026-11-02T00:00:00Z",
                "geography": "Kenya national",
                "series": [{"year": 2024, "value": 50000000}]
            }})
        with patch.dict(os.environ, {
            "KENYA_DATA_GATEWAY_URL": audience,
            "KENYA_DATA_GATEWAY_AUDIENCE": audience
        }):
            response = asyncio.run(fetch_public_context(
                "population", from_year=2020, to_year=2024,
                transport=httpx.MockTransport(transport)))
        self.assertTrue(observed["token"])
        self.assertTrue(observed["payload"])
        self.assertEqual(response["data"]["sourceId"], "world_bank")
        self.assertEqual(response["usage"], "context_only")

    def test_deny_unauthorized_service_identity(self):
        def transport(request: httpx.Request) -> httpx.Response:
            if request.url.host == "metadata.google.internal":
                return httpx.Response(200, text="a"*256)
            return httpx.Response(403, json={"error": "dataset_not_authorized"})
        with patch.dict(os.environ, {
            "KENYA_DATA_GATEWAY_URL": "https://example.run.app/kenyaOpenDataFederation",
            "KENYA_DATA_GATEWAY_AUDIENCE": "https://example.run.app"
        }):
            with self.assertRaises(HubPermissionDenied):
                asyncio.run(fetch_public_context("county_boundaries",
                    transport=httpx.MockTransport(transport)))


if __name__ == "__main__":
    unittest.main()
