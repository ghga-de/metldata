# Copyright 2021 - 2024 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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
"""Model transformation logic for the 'add content property' transformation"""

from typing import Any

from schemapack.spec.schemapack import (
    SchemaPack,
)

from metldata.builtin_transformations.add_content_properties.instruction import (
    AddContentPropertyInstruction,
)
from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.transform.base import EvitableTransformationError


def add_counted_values(
    *,
    model: SchemaPack,
    instructions: list[Any],
) -> SchemaPack:
    """Adds a new content property to the provided model."""
