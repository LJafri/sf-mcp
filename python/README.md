# Salesforce MCP Server (Python)

Python implementation of the Model Context Protocol (MCP) server for Salesforce, following 2025 advancements in MCP architecture.

## Overview

This is a modern Python implementation of the Salesforce DX MCP Server, providing seamless integration between large language models (LLMs) and Salesforce orgs through the Model Context Protocol.

### Key Features

- **Security-First Design**: Uses stored Salesforce CLI credentials without exposing secrets
- **Direct API Integration**: Uses `simple-salesforce` for direct API access
- **Granular Access Control**: Org allowlisting for enhanced security
- **Modular Toolsets**: Enable only the tools you need
- **Async Support**: Built with modern async/await patterns
- **Type Safety**: Full type hints and Pydantic validation

## Installation

### Prerequisites

- Python 3.10 or higher
- Salesforce CLI (`sf`) installed and authenticated
- At least one authorized Salesforce org

### Install from Source

```bash
cd python
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install salesforce-mcp
```

## Quick Start

### 1. Authenticate with Salesforce

First, authenticate with your Salesforce org using the Salesforce CLI:

```bash
sf org login web --alias my-org
```

### 2. Configure MCP Client

#### VS Code

Create or edit `.vscode/mcp.json`:

```json
{
  "servers": {
    "salesforce": {
      "type": "stdio",
      "command": "sf-mcp-server",
      "args": ["--orgs", "DEFAULT_TARGET_ORG", "--toolsets", "all"]
    }
  }
}
```

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "salesforce": {
      "command": "sf-mcp-server",
      "args": ["--orgs", "DEFAULT_TARGET_ORG", "--toolsets", "all"]
    }
  }
}
```

#### Cursor

Edit Cursor's `mcp.json`:

```json
{
  "mcpServers": {
    "salesforce": {
      "command": "sf-mcp-server",
      "args": ["--orgs", "DEFAULT_TARGET_ORG", "--toolsets", "all"]
    }
  }
}
```

### 3. Start Using

Once configured, you can use natural language to interact with Salesforce:

- "List all my Salesforce orgs"
- "Show me all accounts in my org"
- "Deploy my project to the default org"
- "Run Apex tests"

## Configuration

### Org Access Control

The `--orgs` parameter (required) controls which orgs the MCP server can access:

- `DEFAULT_TARGET_ORG` - Allow access to your default org
- `DEFAULT_TARGET_DEV_HUB` - Allow access to your default Dev Hub
- `ALLOW_ALL_ORGS` - Allow access to all authenticated orgs (⚠️ use with caution)
- `username@example.com` - Allow access to specific org by username
- `my-alias` - Allow access to specific org by alias

**Examples:**

```bash
# Default org only
sf-mcp-server --orgs DEFAULT_TARGET_ORG

# Multiple orgs
sf-mcp-server --orgs user@example.com,my-dev-hub,another-org

# Dev Hub and default org
sf-mcp-server --orgs DEFAULT_TARGET_ORG,DEFAULT_TARGET_DEV_HUB
```

### Toolsets

The `--toolsets` parameter (optional, defaults to `all`) controls which tool categories are enabled:

- `all` - Enable all tools (default)
- `orgs` - Org management tools (list orgs, etc.)
- `data` - Data query tools (SOQL queries)
- `users` - User management tools (assign permission sets)
- `metadata` - Metadata deploy/retrieve tools
- `testing` - Testing tools (Apex tests, agent tests)

**Examples:**

```bash
# Enable all toolsets (default)
sf-mcp-server --orgs DEFAULT_TARGET_ORG --toolsets all

# Enable only data and org tools
sf-mcp-server --orgs DEFAULT_TARGET_ORG --toolsets data,orgs

# Enable metadata and testing
sf-mcp-server --orgs my-org --toolsets metadata,testing
```

## Available Tools

### Core Tools (Always Enabled)

- `sf-get-username` - Resolve org username from alias or defaults

### Org Tools (`orgs` toolset)

- `sf-list-all-orgs` - List all configured and allowed Salesforce orgs

### Data Tools (`data` toolset)

- `sf-query-org` - Execute SOQL queries against Salesforce orgs

### User Tools (`users` toolset)

- `sf-assign-permission-set` - Assign permission sets to users

### Metadata Tools (`metadata` toolset)

- `sf-deploy-metadata` - Deploy metadata from project to org
- `sf-retrieve-metadata` - Retrieve metadata from org to project

### Testing Tools (`testing` toolset)

- `sf-test-apex` - Run Apex tests
- `sf-test-agents` - Run Agentforce agent tests

## Development

### Setup Development Environment

```bash
cd python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

### Code Quality

```bash
# Format code
black salesforce_mcp

# Lint code
ruff check salesforce_mcp

# Type check
mypy salesforce_mcp
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=salesforce_mcp
```

## Architecture

### 2025 MCP Advancements

This implementation follows the latest 2025 Model Context Protocol advancements:

1. **Security-First Design**
   - No secrets in configuration
   - Uses encrypted Salesforce CLI credentials
   - Granular org-level access control

2. **Modern Python Patterns**
   - Async/await throughout
   - Type hints and Pydantic validation
   - Structured logging

3. **Modular Architecture**
   - Pluggable toolsets
   - Clean separation of concerns
   - Easy to extend with new tools

4. **MCP SDK Integration**
   - Official MCP Python SDK
   - Standard protocol implementation
   - Compatible with all MCP clients

### Project Structure

```
python/
├── salesforce_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── config.py          # Configuration management
│   ├── auth.py            # Salesforce authentication
│   └── tools/             # Tool implementations
│       ├── __init__.py
│       ├── core.py        # Core tools
│       ├── orgs.py        # Org management
│       ├── data.py        # Data queries
│       ├── users.py       # User management
│       ├── metadata.py    # Metadata operations
│       └── testing.py     # Testing tools
├── tests/                 # Test suite
├── pyproject.toml         # Project metadata
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Security Considerations

### Credential Storage

The server reads Salesforce credentials from:
- `~/.sfdx/org/*.json` (legacy SFDX format)
- `~/.sf/org/*.json` (modern SF CLI format)

These files are created by the Salesforce CLI and contain encrypted tokens.

### Access Control

Always use the principle of least privilege:
- Only allowlist orgs that the MCP server needs access to
- Avoid `ALLOW_ALL_ORGS` in production environments
- Regularly review authorized orgs

### Network Security

The server:
- Never exposes credentials in plain text
- Communicates with Salesforce APIs over HTTPS
- Uses standard OAuth/JWT authentication flows

## Troubleshooting

### "No Salesforce auth files found"

**Solution**: Authenticate with at least one org:
```bash
sf org login web --alias my-org
```

### "Org 'xyz' is not in the allowed orgs list"

**Solution**: Add the org to the `--orgs` parameter or use `ALLOW_ALL_ORGS`

### "Salesforce CLI (sf) not found"

**Solution**: Install the Salesforce CLI from https://developer.salesforce.com/tools/salesforcecli

### Connection Issues

If you encounter connection issues:
1. Verify org authentication: `sf org list`
2. Test connection: `sf org display --target-org my-org`
3. Re-authenticate if needed: `sf org login web`

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

Copyright 2025, Salesforce, Inc.

Licensed under the Apache License, Version 2.0 (the "License"). See [LICENSE.txt](../LICENSE.txt) for details.

## Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Salesforce CLI Documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/)
- [Salesforce DX Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/)
- [Main Project README](../README.md)
