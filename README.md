# chem-development

Open-source chemistry product-development tooling for AI assistants.

This repository currently contains two components:

- `chebi-mcp`: an MCP server for the public ChEBI chemical reference API, with persistent caching and typed tools for search, compound lookup, ontology, structure search, and structure calculations.
- `chem-skills`: Codex skills for chemistry-informed product-development collaboration, using `chebi-mcp` as the reference layer.

## Repository Layout

```text
chem-development/
├── chebi-mcp/
└── chem-skills/
```

## Status

Early scaffold. The intended direction is a practical assistant foundation for chemical identity, role-based alternatives, product-development tradeoff discussion, and source-grounded decision support.

## Add `chebi-mcp` To Agent CLIs

The MCP server runs over stdio through `uv`. From a local clone:

```bash
git clone https://github.com/CarsonBurke/chem-development.git
cd chem-development
```

### Codex CLI

```bash
codex mcp add chebi -- /usr/bin/uv --directory "$(pwd)/chebi-mcp" run chebi-mcp
codex mcp get chebi
```

### Claude Code CLI

Local/project-scoped config:

```bash
claude mcp add --scope local chebi -- /usr/bin/uv --directory "$(pwd)/chebi-mcp" run chebi-mcp
claude mcp get chebi
```

User-scoped config:

```bash
claude mcp add --scope user chebi -- /usr/bin/uv --directory "$(pwd)/chebi-mcp" run chebi-mcp
```

### Gemini CLI

Project-scoped config:

```bash
gemini mcp add --scope project chebi /usr/bin/uv --directory "$(pwd)/chebi-mcp" run chebi-mcp
gemini mcp list
```

User-scoped config:

```bash
gemini mcp add --scope user chebi /usr/bin/uv --directory "$(pwd)/chebi-mcp" run chebi-mcp
```

### Smoke Test

You can verify the MCP server itself without an agent client:

```bash
uv --directory "$(pwd)/chebi-mcp" run python - <<'PY'
from chebi_mcp.client import ChebiClient

card = ChebiClient().chemical_card("lactic acid")
print(card["chebi_accession"], card["formula"], card["mass"])
PY
```

Expected output starts with:

```text
CHEBI:28358 C3H6O3 90.078
```

## License

MIT. ChEBI data and API responses remain subject to EMBL-EBI/ChEBI terms and source database licensing.
