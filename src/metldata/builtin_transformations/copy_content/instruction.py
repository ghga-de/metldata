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

"""Models for instructions used in the 'copy content' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common import NewContentSchemaPath, SourcePath


class CopyContentSchemaPath(NewContentSchemaPath):
    """Specialized version of NewContentSchemaPath that adds a default object path to
    remove the necessity to explicitly specify an empty object path for properties to
    be copied to the root class content.
    """

    object_path: str = Field(
        "",
        description=(
            "The path to the content object to which a property shall be added. The"
            + " path must be specified in dot notation, equivalently to JavaScript"
            + " property accessors."
        ),
        examples=["some_property.another_nested_property"],
    )


class CopyContentInstruction(BaseSettings):
    """A model describing an instruction to copy a content property from one class in a
    schemapack to another.
    """

    class_name: str = Field(..., description="The name of the class to modify.")

    target_content: CopyContentSchemaPath = Field(
        ...,
        description="NewContentSchemaPath object describing where a"
        + " content property will be copied to.",
    )

    source: SourcePath = Field(
        ...,
        description="SourcePath object defining the path to reach a property"
        + " from which content values are copied.",
    )
