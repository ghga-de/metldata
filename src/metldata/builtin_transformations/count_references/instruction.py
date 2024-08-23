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

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common import NewContentSchemaPath
from metldata.builtin_transformations.common.path.path import RelationPath


class AddReferenceCountPropertyInstruction(BaseSettings):
    """A model describing an instruction to"""

    class_name: str = Field(..., description="The name of the class to modify.")

    target_content: NewContentSchemaPath = Field(
        ...,
        description="A NewContentSchemaPath that describes a path to an already"
        + " existing object within the content schema and the name of a property to be"
        + " added to that object's schema",
    )
    source_relation_path: RelationPath = Field(
        ...,
        description="The path describing the relation between the classes of a metadata model.",
    )
