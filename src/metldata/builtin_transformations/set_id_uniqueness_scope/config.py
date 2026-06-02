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

"""Configuration for the 'set id uniqueness scope' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SetIdUniquenessScopeConfig(BaseSettings):
    """Configuration for the set id uniqueness scope transformation."""

    globally_unique_ids: bool = Field(
        ...,
        description=(
            "If true, resource IDs must be globally unique across all classes."
            " If false, IDs only need to be unique within their respective class."
        ),
    )
