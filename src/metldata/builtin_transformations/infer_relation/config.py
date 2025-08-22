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

"Models for configuration used in the 'infer relation' transformation."

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common.path import RelationPath


class InferRelationConfig(BaseSettings):
    """Configuration for the 'infer relation' transformation."""

    class_name: str = Field(
        default=..., description="Name of the class for which to infer a relation."
    )
    relation_name: str = Field(
        default=...,
        description="Name of the newly inferred relation.",
    )
    relation_path: RelationPath = Field(
        default=..., description="Path to the relation."
    )
