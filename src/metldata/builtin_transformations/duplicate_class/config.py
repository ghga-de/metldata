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

"""Models for instructions used in the 'duplicate class' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings


class DuplicateClassConfig(BaseSettings):
    """A model describing a configuration for duplicating a class."""

    source_class_name: str = Field(
        default=..., description="Name of the existing class to be duplicated."
    )
    target_class_name: str = Field(
        default=...,
        description="Name for the new duplicated class. Must not already exist in the model.",
    )
