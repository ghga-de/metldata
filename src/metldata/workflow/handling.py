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

"""Logic for executing workflows."""

from typing import Any

from pydantic import BaseModel, ConfigDict
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.transform.handling import TransformationHandler
from metldata.workflow.base import Workflow, WorkflowStep
from metldata.workflow.exceptions import UnknownTransformationError


class WorkflowResult(BaseModel):
    """Model and data after workflow execution."""

    model_config = ConfigDict(frozen=True)

    model: SchemaPack
    data: DataPack


class WorkflowStepHandler:
    """Handles the execution of a single workflow step by linking it to the appropriate
    transformation.

    Attributes:
    workflow_step (WorkflowStep): The workflow step to be executed.
    input_model (SchemaPack): The input model to be used for the transformation.
    """

    def __init__(self, workflow_step: WorkflowStep, input_model: SchemaPack):
        self.workflow_step = workflow_step
        self.input_model = input_model

    def execute(self, transformation_registry: dict[str, Any]) -> TransformationHandler:
        """Executes the workflow step by retrieving the corresponding transformation
        from the registry and initializing a TransformationHandler.

        Raises a ValueError if the transformation is not found in the registry.
        """
        step_name = self.workflow_step.name
        step_args = self.workflow_step.args

        if step_name not in transformation_registry:
            raise UnknownTransformationError(
                f"Invalid transformation name. {step_name} does not exist in the "
                "transformation registry."
            )

        transformation_definition = transformation_registry[step_name]
        return TransformationHandler(
            transformation_definition=transformation_definition,
            transformation_config=transformation_definition.config_cls(**step_args),
            input_model=self.input_model,
        )


class WorkflowHandler:
    """Handles the execution of a workflow, applying a sequence of transformations
    to a datapack and associated schemapack.

    Attributes:
        workflow (Workflow): The workflow to be executed.
        transformation_registry (dict[str, Any]): A mapping from transformation names
            to their definitions.
        input_model (SchemaPack): The initial schema model that will be transformed by
            the workflow.

    """

    def __init__(
        self,
        workflow: Workflow,
        transformation_registry: dict[str, Any],
        input_model: SchemaPack,
    ):
        self.workflow = workflow
        self.transformation_registry = transformation_registry
        self.input_model = input_model

    def run(self, data: DataPack) -> WorkflowResult:
        """Executes the workflow, applying each transformation in sequence to the model
        and data, and returns the final model and data as a WorkflowResult.
        """
        model = self.input_model

        for step in self.workflow.operations:
            transformation_handler = WorkflowStepHandler(
                workflow_step=step, input_model=model
            ).execute(self.transformation_registry)
            model = transformation_handler.transformed_model
            data = transformation_handler.transform_data(data)

        return WorkflowResult(model=model, data=data)
