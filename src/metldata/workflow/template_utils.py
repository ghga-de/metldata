# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
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

"""Utility functions for handling Jinja2 templates in workflows."""

from collections.abc import Mapping
from typing import Any

from jinja2.sandbox import ImmutableSandboxedEnvironment

# Random string, effectively disabling Jinja2 blocks and comments
RANDOM_START_END_STRING = "Wk4CPM:"
env = ImmutableSandboxedEnvironment(
    block_start_string=RANDOM_START_END_STRING,
    block_end_string=RANDOM_START_END_STRING,
    variable_start_string="{{{",
    variable_end_string="}}}",
    comment_start_string=RANDOM_START_END_STRING,
    comment_end_string=RANDOM_START_END_STRING,
)


def render_single_item(data: Any, item: Any) -> Any:
    """Recursively renders a variable named 'item' in a Json-compatible data structure."""
    if isinstance(data, str):
        return env.from_string(data).render(item=item)
    elif isinstance(data, Mapping):
        return {key: render_single_item(value, item) for key, value in data.items()}
    elif isinstance(data, list | tuple):
        return [render_single_item(value, item) for value in data]
    else:
        return data


def render_items(data: dict[str, Any], items: list[Any]) -> list[dict[str, Any]]:
    """Applies a loop to the data by rendering the template for each item."""
    return [render_single_item(data, item) for item in items]


def apply_loop(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Applies a loop to the data by rendering the template for each item in the 'loop'
    key if present.
    """
    if not data.get("loop", False):
        return [data]
    items = data.pop("loop")
    return render_items(data, items)
