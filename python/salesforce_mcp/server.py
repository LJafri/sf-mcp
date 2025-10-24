#!/usr/bin/env python3
# Copyright 2025, Salesforce, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main MCP server implementation for Salesforce."""

import asyncio
import json
import logging
import sys
from typing import Any, Optional

import click
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
)

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig
from salesforce_mcp.tools import (
    register_core_tools,
    register_data_tools,
    register_metadata_tools,
    register_org_tools,
    register_testing_tools,
    register_user_tools,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class SalesforceMCPServer:
    """Salesforce MCP Server implementation with enhanced features."""

    def __init__(self, config: ServerConfig):
        """Initialize the Salesforce MCP server.

        Args:
            config: Server configuration including allowed orgs and toolsets
        """
        self.config = config
        self.server = Server("sf-mcp-server")
        self.auth = SalesforceAuth(config)

        # Register handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools based on enabled toolsets."""
            tools: list[Tool] = []

            # Core tools (always enabled)
            tools.extend(register_core_tools(self.config, self.auth))

            # Conditional toolsets
            if "all" in self.config.toolsets or "orgs" in self.config.toolsets:
                tools.extend(register_org_tools(self.config, self.auth))

            if "all" in self.config.toolsets or "data" in self.config.toolsets:
                tools.extend(register_data_tools(self.config, self.auth))

            if "all" in self.config.toolsets or "users" in self.config.toolsets:
                tools.extend(register_user_tools(self.config, self.auth))

            if "all" in self.config.toolsets or "metadata" in self.config.toolsets:
                tools.extend(register_metadata_tools(self.config, self.auth))

            if "all" in self.config.toolsets or "testing" in self.config.toolsets:
                tools.extend(register_testing_tools(self.config, self.auth))

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute a tool with the given arguments.

            Args:
                name: Tool name to execute
                arguments: Tool arguments

            Returns:
                List of text content results
            """
            logger.info(f"Executing tool: {name}")

            try:
                # Route to appropriate tool handler
                if name == "sf-get-username":
                    from salesforce_mcp.tools.core import get_username

                    result = await get_username(self.config, self.auth, arguments)
                elif name == "sf-list-all-orgs":
                    from salesforce_mcp.tools.orgs import list_all_orgs

                    result = await list_all_orgs(self.config, self.auth, arguments)
                elif name == "sf-query-org":
                    from salesforce_mcp.tools.data import query_org

                    result = await query_org(self.config, self.auth, arguments)
                elif name == "sf-deploy-metadata":
                    from salesforce_mcp.tools.metadata import deploy_metadata

                    result = await deploy_metadata(self.config, self.auth, arguments)
                elif name == "sf-retrieve-metadata":
                    from salesforce_mcp.tools.metadata import retrieve_metadata

                    result = await retrieve_metadata(self.config, self.auth, arguments)
                elif name == "sf-assign-permission-set":
                    from salesforce_mcp.tools.users import assign_permission_set

                    result = await assign_permission_set(self.config, self.auth, arguments)
                elif name == "sf-test-apex":
                    from salesforce_mcp.tools.testing import test_apex

                    result = await test_apex(self.config, self.auth, arguments)
                elif name == "sf-test-agents":
                    from salesforce_mcp.tools.testing import test_agents

                    result = await test_agents(self.config, self.auth, arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=result)]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                error_msg = f"Error executing {name}: {str(e)}"
                return [TextContent(type="text", text=error_msg)]

    async def run(self) -> None:
        """Run the MCP server using stdio transport."""
        logger.info("Starting Salesforce MCP Server")
        logger.info(f"Version: {self.config.version}")
        logger.info(f"Allowed orgs: {', '.join(self.config.allowed_orgs)}")
        logger.info(f"Enabled toolsets: {', '.join(self.config.toolsets)}")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


@click.command()
@click.option(
    "--orgs",
    "-o",
    required=True,
    multiple=True,
    help="Org usernames/aliases to allow access to. Special values: DEFAULT_TARGET_ORG, DEFAULT_TARGET_DEV_HUB, ALLOW_ALL_ORGS",
)
@click.option(
    "--toolsets",
    "-t",
    multiple=True,
    default=["all"],
    type=click.Choice(["all", "orgs", "data", "users", "metadata", "testing"]),
    help="Toolsets to enable (default: all)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.version_option(version="0.15.0")
def main(orgs: tuple[str, ...], toolsets: tuple[str, ...], debug: bool) -> None:
    """Start the Salesforce MCP server.

    The Salesforce DX MCP Server is a specialized Model Context Protocol (MCP)
    implementation designed to facilitate seamless interaction between large
    language models (LLMs) and Salesforce orgs.

    Examples:

        # Start with default org access
        sf-mcp-server --orgs DEFAULT_TARGET_ORG

        # Multiple orgs with specific toolsets
        sf-mcp-server --orgs user@example.com,my-alias --toolsets data,metadata

        # Allow all orgs (use with caution!)
        sf-mcp-server --orgs ALLOW_ALL_ORGS
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate org inputs
    for org in orgs:
        if org == "ALLOW_ALL_ORGS":
            logger.warning("⚠️  ALLOW_ALL_ORGS is set. This allows access to all authenticated orgs. Use with caution.")

    # Create server configuration
    config = ServerConfig(
        version="0.15.0",
        allowed_orgs=list(orgs),
        toolsets=list(toolsets),
        debug=debug,
    )

    # Create and run server
    server = SalesforceMCPServer(config)

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
