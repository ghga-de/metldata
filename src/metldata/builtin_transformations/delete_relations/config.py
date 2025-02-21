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

"""Models used to describe relations that shall be deleted."""

from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from metldata.builtin_transformations.common.instruction import instructions_by_class
from metldata.builtin_transformations.delete_relations.instruction import (
    DeleteRelationInstruction,
)


class DeleteRelationsConfig(BaseSettings):
    """Config containing relation name to be deleted from the model and the data."""

    model_config = SettingsConfigDict(extra="forbid")

    delete_relations: list[DeleteRelationInstruction] = Field(
        default=...,
        description="A list of instructions describing which relation is removed from"
        + " which class.",
    )

    @cached_property
    def instructions_by_class(self):
        """Returns a dictionary of instructions by class."""
        return instructions_by_class(self.delete_relations)
