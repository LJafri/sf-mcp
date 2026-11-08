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

"""Testing tools for Salesforce MCP server."""

import logging
import subprocess
from typing import Any, Dict, List

from mcp.types import Tool

from salesforce_mcp.auth import SalesforceAuth
from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


def register_testing_tools(config: ServerConfig, auth: SalesforceAuth) -> List[Tool]:
    """Register testing tools.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager

    Returns:
        List of testing tools
    """
    return [
        Tool(
            name="sf-test-apex",
            description="""Executes Apex tests in a Salesforce org.

Parameters:
- usernameOrAlias: Org username or alias (optional, uses default if not specified)
- testClasses: Comma-separated list of test class names (optional, runs all tests if not specified)
- wait: Minutes to wait for tests to complete (default: 10)
- codeCoverage: Include code coverage (default: true)

Returns test results including pass/fail status and code coverage.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Org username or alias (optional)",
                    },
                    "testClasses": {
                        "type": "string",
                        "description": "Comma-separated test class names (optional)",
                    },
                    "wait": {
                        "type": "integer",
                        "description": "Minutes to wait for tests",
                        "default": 10,
                    },
                    "codeCoverage": {
                        "type": "boolean",
                        "description": "Include code coverage",
                        "default": True,
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
            name="sf-test-agents",
            description="""Executes agent tests in a Salesforce org.

Parameters:
- usernameOrAlias: Org username or alias (optional, uses default if not specified)
- agentName: Name of the agent to test (optional)
- wait: Minutes to wait for tests to complete (default: 10)

Returns agent test results.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "usernameOrAlias": {
                        "type": "string",
                        "description": "Org username or alias (optional)",
                    },
                    "agentName": {
                        "type": "string",
                        "description": "Agent name to test (optional)",
                    },
                    "wait": {
                        "type": "integer",
                        "description": "Minutes to wait for tests",
                        "default": 10,
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


async def test_apex(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Execute Apex tests in a Salesforce org.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        Test results
    """
    try:
        username_or_alias = arguments.get("usernameOrAlias")
        test_classes = arguments.get("testClasses")
        wait_time = arguments.get("wait", 10)
        code_coverage = arguments.get("codeCoverage", True)
        directory = arguments.get("directory", ".")

        # Resolve username
        username = auth.resolve_org_username(username_or_alias)

        # Build sf command
        cmd = ["sf", "apex", "run", "test", "--target-org", username, "--wait", str(wait_time), "--json"]

        if code_coverage:
            cmd.append("--code-coverage")

        if test_classes:
            cmd.extend(["--tests", test_classes])

        # Execute tests
        result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=wait_time * 60 + 60)

        if result.returncode == 0:
            return f"Apex tests completed:\n\n{result.stdout}"
        else:
            return f"Apex tests failed:\n\n{result.stderr or result.stdout}"

    except subprocess.TimeoutExpired:
        return "Apex tests timed out."
    except FileNotFoundError:
        return "Error: Salesforce CLI (sf) not found. Please install it from https://developer.salesforce.com/tools/salesforcecli"
    except Exception as e:
        logger.error(f"Error running Apex tests: {e}")
        return f"Failed to run Apex tests: {str(e)}"


async def test_agents(config: ServerConfig, auth: SalesforceAuth, arguments: Dict[str, Any]) -> str:
    """Execute agent tests in a Salesforce org.

    Args:
        config: Server configuration
        auth: Salesforce authentication manager
        arguments: Tool arguments

    Returns:
        Test results
    """
    try:
        username_or_alias = arguments.get("usernameOrAlias")
        agent_name = arguments.get("agentName")
        wait_time = arguments.get("wait", 10)
        directory = arguments.get("directory", ".")

        # Resolve username
        username = auth.resolve_org_username(username_or_alias)

        # Build sf command
        cmd = ["sf", "agent", "test", "run", "--target-org", username, "--wait", str(wait_time), "--json"]

        if agent_name:
            cmd.extend(["--name", agent_name])

        # Execute tests
        result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=wait_time * 60 + 60)

        if result.returncode == 0:
            return f"Agent tests completed:\n\n{result.stdout}"
        else:
            return f"Agent tests failed:\n\n{result.stderr or result.stdout}"

    except subprocess.TimeoutExpired:
        return "Agent tests timed out."
    except FileNotFoundError:
        return "Error: Salesforce CLI (sf) not found. Please install it from https://developer.salesforce.com/tools/salesforcecli"
    except Exception as e:
        logger.error(f"Error running agent tests: {e}")
        return f"Failed to run agent tests: {str(e)}"
