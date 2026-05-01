from __future__ import annotations

import json

import httpx
import respx

from chebi_mcp.client import CacheConfig, ChebiClient, ResponseCache


def client(tmp_path):
    return ChebiClient(
        base_url="https://example.test/chebi/backend/api/public",
        cache=ResponseCache(CacheConfig(path=tmp_path / "cache.sqlite", ttl_seconds=60)),
    )


@respx.mock
def test_es_search_uses_expected_endpoint(tmp_path):
    route = respx.get("https://example.test/chebi/backend/api/public/es_search/").mock(
        return_value=httpx.Response(200, json={"total": 1, "results": []})
    )

    result = client(tmp_path).es_search("lactic acid", size=5)

    assert result["total"] == 1
    assert route.calls.last.request.url.params["term"] == "lactic acid"
    assert route.calls.last.request.url.params["size"] == "5"


@respx.mock
def test_get_compounds_joins_ids(tmp_path):
    route = respx.get("https://example.test/chebi/backend/api/public/compounds/").mock(
        return_value=httpx.Response(200, json={"CHEBI:1": {"name": "one"}})
    )

    result = client(tmp_path).get_compounds(["CHEBI:1", "CHEBI:2"])

    assert result["CHEBI:1"]["name"] == "one"
    assert route.calls.last.request.url.params["chebi_ids"] == "CHEBI:1,CHEBI:2"


@respx.mock
def test_cache_reuses_get_response(tmp_path):
    route = respx.get("https://example.test/chebi/backend/api/public/compound/CHEBI:28358/").mock(
        return_value=httpx.Response(200, json={"chebi_accession": "CHEBI:28358"})
    )
    c = client(tmp_path)

    assert c.get_compound("CHEBI:28358")["chebi_accession"] == "CHEBI:28358"
    assert c.get_compound("CHEBI:28358")["chebi_accession"] == "CHEBI:28358"

    assert route.call_count == 1


@respx.mock
def test_advanced_search_posts_specification(tmp_path):
    route = respx.post("https://example.test/chebi/backend/api/public/advanced_search/").mock(
        return_value=httpx.Response(200, json={"total": 22})
    )
    spec = {"ontology_specification": {"and_specification": [{"relation": "has_role", "entity": "CHEBI:64049"}]}}

    result = client(tmp_path).advanced_search(spec, size=10)

    assert result["total"] == 22
    assert json.loads(route.calls.last.request.content.decode()) == spec
    assert route.calls.last.request.url.params["size"] == "10"

