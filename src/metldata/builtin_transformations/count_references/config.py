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
"""Models used to describe count content properties that shall be calculated and added."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)


class CountReferencesConfig(BaseSettings):
    """Config containing content properties to be deleted from models and data."""

    model_config = SettingsConfigDict(extra="forbid")

    count_references: list[AddReferenceCountPropertyInstruction] = Field(
        ...,
        description=("Description TODO"),
        examples=[],
    )

    def instructions_by_class(
        self,
    ) -> dict[str, list[AddReferenceCountPropertyInstruction]]:
        """Returns a dictionary of instructions by class (i.e. config for each class)."""
        instructions_by_class: dict[
            str, list[AddReferenceCountPropertyInstruction]
        ] = {}
        for instruction in self.count_references:
            instructions_by_class.setdefault(instruction.class_name, []).append(
                instruction
            )
        return instructions_by_class
