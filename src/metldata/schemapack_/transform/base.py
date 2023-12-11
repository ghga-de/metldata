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

"""Models to describe transformations and workflows."""

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from typing import Callable, Generic, Optional, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_validator,
    model_validator,
)
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack


class ModelAssumptionError(RuntimeError):
    """Raised when assumptions made by transformation step about a model are not met."""


class ModelTransformationError(RuntimeError):
    """Raised when a transformation failed when applied to the schemapack-based model.
    This exception should only be raised when the error could not have been caught
    earlier by model assumption checks (otherwise the AssumptionsInsufficiencyError
    should be raised instead)."""


class DataTransformationError(RuntimeError):
    """Raised when a transformation failed when applied to data in datapack-format.
    This exception should only be raised when the error could not have been caught
    earlier by model assumption checks (otherwise the EvitableTransformationError
    should be raised instead)."""


class EvitableTransformationError(RuntimeError):
    """Raised when an exception during the model or data transformation should have
    been caught earlier by model assumption or data validation checks."""

    def __init__(self):
        super().__init__(
            "This unexpected error appeared during transformation, however, it should"
            + " have been caught earlier during model assumption checks (and/or by data"
            + " validation against the assumption-checked model). Please make sure that"
            + " the model assumption checks guarantee the workability of the"
            + " corresponding transformation wrt the provided model (and/or data)."
        )


Config = TypeVar("Config", bound=BaseModel)


class DataTransformer(ABC, Generic[Config]):
    """A base class for a data transformer."""

    def __init__(
        self,
        *,
        config: Config,
        input_model: SchemaPack,
        transformed_model: SchemaPack,
    ):
        """Initialize the transformer with config params, the input model, and the
        transformed model.
        """
        self._config = config
        self._input_model = input_model
        self._transformed_model = transformed_model

    @abstractmethod
    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        ...


@dataclass(frozen=True)
class TransformationDefinition(Generic[Config]):
    """A model for describing a transformation."""

    config_cls: type[Config] = Field(
        ..., description="The config model of the transformation."
    )
    check_model_assumptions: Callable[[SchemaPack, Config], None] = Field(
        ...,
        description=(
            "A function that checks the assumptions made about the input model."
            "Raises a ModelAssumptionError if the assumptions are not met."
        ),
    )
    transform_model: Callable[[SchemaPack, Config], SchemaPack] = Field(
        ...,
        description=(
            "A function to transform the model. Raises a"
            + " ModelTransformationError if the transformation fails."
        ),
    )
    data_transformer_factory: type[DataTransformer] = Field(
        ...,
        description=(
            "A class for transforming data. Raises a DataTransformationError"
            "if the transformation fails."
        ),
    )


class WorkflowConfig(BaseModel, ABC):
    """A base class for workflow configs."""


class WorkflowStepBase(BaseModel, ABC):
    """A base class for workflow steps."""

    model_config = ConfigDict(frozen=True)
    description: str = Field(..., description="A description of the step.")
    input: Optional[str] = Field(
        ...,
        description=(
            "The name of the workflow step from which the output is used as input"
            " for this step. If this is the first step, set to None."
        ),
    )


class WorkflowStep(WorkflowStepBase):
    """A single step in a transformation workflow."""

    transformation_definition: TransformationDefinition = Field(
        ...,
        description="The transformation to be executed in this step.",
    )


class WorkflowDefinition(BaseModel):
    """A definition of a transformation workflow."""

    model_config = ConfigDict(frozen=True)
    description: str = Field(..., description="A description of the workflow.")
    steps: dict[str, WorkflowStep] = Field(
        ...,
        description=(
            "A dictionary of workflow steps. The keys are the names of the steps, and"
            + " the values are the workflow steps themselves."
        ),
    )
    artifacts: dict[str, str] = Field(
        ...,
        description=(
            "A dictionary of artifacts that are output by this workflow."
            + " The keys are the names of the artifacts, and the values are the names"
            + " of the workflow steps that output them."
        ),
    )

    # pylint: disable=no-self-argument
    @field_validator("steps", mode="after")
    def validate_step_references(
        cls, steps: dict[str, WorkflowStep]
    ) -> dict[str, WorkflowStep]:
        """Validate that workflow steps reference other existing steps as input.
        There should be exactly one step with input=None.
        """
        step_with_no_input_found = False

        for step_name, step in steps.items():
            if step.input is None:
                if step_with_no_input_found:
                    raise ValueError(
                        "There should be exactly one step with input=None. But multiple"
                        + " were found."
                    )
                step_with_no_input_found = True
                continue
            if step.input not in steps:
                raise ValueError(
                    f"Step {step.input} referenced in step {step_name} is not defined."
                )

        if not step_with_no_input_found:
            raise ValueError(
                "There should be exactly one step with input=None but none was found."
            )

        return steps

    @model_validator(mode="after")
    def validate_artifact_references(cls, values):
        """Validate that artifacts reference existing workflow steps."""
        steps = values.steps
        if steps is None:
            raise ValueError("Steps are undefined.")
        artifacts = values.artifacts
        if artifacts is None:
            raise ValueError("Artifacts are undefined.")

        for artifact_name, step_name in artifacts.items():
            if step_name not in steps:
                raise ValueError(
                    f"Step {step_name} referenced in artifact {artifact_name} is not defined."
                )

        return values

    @property
    def config_cls(self) -> type[WorkflowConfig]:
        """Get a config model containing the config requirements from all workflow
        steps.
        """
        step_configs = {
            step_name: (step.transformation_definition.config_cls, ...)
            for step_name, step in self.steps.items()
        }

        config_cls = create_model(  # type: ignore
            "SpecificWorkflowConfig",
            **step_configs,
            __base__=WorkflowConfig,
        )

        return config_cls

    @property
    def step_order(self) -> list[str]:
        """Get a list of step names in the order in which the steps should be executed."""
        # create graph from steps
        graph: dict[str, set[str]] = defaultdict(set[str])
        for step_name, step in self.steps.items():
            if step.input:
                graph[step_name].add(step.input)

        # sort with TopologicalSorter
        topological_sorter = TopologicalSorter(graph)
        try:
            return list(topological_sorter.static_order())
        except CycleError as exc:
            raise RuntimeError("Step definitions imply a circular dependency.") from exc
