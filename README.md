# chem-development

Open-source chemistry product-development tooling for AI assistants.

- `chebi-mcp`: an MCP server for the public ChEBI chemical reference API, with persistent caching and typed tools for search, compound lookup, ontology, structure search, and structure calculations.
- `chem-skills`: Codex skills for chemistry-informed product-development collaboration, using `chebi-mcp` as the reference layer.

## Add `chebi-mcp` To Agent CLIs

The MCP server runs over stdio through `uv`. From a local clone:

```bash
git clone https://github.com/CarsonBurke/chem-development.git
cd chem-development
```

### Codex CLI

```bash
codex mcp add chebi -- /usr/bin/uv --directory chebi-mcp run chebi-mcp
codex mcp get chebi
```

Codex Desktop uses the same Codex MCP configuration as the CLI. If you use Codex Desktop, prefer registering the server with an absolute path so the desktop app can launch it regardless of its working directory:

```bash
codex mcp add chebi -- /usr/bin/uv --directory /absolute/path/to/chem-development/chebi-mcp run chebi-mcp
```

### Claude Code CLI

```bash
claude mcp add chebi -- /usr/bin/uv --directory chebi-mcp run chebi-mcp
claude mcp get chebi
```

### Claude Desktop

Claude Desktop reads MCP servers from `claude_desktop_config.json`. Add a `mcpServers` entry using an absolute path:

```json
{
  "mcpServers": {
    "chebi": {
      "command": "/usr/bin/uv",
      "args": [
        "--directory",
        "/absolute/path/to/chem-development/chebi-mcp",
        "run",
        "chebi-mcp"
      ]
    }
  }
}
```

Common config locations:

- Linux: `~/.config/Claude/claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Restart Claude Desktop after editing the config.

### Gemini CLI

Project-scoped config:

```bash
gemini mcp add chebi /usr/bin/uv --directory chebi-mcp run chebi-mcp
gemini mcp list
```

### Smoke Test

You can verify the MCP server itself without an agent client:

```bash
uv --directory chebi-mcp run python - <<'PY'
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
