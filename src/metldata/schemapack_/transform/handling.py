# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Logic for handling Transformation."""

from pydantic import BaseModel, ConfigDict
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack
from schemapack.validation import SchemaPackValidator

from metldata.schemapack_.transform.base import (
    Config,
    TransformationDefinition,
    WorkflowConfig,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowStepBase,
)


class WorkflowConfigMismatchError(RuntimeError):
    """Raised when the provided workflow config does not match the config class of the
    workflow definition.
    """

    def __init__(
        self, workflow_definition: WorkflowDefinition, workflow_config: BaseModel
    ):
        """Initialize the error with the workflow definition and the config."""
        message = (
            f"The config {workflow_config} is not an instance of the config class "
            f"{workflow_definition.config_cls} of the workflow definition "
            f"{workflow_definition}."
        )
        super().__init__(message)


class TransformationHandler:
    """Used for executing transformations described in a TransformationDefinition."""

    def __init__(
        self,
        transformation_definition: TransformationDefinition[Config],
        transformation_config: Config,
        input_model: SchemaPack,
    ):
        """Initialize the TransformationHandler by checking the assumptions made on the
        input model and transforming the model as described in the transformation
        definition. The transformed model is available at the `transformed_model`
        attribute.

        Raises:
            ModelAssumptionError:
                if the assumptions made on the input model are not met.
        """
        self._definition = transformation_definition
        self._config = transformation_config
        self._input_model = input_model

        self._definition.check_model_assumptions(self._input_model, self._config)
        self.transformed_model = self._definition.transform_model(
            self._input_model, self._config
        )
        self._data_transformer = self._definition.data_transformer_factory(
            config=self._config,
            input_model=self._input_model,
            transformed_model=self.transformed_model,
        )

        self._original_data_validator = SchemaPackValidator(
            schemapack=self._input_model
        )
        self._transformed_data_validator = SchemaPackValidator(
            schemapack=self.transformed_model
        )

    def transform_data(self, data: DataPack) -> DataPack:
        """Transforms data using the transformation definition. Validates the
        input data against the input model and the transformed data
        against the transformed model.

        Args:
            data: The data to be transformed.

        Raises:
            schemapack.exceptions.ValidationError:
                If validation of input data or transformed data fails against the
                original or transformed model, respectively.
            DataTransformationError:
                if the transformation fails.
        """
        self._original_data_validator.validate(datapack=data)
        transformed_data = self._data_transformer.transform(data=data)
        self._transformed_data_validator.validate(datapack=transformed_data)

        return transformed_data


class ResolvedWorkflowStep(WorkflowStepBase):
    """A resolved workflow step contains a transformation handler."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    transformation_handler: TransformationHandler


class ResolvedWorkflow(WorkflowDefinition):
    """A resolved workflow contains a list of resolved workflow steps."""

    steps: dict[str, ResolvedWorkflowStep]  # type: ignore
    workflow_config: WorkflowConfig


def check_workflow_config(
    *, workflow_definition: WorkflowDefinition, workflow_config: WorkflowConfig
):
    """Checks if the config is an instance of the config class of the workflow
    definition.

    Raises:
        WorkflowConfigMismatchError:
    """
    if isinstance(workflow_config, workflow_definition.config_cls):
        raise WorkflowConfigMismatchError(
            workflow_definition=workflow_definition, workflow_config=workflow_config
        )


def resolve_workflow_step(
    *,
    workflow_step: WorkflowStep,
    step_name: str,
    workflow_definition: WorkflowDefinition,
    workflow_config: WorkflowConfig,
    input_model: SchemaPack,
) -> ResolvedWorkflowStep:
    """Translates a workflow step given a workflow definition and a workflow config
    into a resolved workflow step.
    """
    check_workflow_config(
        workflow_definition=workflow_definition, workflow_config=workflow_config
    )

    transformation_config: BaseModel = getattr(workflow_config, step_name)
    transformation_handler = TransformationHandler(
        transformation_definition=workflow_step.transformation_definition,
        transformation_config=transformation_config,
        input_model=input_model,
    )
    return ResolvedWorkflowStep(
        transformation_handler=transformation_handler,
        input=workflow_step.input,
        description=workflow_step.description,
    )


def resolve_workflow(
    workflow_definition: WorkflowDefinition,
    input_model: SchemaPack,
    workflow_config: WorkflowConfig,
) -> ResolvedWorkflow:
    """Translates a workflow definition given an input model and a workflow config into
    a resolved workflow.
    """
    check_workflow_config(
        workflow_definition=workflow_definition, workflow_config=workflow_config
    )

    resolved_steps: dict[str, ResolvedWorkflowStep] = {}
    for step_name in workflow_definition.step_order:
        workflow_step = workflow_definition.steps[step_name]
        input_model = (
            input_model
            if workflow_step.input is None
            else resolved_steps[
                workflow_step.input
            ].transformation_handler.transformed_model
        )

        resolved_steps[step_name] = resolve_workflow_step(
            workflow_step=workflow_step,
            step_name=step_name,
            workflow_definition=workflow_definition,
            workflow_config=workflow_config,
            input_model=input_model,
        )

    return ResolvedWorkflow(
        steps=resolved_steps,
        workflow_config=workflow_config,
        description=workflow_definition.description,
        artifacts=workflow_definition.artifacts,
    )


def get_model_artifacts_from_resolved_workflow(resolved_workflow: ResolvedWorkflow):
    """Returns a dictionary of models for artifacts produced by resolved workflow."""
    return {
        artifact_name: resolved_workflow.steps[
            step_name
        ].transformation_handler.transformed_model
        for artifact_name, step_name in resolved_workflow.artifacts.items()
    }


class WorkflowHandler:
    """Used for executing workflows described in a WorkflowDefinition."""

    def __init__(
        self,
        workflow_definition: WorkflowDefinition,
        workflow_config: WorkflowConfig,
        input_model: SchemaPack,
    ):
        """Initialize the WorkflowHandler with a workflow deinition, a matching
        config, and a model. The workflow definition is translated into a
        resolved workflow.
        """
        self._resolved_workflow = resolve_workflow(
            workflow_definition=workflow_definition,
            input_model=input_model,
            workflow_config=workflow_config,
        )

        self.artifact_models = get_model_artifacts_from_resolved_workflow(
            self._resolved_workflow
        )

    def run(self, *, data: DataPack) -> dict[str, DataPack]:
        """Run the workflow definition on data to generate artifacts."""
        transformed_data: dict[str, DataPack] = {}
        for step_name in self._resolved_workflow.step_order:
            step = self._resolved_workflow.steps[step_name]
            input_data = data if step.input is None else transformed_data[step.input]
            transformed_data[step_name] = step.transformation_handler.transform_data(
                input_data
            )

        return {
            artifact_name: transformed_data[step_name]
            for artifact_name, step_name in self._resolved_workflow.artifacts.items()
        }
