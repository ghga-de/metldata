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

"""Models for instructions used in the 'delete class' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings


class TransformContentConfig(BaseSettings):
    """A model describing an instruction for deleting a class ."""

    class_name: str = Field(
        default=..., description="Name of the class that should be transformed."
    )
    model: dict[str, object] = Field(
        default_factory=dict,
        description="Schema the transformed data needs to adhere to.",
    )
    embedding_profile: dict[str, object] = Field(
        default_factory=dict,
        description="(Optional?) Embedding profile for denormalization.",
    )
    data_template: str = Field(
        default=..., description="Jinja template used to transform existing content."
    )
