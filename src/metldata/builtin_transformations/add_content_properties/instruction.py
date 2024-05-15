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

DEFAULT_CONTENT_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "additionalProperties": False,
}


class NewContentSchemaPath(BaseSettings):
    """A model describing the path of an object property within the content schema that
    is yet to be added. The model comprises a path to an already existing object within
    the content schema and the name of a property to be added to that object's schema
    """

    object_path: str = Field(
        ...,
        description=(
            "The path to the content object to which a property shall be added. The"
            + " path must be specified in dot notation, equivalently to JavaScript"
            + " property accessors."
        ),
        examples=["some_property.another_nested_property"],
    )

    property_name: str = Field(..., description="The name of the property to be added.")


class AddContentPropertyInstruction(BaseSettings):
    """A model describing an instruction to add a new content property to a class in a
    schemapack, including an associated default value in corresponding data.
    """

    class_name: str = Field(..., description="The name of the class to modify.")

    target_content: NewContentSchemaPath

    required: bool = Field(
        True,
        description=(
            "Indicates whether the newly added property shall be added to the"
            + " 'required' list of the corresponding object. Defaults to 'True'."
        ),
    )

    content_schema: dict[str, Any] = Field(
        DEFAULT_CONTENT_SCHEMA,
        description="The JSON schema of the newly added property.",
    )

    value: Any = Field(
        {}, description="A value to assign to the new property in the data."
    )
