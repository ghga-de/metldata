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

"""Model transformation logic for the 'count references' transformation"""

from typing import Any, Final

from schemapack.spec.schemapack import (
    SchemaPack,
)

from metldata.builtin_transformations.common.model_transform import add_properties
from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)

DEFAULT_PROPERTY_SCHEMA: Final[dict[str, Any]] = {"type": "integer"}


def add_count_references(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[AddReferenceCountPropertyInstruction]],
) -> SchemaPack:
    """The target content - object_names are added to the model with the 'add_content_properties
    step of the workflow. Thus, this function only adds the property_name to a content schema.
    """
    return add_properties(
        model=model,
        instructions_by_class=instructions_by_class,
        source_schema=DEFAULT_PROPERTY_SCHEMA,
    )
