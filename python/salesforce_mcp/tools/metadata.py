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

"""Metadata management tools for Salesforce MCP server."""

import logging
import subprocess
from typing import Any, Dict, List

from mcp.types import Tool

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


def register_metadata_tools(config: ServerConfig, auth: SalesforceAuth) -> List[Tool]:
    """Register metadata management tools.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager

    Returns:
        List of metadata tools
    """
    return [
        Tool(
            name="sf-deploy-metadata",
            description="""Deploys metadata from your SFDX project to a Salesforce org.

Parameters:
- usernameOrAlias: Org username or alias (optional, uses default if not specified)
- sourcePath: Path to source to deploy (optional, deploys entire project if not specified)
- testLevel: Test level for deployment (NoTestRun, RunSpecifiedTests, RunLocalTests, RunAllTestsInOrg)
- wait: Minutes to wait for deployment to complete (default: 33)

Returns deployment status and results.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Org username or alias (optional)",
                    },
                    "sourcePath": {
                        "type": "string",
                        "description": "Path to source directory or file (optional)",
                    },
                    "testLevel": {
                        "type": "string",
                        "description": "Test level for deployment",
                        "enum": ["NoTestRun", "RunSpecifiedTests", "RunLocalTests", "RunAllTestsInOrg"],
                        "default": "NoTestRun",
                    },
                    "wait": {
                        "type": "integer",
                        "description": "Minutes to wait for deployment",
                        "default": 33,
                    },
                    "directory": {
                        "type": "string",
                        "description": "Project directory (optional)",
                        "default": ".",
                    },
                },
            },
        ),
        Tool(
            name="sf-retrieve-metadata",
            description="""Retrieves metadata from a Salesforce org to your SFDX project.

Parameters:
- usernameOrAlias: Org username or alias (optional, uses default if not specified)
- sourcePath: Path where to retrieve metadata (optional)
- manifestPath: Path to package.xml manifest file (optional)

Returns retrieval status and results.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Org username or alias (optional)",
                    },
                    "sourcePath": {
                        "type": "string",
                        "description": "Path to retrieve metadata to (optional)",
                    },
                    "manifestPath": {
                        "type": "string",
                        "description": "Path to package.xml manifest (optional)",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Project directory (optional)",
                        "default": ".",
                    },
                },
            },
        ),
    ]


async def deploy_metadata(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Deploy metadata to a Salesforce org.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        Deployment result message
    """
    try:
        username_or_alias = arguments.get("usernameOrAlias")
        source_path = arguments.get("sourcePath", "force-app")
        test_level = arguments.get("testLevel", "NoTestRun")
        wait_time = arguments.get("wait", 33)
        directory = arguments.get("directory", ".")

        # Resolve username
        username = auth.resolve_org_username(username_or_alias)

        # Build sf command
        cmd = [
            "sf",
            "project",
            "deploy",
            "start",
            "--target-org",
            username,
            "--source-dir",
            source_path,
            "--test-level",
            test_level,
            "--wait",
            str(wait_time),
            "--json",
        ]

        # Execute deployment
        result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=wait_time * 60 + 60)

        if result.returncode == 0:
            return f"Deployment successful:\n\n{result.stdout}"
        else:
            return f"Deployment failed:\n\n{result.stderr or result.stdout}"

    except subprocess.TimeoutExpired:
        return "Deployment timed out. Check org for deployment status."
    except FileNotFoundError:
        return "Error: Salesforce CLI (sf) not found. Please install it from https://developer.salesforce.com/tools/salesforcecli"
    except Exception as e:
        logger.error(f"Error deploying metadata: {e}")
        return f"Failed to deploy metadata: {str(e)}"


async def retrieve_metadata(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Retrieve metadata from a Salesforce org.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        Retrieval result message
    """
    try:
        username_or_alias = arguments.get("usernameOrAlias")
        source_path = arguments.get("sourcePath")
        manifest_path = arguments.get("manifestPath")
        directory = arguments.get("directory", ".")

        # Resolve username
        username = auth.resolve_org_username(username_or_alias)

        # Build sf command
        cmd = ["sf", "project", "retrieve", "start", "--target-org", username, "--json"]

        if source_path:
            cmd.extend(["--source-dir", source_path])
        elif manifest_path:
            cmd.extend(["--manifest", manifest_path])

        # Execute retrieval
        result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            return f"Retrieval successful:\n\n{result.stdout}"
        else:
            return f"Retrieval failed:\n\n{result.stderr or result.stdout}"

    except subprocess.TimeoutExpired:
        return "Retrieval timed out."
    except FileNotFoundError:
        return "Error: Salesforce CLI (sf) not found. Please install it from https://developer.salesforce.com/tools/salesforcecli"
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        return f"Failed to retrieve metadata: {str(e)}"
