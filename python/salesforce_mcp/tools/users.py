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

"""User management tools for Salesforce MCP server."""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


def register_user_tools(config: ServerConfig, auth: SalesforceAuth) -> List[Tool]:
    """Register user management tools.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager

    Returns:
        List of user tools
    """
    return [
        Tool(
            name="sf-assign-permission-set",
            description="""Assigns a permission set to a user in a Salesforce org.

Parameters:
- permissionSetName: Name of the permission set to assign (required)
- usernameOrAlias: Org username or alias (optional, uses default if not specified)
- targetUsername: Username of the user to assign permission set to (optional, assigns to current user if not specified)

Returns confirmation of permission set assignment.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "permissionSetName": {
                        "type": "string",
                        "description": "Name of the permission set",
                    },
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Org username or alias (optional)",
                    },
                    "targetUsername": {
                        "type": "string",
                        "description": "Target user to assign permission set to (optional)",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Working directory (optional)",
                        "default": ".",
                    },
                },
                "required": ["permissionSetName"],
            },
        ),
    ]


async def assign_permission_set(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Assign a permission set to a user.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        Result message
    """
    try:
        permission_set_name = arguments.get("permissionSetName")
        if not permission_set_name:
            return "Error: permissionSetName parameter is required"

        username_or_alias = arguments.get("usernameOrAlias")
        target_username = arguments.get("targetUsername")

        # Get connection
        sf = auth.get_connection(username_or_alias)

        # Get PermissionSet Id
        ps_query = f"SELECT Id FROM PermissionSet WHERE Name = '{permission_set_name}' LIMIT 1"
        ps_result = sf.query(ps_query)

        if ps_result["totalSize"] == 0:
            return f"Error: Permission set '{permission_set_name}' not found"

        permission_set_id = ps_result["records"][0]["Id"]

        # Get User Id
        if target_username:
            user_query = f"SELECT Id FROM User WHERE Username = '{target_username}' LIMIT 1"
        else:
            # Get current user
            user_query = "SELECT Id FROM User WHERE Username = UserInfo.getUserName() LIMIT 1"

        user_result = sf.query(user_query)

        if user_result["totalSize"] == 0:
            return f"Error: User '{target_username or 'current'}' not found"

        user_id = user_result["records"][0]["Id"]

        # Check if assignment already exists
        check_query = f"SELECT Id FROM PermissionSetAssignment WHERE PermissionSetId = '{permission_set_id}' AND AssigneeId = '{user_id}'"
        existing = sf.query(check_query)

        if existing["totalSize"] > 0:
            return f"Permission set '{permission_set_name}' is already assigned to the user"

        # Create assignment
        assignment = sf.PermissionSetAssignment.create(
            {
                "PermissionSetId": permission_set_id,
                "AssigneeId": user_id,
            }
        )

        if assignment.get("success"):
            return f"Successfully assigned permission set '{permission_set_name}' to user"
        else:
            return f"Failed to assign permission set: {assignment.get('errors', 'Unknown error')}"

    except Exception as e:
        logger.error(f"Error assigning permission set: {e}")
        return f"Failed to assign permission set: {str(e)}"
