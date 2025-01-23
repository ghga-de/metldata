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

"""Models for instructions used in the 'sum operation' transformation."""

from pydantic import Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common.contentschema import (
    NewContentSchemaPath,
    SourcePath,
)


class SumOperationInstruction(BaseSettings):
    """A model describing an instruction add a new content property that holds
    the sum of values from another property.
    """

    class_name: str = Field(..., description="The name of the class to modify.")

    target_content: NewContentSchemaPath = Field(
        ...,
        description="NewContentSchemaPath object describing where a new"
        + " content property will be added.",
    )

    source: SourcePath = Field(
        ...,
        description="A SourcePath object defining the path to the property containing"
        + "the values to be summed for the new content property.",
    )