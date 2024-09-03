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
"""Models and functions related to content schema manipulation."""

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common.path.path import RelationPath


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


class SourcePath(BaseSettings):
    """A model describing the source path of an object within the schema that describes
    the path to navigate between classes and the content schema property that is to be
    used in a transformation.
    """

    relation_path: RelationPath = Field(
        ...,
        description="A RelationPath establishing how to navigate between classes.",
        examples=["ClassA(relation)>ClassB"],
    )
    content_path: str = Field(..., description="Content schema property name")
