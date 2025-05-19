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

"""Models to describe workflow."""

from typing import TypeVar

from pydantic import BaseModel, Field


class WorkflowStepBase(BaseModel):
    """Base class for workflow steps."""

    name: str
    description: str = Field(default=..., description="A description of the step.")
    args: object


class WorkflowStepPrecursor(WorkflowStepBase):
    """Precursor model with loop specification"""

    loop: list[object] = []


TConfig = TypeVar("TConfig", bound=BaseModel)


class WorkflowStep[TConfig](WorkflowStepBase):
    """Fully derived workflow step model"""

    args: TConfig


class Workflow(BaseModel):
    """Base class for workflow."""

    input: str = Field(default=..., description="Model version")
    output: str = Field(default=..., description="Output name")

    operations: list[WorkflowStep] = Field(
        default=..., description="The steps of the workflow."
    )
