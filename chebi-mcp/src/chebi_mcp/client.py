from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


DEFAULT_BASE_URL = "https://www.ebi.ac.uk/chebi/backend/api/public"
DEFAULT_TTL_SECONDS = 30 * 24 * 60 * 60


class ChebiError(RuntimeError):
    """Raised when ChEBI returns an unsuccessful response."""


@dataclass(frozen=True)
class CacheConfig:
    path: Path
    ttl_seconds: int
    disabled: bool = False

    @classmethod
    def from_env(cls) -> "CacheConfig":
        path = Path(
            os.getenv(
                "CHEBI_MCP_CACHE_PATH",
                str(Path.home() / ".cache" / "chebi-mcp" / "cache.sqlite"),
            )
        ).expanduser()
        ttl = int(os.getenv("CHEBI_MCP_CACHE_TTL_SECONDS", str(DEFAULT_TTL_SECONDS)))
        disabled = os.getenv("CHEBI_MCP_DISABLE_CACHE", "").lower() in {"1", "true", "yes"}
        return cls(path=path, ttl_seconds=ttl, disabled=disabled)


class ResponseCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self._conn: sqlite3.Connection | None = None

    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self.config.path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.config.path)
            self._conn.execute(
                """
                create table if not exists response_cache (
                    key text primary key,
                    status_code integer not null,
                    content_type text not null,
                    body blob not null,
                    created_at real not null
                )
                """
            )
        return self._conn

    def get(self, key: str) -> tuple[int, str, bytes] | None:
        if self.config.disabled:
            return None
        row = self._connect().execute(
            "select status_code, content_type, body, created_at from response_cache where key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        status_code, content_type, body, created_at = row
        if time.time() - float(created_at) > self.config.ttl_seconds:
            return None
        return int(status_code), str(content_type), bytes(body)

    def set(self, key: str, status_code: int, content_type: str, body: bytes) -> None:
        if self.config.disabled:
            return
        self._connect().execute(
            """
            insert or replace into response_cache
            (key, status_code, content_type, body, created_at)
            values (?, ?, ?, ?, ?)
            """,
            (key, status_code, content_type, body, time.time()),
        )
        self._connect().commit()


class ChebiClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("CHEBI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        timeout = timeout_seconds or float(os.getenv("CHEBI_MCP_TIMEOUT_SECONDS", "10"))
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Accept-Encoding": "gzip", "User-Agent": "chebi-mcp/0.1.0"},
            follow_redirects=True,
        )
        self.cache = cache or ResponseCache(CacheConfig.from_env())

    def close(self) -> None:
        self._client.close()

    def _cache_key(self, method: str, path: str, params: dict[str, Any] | None, body: Any) -> str:
        payload = json.dumps(
            {"method": method, "path": path, "params": params or {}, "body": body},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        text_body: str | None = None,
        accept: str | None = None,
    ) -> tuple[str, bytes]:
        body_for_key = json_body if text_body is None else text_body
        cache_key = self._cache_key(method, path, params, body_for_key)
        cached = self.cache.get(cache_key)
        if cached is not None:
            status_code, content_type, body = cached
            if status_code >= 400:
                raise ChebiError(body.decode("utf-8", errors="replace"))
            return content_type, body

        headers: dict[str, str] = {}
        if accept is not None:
            headers["Accept"] = accept
        if text_body is not None:
            headers["Content-Type"] = "text/plain;charset=UTF-8"
            response = self._client.request(method, path, params=params, content=text_body, headers=headers)
        else:
            response = self._client.request(method, path, params=params, json=json_body, headers=headers)

        content_type = response.headers.get("content-type", "")
        body = response.content
        self.cache.set(cache_key, response.status_code, content_type, body)
        if response.status_code >= 400:
            raise ChebiError(body.decode("utf-8", errors="replace"))
        return content_type, body

    def _json(self, method: str, path: str, **kwargs: Any) -> Any:
        _, body = self._request(method, path, accept="application/json", **kwargs)
        return json.loads(body.decode("utf-8"))

    def _text(self, method: str, path: str, **kwargs: Any) -> str:
        _, body = self._request(method, path, **kwargs)
        return body.decode("utf-8")

    def es_search(self, term: str, page: int = 1, size: int = 15) -> Any:
        return self._json("GET", "/es_search/", params={"term": term, "page": page, "size": size})

    def get_compound(
        self,
        chebi_id: str,
        only_ontology_parents: bool = False,
        only_ontology_children: bool = False,
    ) -> Any:
        return self._json(
            "GET",
            f"/compound/{chebi_id}/",
            params={
                "only_ontology_parents": only_ontology_parents,
                "only_ontology_children": only_ontology_children,
            },
        )

    def get_compounds(self, chebi_ids: list[str]) -> Any:
        return self._json("GET", "/compounds/", params={"chebi_ids": ",".join(chebi_ids)})

    def advanced_search(
        self,
        specification: dict[str, Any],
        *,
        three_star_only: bool = True,
        has_structure: bool | None = None,
        page: int = 1,
        size: int = 15,
        download: bool = False,
    ) -> Any:
        params: dict[str, Any] = {
            "three_star_only": three_star_only,
            "page": page,
            "size": size,
            "download": download,
        }
        if has_structure is not None:
            params["has_structure"] = has_structure
        return self._json("POST", "/advanced_search/", params=params, json_body=specification)

    def sources_list(self) -> Any:
        return self._json("GET", "/advanced_search/sources_list")

    def ontology_parents(self, chebi_id: str) -> Any:
        return self._json("GET", f"/ontology/parents/{chebi_id}/")

    def ontology_children(self, chebi_id: str) -> Any:
        return self._json("GET", f"/ontology/children/{chebi_id}/")

    def ontology_all_children_in_path(
        self,
        relation: str,
        entity: str,
        *,
        three_star_only: bool = True,
        has_structure: bool | None = None,
        page: int = 1,
        size: int = 15,
        download: bool = False,
    ) -> Any:
        params: dict[str, Any] = {
            "relation": relation,
            "entity": entity,
            "three_star_only": three_star_only,
            "page": page,
            "size": size,
            "download": download,
        }
        if has_structure is not None:
            params["has_structure"] = has_structure
        return self._json("GET", "/ontology/all_children_in_path/", params=params)

    def structure_search(
        self,
        smiles: str,
        search_type: str,
        *,
        similarity: float | None = None,
        three_star_only: bool = True,
        page: int = 1,
        size: int = 15,
        download: bool = False,
    ) -> Any:
        params: dict[str, Any] = {
            "smiles": smiles,
            "search_type": search_type,
            "three_star_only": three_star_only,
            "page": page,
            "size": size,
            "download": download,
        }
        if similarity is not None:
            params["similarity"] = similarity
        return self._json("GET", "/structure_search/", params=params)

    def compound_structure_svg(self, chebi_id: str) -> str:
        return self._text("GET", f"/compound/{chebi_id}/structure/", accept="image/svg+xml")

    def structure_svg(self, structure_id: int) -> str:
        return self._text("GET", f"/structure/{structure_id}/", accept="image/svg+xml")

    def molfile(self, compound_id: int) -> str:
        return self._text("GET", f"/molfile/{compound_id}/")

    def structure_calculation(self, endpoint: str, structure_or_formula: str) -> str:
        return self._text("POST", endpoint, text_body=structure_or_formula)

    def depict_indigo_png(self, structure: str, width: int = 300, height: int = 300, transbg: bool = False) -> dict[str, str]:
        _, body = self._request(
            "POST",
            "/structure-calculations/depict-indigo/",
            params={"width": width, "height": height, "transbg": transbg},
            text_body=structure,
            accept="image/png",
        )
        return {"format": "png", "base64": base64.b64encode(body).decode("ascii")}

    def chemical_card(self, query_or_chebi_id: str) -> dict[str, Any]:
        if query_or_chebi_id.upper().startswith("CHEBI:") or query_or_chebi_id.isdigit():
            chebi_id = query_or_chebi_id
            search = None
        else:
            search = self.es_search(query_or_chebi_id, size=1)
            results = search.get("results") or []
            if not results:
                return {"query": query_or_chebi_id, "found": False, "source": "ChEBI"}
            chebi_id = results[0]["_source"]["chebi_accession"]

        compound = self.get_compound(chebi_id)
        chemical_data = compound.get("chemical_data") or {}
        return {
            "query": query_or_chebi_id,
            "found": True,
            "source": "ChEBI",
            "chebi_accession": compound.get("chebi_accession"),
            "name": compound.get("name"),
            "ascii_name": compound.get("ascii_name"),
            "definition": compound.get("definition"),
            "stars": compound.get("stars"),
            "formula": chemical_data.get("formula"),
            "charge": chemical_data.get("charge"),
            "mass": chemical_data.get("mass"),
            "monoisotopic_mass": chemical_data.get("monoisotopic_mass"),
            "secondary_ids": compound.get("secondary_ids", []),
            "names": compound.get("names", {}),
            "database_accessions": compound.get("database_accessions", {}),
            "ontology_relations": compound.get("ontology_relations", {}),
            "roles_classification": compound.get("roles_classification", []),
            "search_match": search,
        }

