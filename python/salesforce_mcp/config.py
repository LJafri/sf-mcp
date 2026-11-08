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

"""Configuration management for Salesforce MCP server."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ServerConfig:
    """Server configuration for Salesforce MCP.

    Attributes:
        version: Server version
        allowed_orgs: List of org usernames/aliases that are allowed
        toolsets: List of enabled toolsets (all, orgs, data, users, metadata, testing)
        debug: Enable debug logging
    """

    version: str
    allowed_orgs: List[str]
    toolsets: List[str] = field(default_factory=lambda: ["all"])
    debug: bool = False

    def is_org_allowed(self, username_or_alias: str) -> bool:
        """Check if an org is allowed based on configuration.

        Args:
            username_or_alias: Username or alias to check

        Returns:
            True if the org is allowed, False otherwise
        """
        # Check if all orgs are allowed
        if "ALLOW_ALL_ORGS" in self.allowed_orgs:
            return True

        # Check if specific org is in the list
        if username_or_alias in self.allowed_orgs:
            return True

        # Special handling for default orgs will be done in auth module
        return False

    def is_toolset_enabled(self, toolset: str) -> bool:
        """Check if a toolset is enabled.

        Args:
            toolset: Toolset name to check

        Returns:
            True if the toolset is enabled, False otherwise
        """
        return "all" in self.toolsets or toolset in self.toolsets
