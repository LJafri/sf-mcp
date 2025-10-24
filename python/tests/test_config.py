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

"""Tests for configuration management."""

import pytest
from salesforce_mcp.config import ServerConfig


def test_server_config_creation():
    """Test basic server configuration creation."""
    config = ServerConfig(
        version="0.15.0",
        allowed_orgs=["test@example.com"],
        toolsets=["all"],
    )
    assert config.version == "0.15.0"
    assert "test@example.com" in config.allowed_orgs
    assert config.toolsets == ["all"]


def test_is_org_allowed_specific():
    """Test org allowlist checking for specific orgs."""
    config = ServerConfig(
        version="0.15.0",
        allowed_orgs=["test@example.com", "admin@example.com"],
        toolsets=["all"],
    )
    assert config.is_org_allowed("test@example.com")
    assert config.is_org_allowed("admin@example.com")
    assert not config.is_org_allowed("other@example.com")


def test_is_org_allowed_all():
    """Test org allowlist checking with ALLOW_ALL_ORGS."""
    config = ServerConfig(
        version="0.15.0",
        allowed_orgs=["ALLOW_ALL_ORGS"],
        toolsets=["all"],
    )
    assert config.is_org_allowed("any@example.com")
    assert config.is_org_allowed("another@example.com")


def test_is_toolset_enabled():
    """Test toolset enabled checking."""
    config = ServerConfig(
        version="0.15.0",
        allowed_orgs=["test@example.com"],
        toolsets=["data", "orgs"],
    )
    assert config.is_toolset_enabled("data")
    assert config.is_toolset_enabled("orgs")
    assert not config.is_toolset_enabled("metadata")


def test_is_toolset_enabled_all():
    """Test toolset enabled checking with 'all'."""
    config = ServerConfig(
        version="0.15.0",
        allowed_orgs=["test@example.com"],
        toolsets=["all"],
    )
    assert config.is_toolset_enabled("data")
    assert config.is_toolset_enabled("orgs")
    assert config.is_toolset_enabled("metadata")
    assert config.is_toolset_enabled("testing")
