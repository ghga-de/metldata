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
from metldata.builtin_transformations.count_content_values.path.path import RelationPath

ADDED_PROPERTY_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "additionalProperties": True,
}


class SourcePaths(BaseSettings):
    """TODO"""

    relation_path: RelationPath
    content_path: str


class CountContentValuesInstruction(BaseSettings):
    """TODO"""

    class_name: str = Field(..., description="The name of the class to modify.")
    target_content: NewContentSchemaPath
    source: SourcePaths
