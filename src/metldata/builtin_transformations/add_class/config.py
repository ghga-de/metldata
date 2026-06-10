# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Models for configuration used in the 'add class' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings
from schemapack.spec.schemapack import ClassRelation


class RelationSpec(ClassRelation):
    """A model extending a schemapack relation specification with additional annotation property
    pointing the field holding the references resource id.
    """

    relation_property_name: str = Field(description="The name of the relation.")
    target_resources: str = Field(
        description="Field in the new class's annotation holding the FK to the target resource."
    )


class AddClassConfig(BaseSettings):
    """A model describing a configuration for adding a class."""

    class_name: str = Field(
        default=...,
        description="The name of the class to add.",
    )
    id_property_name: str = Field(
        default=...,
        description="The property used as the resource ID.",
    )
    content_schema: dict = Field(
        default=...,
        description="A valid JSON Schema object describing the class content.",
    )
    description: str | None = Field(
        default=None,
        description="Description of the class.",
    )
    relations: list[RelationSpec] = Field(
        default_factory=list,
        description="Relations from the new class to existing classes.",
    )
