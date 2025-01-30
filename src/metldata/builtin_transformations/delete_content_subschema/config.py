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
#

"""Models used to describe content properties that shall be deleted."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeleteContentSubschemaConfig(BaseSettings):
    """Config containing content properties to be deleted from models and data."""

    model_config = SettingsConfigDict(extra="forbid")

    properties_to_delete: dict[str, list[str]] = Field(
        ...,
        description=(
            "A nested dictionary specifying properties that should be deleted per"
            + " class. The keys refer to classes, the values to the properties that"
            + " should be deleted from the respective class."
        ),
        examples=[
            {
                "ClassA": ["some_property", "another_property"],
                "ClassB": ["some_property"],
                "ClassC": ["some_property", "yet_another_property"],
            }
        ],
    )
