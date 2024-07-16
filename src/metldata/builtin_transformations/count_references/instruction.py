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
"""Models for instructions used in the 'add content properties' transformation."""

from typing import Any, Final

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common import NewContentSchemaPath

DEFAULT_REFERENCE_COUNT_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"count": {"type": "integer"}},
    "required": ["count"],
}


class AddCountPropertyInstruction(BaseSettings):
    """A model describing an instruction to
    TODO reference_count_schema don't have to be exposed
    """

    class_name: str = Field(..., description="The name of the class to modify.")

    target_content_path: NewContentSchemaPath = Field(
        ...,
        description="A NewContentSchemaPath that describes a path to an already"
        + " existing object within the content schema and the name of a property to be"
        + " added to that object's schema",
    )

    required: bool = Field(
        True,
        description=(
            "Indicates whether the newly added property shall be added to the"
            + " 'required' list of the corresponding object. Defaults to 'True'."
        ),
    )

    reference_count_schema: dict[str, Any] = Field(
        DEFAULT_REFERENCE_COUNT_SCHEMA,
        description="The JSON schema of the newly added property.",
    )

    # value: Any = Field({}, description="Value needs to be calculated")
