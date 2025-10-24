# Changelog

All notable changes to the Python implementation of Salesforce MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.15.0] - 2025-10-24

### Added
- Initial Python implementation of Salesforce MCP server
- Core tools: `sf-get-username`
- Org tools: `sf-list-all-orgs`
- Data tools: `sf-query-org`
- User tools: `sf-assign-permission-set`
- Metadata tools: `sf-deploy-metadata`, `sf-retrieve-metadata`
- Testing tools: `sf-test-apex`, `sf-test-agents`
- Security-first authentication using Salesforce CLI credentials
- Granular org access control
- Modular toolset architecture
- Full type hints and Pydantic validation
- Async/await support throughout
- Comprehensive documentation

### Features
- Compatible with all MCP clients (VS Code, Claude Desktop, Cursor, etc.)
- No secrets in configuration
- Support for both `.sfdx` and `.sf` credential directories
- Default org resolution (target-org and target-dev-hub)
- Flexible org allowlisting (specific orgs, defaults, or all)
- Configurable toolsets for reduced context size

### Technical
- Built with official MCP Python SDK (mcp>=1.3.0)
- Uses simple-salesforce for Salesforce API integration
- Click-based CLI with rich help text
- Structured logging with Python logging module
- Comprehensive test suite with pytest
