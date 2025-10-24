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

"""Data management tools for Salesforce MCP server."""

import json
import logging
from typing import Any, Dict, List

from mcp.types import Tool

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


def register_data_tools(config: ServerConfig, auth: SalesforceAuth) -> List[Tool]:
    """Register data management tools.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager

    Returns:
        List of data tools
    """
    return [
        Tool(
            name="sf-query-org",
            description="""Run a SOQL query against a Salesforce org.

Execute SOQL (Salesforce Object Query Language) queries to retrieve data from Salesforce objects.

Parameters:
- query: SOQL query to run (required)
- usernameOrAlias: username or alias for the Salesforce org (optional, uses default if not specified)
- useToolingApi: Use Tooling API instead of standard API (default: false)

Examples:
- SELECT Id, Name FROM Account LIMIT 10
- SELECT Id, Subject FROM Case WHERE Status = 'Open'
- SELECT Id, Email FROM User WHERE IsActive = true

Returns query results in JSON format.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SOQL query to execute",
                    },
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Org username or alias (optional)",
                    },
                    "useToolingApi": {
                        "type": "boolean",
                        "description": "Use Tooling API instead of standard API",
                        "default": False,
                    },
                    "directory": {
                        "type": "string",
                        "description": "Working directory (optional)",
                        "default": ".",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


async def query_org(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Execute a SOQL query against a Salesforce org.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments containing query and optional org

    Returns:
        JSON string with query results
    """
    try:
        query = arguments.get("query")
        if not query:
            return "Error: query parameter is required"

        username_or_alias = arguments.get("usernameOrAlias")
        use_tooling_api = arguments.get("useToolingApi", False)

        # Get connection
        sf = auth.get_connection(username_or_alias)

        # Execute query
        if use_tooling_api:
            # Use Tooling API
            result = sf.toolingexecute(f"query/?q={query}")
        else:
            # Use standard API
            result = sf.query(query)

        return f"SOQL query results:\n\n{json.dumps(result, indent=2, default=str)}"

    except Exception as e:
        logger.error(f"Error executing query: {e}")
        error_message = str(e)

        # Provide helpful hints
        if "is not supported" in error_message:
            if arguments.get("useToolingApi"):
                error_message += "\nTry not using the Tooling API for this query."
            else:
                error_message += "\nTry using the Tooling API for this query."

        return f"Failed to query org: {error_message}"
