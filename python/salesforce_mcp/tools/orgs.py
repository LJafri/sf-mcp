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

"""Org management tools for Salesforce MCP server."""

import json
import logging
from typing import Any, Dict, List

from mcp.types import Tool

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


def register_org_tools(config: ServerConfig, auth: SalesforceAuth) -> List[Tool]:
    """Register org management tools.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager

    Returns:
        List of org tools
    """
    return [
        Tool(
            name="sf-list-all-orgs",
            description="""Lists all configured Salesforce orgs.

AGENT INSTRUCTIONS:
DO NOT use this tool to try to determine which org a user wants, use sf-get-username instead.
Only use it if the user explicitly asks for a list of orgs.

Example usage:
- Can you list all Salesforce orgs for me
- List all Salesforce orgs
- List all orgs
- Show me my orgs

Returns a JSON list of all allowed orgs with their details.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Working directory (optional)",
                        "default": ".",
                    }
                },
            },
        ),
    ]


async def list_all_orgs(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """List all allowed Salesforce orgs.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        JSON string with list of orgs
    """
    try:
        orgs = auth.get_all_allowed_orgs()
        return f"List of configured Salesforce orgs:\n\n{json.dumps(orgs, indent=2)}"
    except Exception as e:
        logger.error(f"Error listing orgs: {e}")
        return f"Failed to list orgs: {str(e)}"
