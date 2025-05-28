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


class WorkflowTemplate(BaseModel):
    """Base class for workflow templates."""

    input: str = Field(
        default=..., description="The input model version for the transformation subject."
    )
    output: str = Field(
        default=...,
        description="Identifier for the resulting model the workflow is applied.",
    )

    operations: list[dict] = Field(
        default=..., description="List of operations to apply during the workflow"
    )


class WorkflowStepBase(BaseModel):
    """Represents a single step within a workflow, defining a transformation to be applied."""

    name: str = Field(
        default=...,
        description="The name of the transformation that corresponds to an entry"
        + " in the transformation registry.",
    )
    description: str = Field(description="A description explaining the workflow step.")
    args: object = Field(
        default=...,
        description="The arguments or parameters required by the transformation."
        + " These are passed to the transformation definition and vary depending"
        + " on the transformation type.",
    )


class WorkflowStepPrecursor(WorkflowStepBase):
    """Represents a precursor model with loop specification by extending
    'WorkflowStepBase' with a loop attribute.
    """

    loop: list[object] = Field(
        default_factory=list,
        description="Optional list specifying loop parameters for the workflow step.",
    )


TransformationConfig = TypeVar("TransformationConfig", bound=BaseModel)


class WorkflowStep[TransformationConfig](WorkflowStepBase):
    """Represents a fully derived workflow step model."""

    args: TransformationConfig = Field(
        default=..., description="The configuration arguments for the workflow step."
    )


class Workflow(BaseModel):
    """Represents a workflow consisting of a sequence of transformation steps."""

    input: str = Field(
        default=...,
        description="The model version that serves as the input to the workflow.",
    )
    output: str = Field(
        default=...,
        description="The identifier or name for the output produced by the workflow.",
    )

    operations: list[WorkflowStep] = Field(
        default=...,
        description="The ordered list of workflow steps to be applied to the input model.",
    )
