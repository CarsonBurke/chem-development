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

## License

MIT. ChEBI data and API responses remain subject to EMBL-EBI/ChEBI terms and source database licensing.

