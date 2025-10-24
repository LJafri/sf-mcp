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

"""Tool registration and management for Salesforce MCP."""

from salesforce_mcp.tools.core import register_core_tools
from salesforce_mcp.tools.data import register_data_tools
from salesforce_mcp.tools.metadata import register_metadata_tools
from salesforce_mcp.tools.orgs import register_org_tools
from salesforce_mcp.tools.testing import register_testing_tools
from salesforce_mcp.tools.users import register_user_tools

__all__ = [
    "register_core_tools",
    "register_data_tools",
    "register_metadata_tools",
    "register_org_tools",
    "register_testing_tools",
    "register_user_tools",
]
