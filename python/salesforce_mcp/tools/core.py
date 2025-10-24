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

"""Core tools for Salesforce MCP server."""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


def register_core_tools(config: ServerConfig, auth: SalesforceAuth) -> List[Tool]:
    """Register core tools that are always available.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager

    Returns:
        List of core tools
    """
    return [
        Tool(
            name="sf-get-username",
            description="""Determines the appropriate username or alias for Salesforce operations.

This tool helps resolve which org to use based on user input or defaults.
It handles both default orgs and Dev Hubs.

Use this tool when you need to determine which org to operate on before calling other tools.

Parameters:
- usernameOrAlias: (optional) Username, alias, or special value like DEFAULT_TARGET_ORG
- isDevHub: (optional) Whether to get Dev Hub org instead of regular org (default: false)

Returns the resolved username to use with other tools.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Username, alias, or DEFAULT_TARGET_ORG/DEFAULT_TARGET_DEV_HUB",
                    },
                    "isDevHub": {
                        "type": "boolean",
                        "description": "Whether to get the default Dev Hub org",
                        "default": False,
                    },
                },
            },
        ),
    ]


async def get_username(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Get and resolve a Salesforce org username.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        JSON string with resolved username
    """
    try:
        username_or_alias = arguments.get("usernameOrAlias")
        is_dev_hub = arguments.get("isDevHub", False)

        # If no username provided, try to get default
        if not username_or_alias:
            username_or_alias = "DEFAULT_TARGET_DEV_HUB" if is_dev_hub else "DEFAULT_TARGET_ORG"

        # Resolve the username
        resolved_username = auth.resolve_org_username(username_or_alias)

        return f"Resolved org username: {resolved_username}"

    except Exception as e:
        logger.error(f"Error getting username: {e}")
        return f"Error: {str(e)}"
