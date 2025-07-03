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

"Models for configuration used in the 'merge relations' transformation."

import ast

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from schemapack.spec.schemapack import MandatoryRelationSpec, MultipleRelationSpec


class MergeRelationsConfig(BaseSettings):
    """A model describing a configuration for merging relations."""

    class_name: str = Field(
        default=..., description="The name of the class to merge relations for."
    )
    description: str | None = Field(
        default=None, description="Description of the relation."
    )
    source_relations: list[str] = Field(
        default=..., description="List of relation names to be merged."
    )
    target_relation: str = Field(
        default=..., description="The name of the relation to merge into."
    )
    mandatory: MandatoryRelationSpec = Field(
        ..., description=("The modality of the relation.")
    )
    multiple: MultipleRelationSpec = Field(
        ..., description=("The cardinality of the relation.")
    )

    @field_validator("source_relations", mode="before")
    @classmethod
    def convert_source_relations(cls, value):
        """Handles Jinja2 rendering that stringifies lists: converts string source_relations
        into a list before pydantic validation.
        """
        if isinstance(value, str):
            return ast.literal_eval(value)
        return value
