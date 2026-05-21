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

"""Logic for executing workflows."""

from collections.abc import Mapping
from typing import Any

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.transform.handling import TransformationHandler
from metldata.workflow.base import Workflow, WorkflowStep
from metldata.workflow.exceptions import (
    UnknownTransformationError,
    WorkflowExecutionError,
)


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
        self.step_name = self.workflow_step.name
        self.step_args = self.workflow_step.args

    def execute(
        self,
        transformation_registry: Mapping[str, Any],
        *,
        validate_input: bool = False,
        validate_output: bool = False,
    ) -> TransformationHandler:
        """Executes the workflow step by retrieving the corresponding transformation
        from the registry and initializing a TransformationHandler.

        Raises a UnknownTransformationError if the transformation is not found in the registry.
        """
        try:
            transformation_definition = transformation_registry[self.step_name]
        except KeyError as error:
            raise UnknownTransformationError(
                f"Invalid transformation name. {self.step_name} does not exist in the "
                "transformation registry."
            ) from error

        return TransformationHandler(
            transformation_definition=transformation_definition,
            transformation_config=transformation_definition.config_cls(
                **self.step_args
            ),
            input_model=self.input_model,
            validate_input=validate_input,
            validate_output=validate_output,
        )


class WorkflowHandler[SubmissionAnnotation]:
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
        transformation_registry: Mapping[str, Any],
        input_model: SchemaPack,
    ):
        self.workflow = workflow
        self.transformation_registry = transformation_registry
        self.input_model = input_model

        # populated in place by _build_transformation_handlers, which is called during initialization
        self._transformation_handlers: list[TransformationHandler] = []
        self.output_model = self._build_transformation_handlers()

    def _build_transformation_handlers(self) -> SchemaPack:
        """Execute each workflow step to build the transformation handlers and
        return the final transformed model.
        """
        model = self.input_model
        last_step = len(self.workflow.operations) - 1

        for idx, step in enumerate(self.workflow.operations):
            step_handler = WorkflowStepHandler(workflow_step=step, input_model=model)

            transformation_handler = step_handler.execute(
                self.transformation_registry,
                validate_input=(idx == 0),
                validate_output=(idx == last_step),
            )
            self._transformation_handlers.append(transformation_handler)
            model = transformation_handler.transformed_model

        return model

    def run(self, data: DataPack, annotation: SubmissionAnnotation) -> DataPack:
        """Apply each transformation's data step in sequence and return the
        resulting :class:`DataPack`. The transformed model is available on
        :attr:`output_model`.
        Raises a WorkflowExecutionError if any transformation raises an error during execution.
        """
        for handler in self._transformation_handlers:
            try:
                data = handler.transform_data(data, annotation)
            except Exception as error:
                raise WorkflowExecutionError(
                    transformation_handler=handler, error=error
                ) from error
        return data
