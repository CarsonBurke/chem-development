# chebi-mcp

MCP server for the public ChEBI 2.0 API.

The server exposes the public ChEBI endpoints as typed MCP tools and adds a small persistent cache for normal assistant use. ChEBI remains the source of truth; this package is a thin access layer with predictable tool names.

## Run

```bash
uv run chebi-mcp
```

Useful environment variables:

- `CHEBI_BASE_URL`: defaults to `https://www.ebi.ac.uk/chebi/backend/api/public`
- `CHEBI_MCP_CACHE_PATH`: defaults to `~/.cache/chebi-mcp/cache.sqlite`
- `CHEBI_MCP_CACHE_TTL_SECONDS`: defaults to 2592000, or 30 days
- `CHEBI_MCP_DISABLE_CACHE`: set to `1` to disable persistent caching
- `CHEBI_MCP_TIMEOUT_SECONDS`: defaults to 10

## Tools

Core API coverage:

- `chebi_es_search`
- `chebi_get_compound`
- `chebi_get_compounds`
- `chebi_advanced_search`
- `chebi_sources_list`
- `chebi_ontology_parents`
- `chebi_ontology_children`
- `chebi_ontology_all_children_in_path`
- `chebi_structure_search`
- `chebi_compound_structure_svg`
- `chebi_structure_svg`
- `chebi_molfile`
- `chebi_avg_mass`
- `chebi_avg_mass_from_formula`
- `chebi_monoisotopic_mass`
- `chebi_monoisotopic_mass_from_formula`
- `chebi_mol_formula`
- `chebi_net_charge`
- `chebi_depict_indigo_png`

Convenience tools:

- `chebi_chemical_card`
- `chebi_role_alternatives`

## Notes

ChEBI is strong for identity, synonyms, formula/mass, ontology classes, roles, and cross references. It is not a complete product-development source for pKa, solubility, GHS/SDS, regulatory limits, or formulation compatibility.

