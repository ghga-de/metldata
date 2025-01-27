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

"""Models for instructions used in the 'count content values' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common import NewContentSchemaProperty, SourcePath


class CopyContentInstruction(BaseSettings):
    """A model describing an instruction to add a new content property to a class in a
    schemapack, including an associated default value in corresponding data.
    """

    class_name: str = Field(..., description="The name of the class to modify.")

    target_content: NewContentSchemaProperty = Field(
        ...,
        description="Contains the name of the property to be added to the target"
        + " content schema.",
    )

    source: SourcePath = Field(
        ...,
        description="SourcePath object defining the path to reach a property"
        + " from which content values are sourced.",
    )
