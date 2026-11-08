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

"""Authentication and connection management for Salesforce."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from simple_salesforce import Salesforce

from salesforce_mcp.config import ServerConfig

logger = logging.getLogger(__name__)


class SalesforceAuth:
    """Manages Salesforce authentication and connections.

    This class provides secure access to Salesforce orgs using stored
    credentials from the Salesforce CLI without exposing secrets.
    """

    def __init__(self, config: ServerConfig):
        """Initialize Salesforce authentication manager.

        Args:
            config: Server configuration
        """
        self.config = config
        self._connections: Dict[str, Salesforce] = {}
        self._auth_info_cache: Optional[Dict[str, Any]] = None

    def get_sfdx_auth_dir(self) -> Path:
        """Get the SFDX authentication directory.

        Returns:
            Path to SFDX auth directory
        """
        # Check for custom SFDX_AUTH_DIR
        if auth_dir := os.getenv("SFDX_AUTH_DIR"):
            return Path(auth_dir)

        # Default location
        home = Path.home()
        return home / ".sfdx" / "org"

    def get_sf_state_dir(self) -> Path:
        """Get the SF CLI state directory.

        Returns:
            Path to SF state directory
        """
        if state_dir := os.getenv("SF_STATE_DIR"):
            return Path(state_dir)

        home = Path.home()
        return home / ".sf" / "org"

    def load_auth_files(self) -> Dict[str, Any]:
        """Load authentication files from SFDX/SF directories.

        Returns:
            Dictionary of org username to auth info

        Raises:
            FileNotFoundError: If no auth files are found
        """
        if self._auth_info_cache is not None:
            return self._auth_info_cache

        auth_info: Dict[str, Any] = {}

        # Try both .sfdx and .sf directories
        for auth_dir in [self.get_sfdx_auth_dir(), self.get_sf_state_dir()]:
            if not auth_dir.exists():
                continue

            for auth_file in auth_dir.glob("*.json"):
                try:
                    with open(auth_file, "r") as f:
                        data = json.load(f)
                        username = data.get("username")
                        if username:
                            auth_info[username] = data
                            # Also store by alias if present
                            if alias := data.get("alias"):
                                auth_info[alias] = data
                except Exception as e:
                    logger.warning(f"Failed to load auth file {auth_file}: {e}")

        if not auth_info:
            raise FileNotFoundError("No Salesforce auth files found. Please authenticate with 'sf org login web'")

        self._auth_info_cache = auth_info
        return auth_info

    def get_default_org(self, dev_hub: bool = False) -> Optional[str]:
        """Get the default org username.

        Args:
            dev_hub: If True, get default dev hub instead of default org

        Returns:
            Default org username or None if not set
        """
        # Check for project-level default
        project_config = Path.cwd() / ".sf" / "config.json"
        if project_config.exists():
            try:
                with open(project_config, "r") as f:
                    config = json.load(f)
                    key = "target-dev-hub" if dev_hub else "target-org"
                    if org := config.get(key):
                        return org
            except Exception as e:
                logger.warning(f"Failed to load project config: {e}")

        # Check for global default
        global_config = Path.home() / ".sf" / "config.json"
        if global_config.exists():
            try:
                with open(global_config, "r") as f:
                    config = json.load(f)
                    key = "target-dev-hub" if dev_hub else "target-org"
                    if org := config.get(key):
                        return org
            except Exception as e:
                logger.warning(f"Failed to load global config: {e}")

        return None

    def resolve_org_username(self, username_or_alias: Optional[str] = None) -> str:
        """Resolve an org username from alias or default.

        Args:
            username_or_alias: Username, alias, or special value (DEFAULT_TARGET_ORG, etc.)

        Returns:
            Resolved username

        Raises:
            ValueError: If org cannot be resolved or is not allowed
        """
        # Handle special values
        if username_or_alias == "DEFAULT_TARGET_ORG":
            default_org = self.get_default_org(dev_hub=False)
            if not default_org:
                raise ValueError("No default target org is set")
            username_or_alias = default_org
        elif username_or_alias == "DEFAULT_TARGET_DEV_HUB":
            default_org = self.get_default_org(dev_hub=True)
            if not default_org:
                raise ValueError("No default dev hub is set")
            username_or_alias = default_org
        elif not username_or_alias:
            # Try to get default org
            default_org = self.get_default_org(dev_hub=False)
            if not default_org:
                raise ValueError("No org specified and no default org is set")
            username_or_alias = default_org

        # Check if org is allowed
        if not self.config.is_org_allowed(username_or_alias):
            raise ValueError(f"Org '{username_or_alias}' is not in the allowed orgs list")

        # Load auth files and resolve alias
        auth_info = self.load_auth_files()
        if username_or_alias in auth_info:
            return auth_info[username_or_alias].get("username", username_or_alias)

        raise ValueError(f"No auth info found for org: {username_or_alias}")

    def get_connection(self, username_or_alias: Optional[str] = None) -> Salesforce:
        """Get a Salesforce connection for the specified org.

        Args:
            username_or_alias: Username, alias, or special value

        Returns:
            Salesforce connection object

        Raises:
            ValueError: If org cannot be resolved or connection fails
        """
        username = self.resolve_org_username(username_or_alias)

        # Return cached connection if available
        if username in self._connections:
            return self._connections[username]

        # Load auth info
        auth_info = self.load_auth_files()
        if username not in auth_info:
            raise ValueError(f"No auth info found for: {username}")

        org_data = auth_info[username]

        # Create connection
        try:
            # Support both access token and refresh token auth
            if access_token := org_data.get("accessToken"):
                sf = Salesforce(
                    instance_url=org_data["instanceUrl"],
                    session_id=access_token,
                )
            else:
                # Use refresh token flow
                sf = Salesforce(
                    instance_url=org_data["instanceUrl"],
                    username=username,
                    password="",  # Using stored tokens
                    security_token="",
                    organizationId=org_data.get("orgId"),
                )

            self._connections[username] = sf
            logger.info(f"Connected to org: {username}")
            return sf

        except Exception as e:
            raise ValueError(f"Failed to connect to org {username}: {e}")

    def get_all_allowed_orgs(self) -> List[Dict[str, Any]]:
        """Get all allowed orgs based on configuration.

        Returns:
            List of org information dictionaries
        """
        auth_info = self.load_auth_files()
        orgs = []

        for username, data in auth_info.items():
            # Skip alias entries
            if "@" not in username:
                continue

            # Check if allowed
            if self.config.is_org_allowed(username):
                orgs.append(
                    {
                        "username": username,
                        "alias": data.get("alias"),
                        "orgId": data.get("orgId"),
                        "instanceUrl": data.get("instanceUrl"),
                        "connectedStatus": data.get("connectedStatus", "Connected"),
                    }
                )

        # Handle special DEFAULT_TARGET_ORG values
        if "DEFAULT_TARGET_ORG" in self.config.allowed_orgs:
            default_org = self.get_default_org(dev_hub=False)
            if default_org and default_org in auth_info:
                data = auth_info[default_org]
                if not any(org["username"] == default_org for org in orgs):
                    orgs.append(
                        {
                            "username": default_org,
                            "alias": data.get("alias"),
                            "orgId": data.get("orgId"),
                            "instanceUrl": data.get("instanceUrl"),
                            "connectedStatus": data.get("connectedStatus", "Connected"),
                            "isDefault": True,
                        }
                    )

        if "DEFAULT_TARGET_DEV_HUB" in self.config.allowed_orgs:
            default_hub = self.get_default_org(dev_hub=True)
            if default_hub and default_hub in auth_info:
                data = auth_info[default_hub]
                if not any(org["username"] == default_hub for org in orgs):
                    orgs.append(
                        {
                            "username": default_hub,
                            "alias": data.get("alias"),
                            "orgId": data.get("orgId"),
                            "instanceUrl": data.get("instanceUrl"),
                            "connectedStatus": data.get("connectedStatus", "Connected"),
                            "isDefaultDevHub": True,
                        }
                    )

        return orgs
