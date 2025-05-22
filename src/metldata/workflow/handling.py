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

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

from schemapack import load_schemapack
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.transform.handling import TransformationHandler
from metldata.workflow.base import Workflow, WorkflowStep


@dataclass
class WorkflowResult:
    """Model and data after workflow execution."""

    model: SchemaPack
    data: DataPack


class WorkflowStepHandler:
    """Used for linking workflow step to transformations"""

    def __init__(self, workflow_step: WorkflowStep, input_model: SchemaPack):
        self.workflow_step = workflow_step
        self.input_model = input_model

    def run(self, transformation_registry: dict[str, Any]):
        """Run a singe workflow step."""
        step_name = self.workflow_step.name
        step_args = self.workflow_step.args

        if step_name not in transformation_registry:
            raise ValueError(f"Unknown transformation: {step_name}")

        transformation_definition = transformation_registry[step_name]
        return TransformationHandler(
            transformation_definition=transformation_definition,
            transformation_config=transformation_definition.config_cls(**step_args),
            input_model=self.input_model,
        )


class WorkflowHandler:
    """Executes a workflow step by step."""

    def __init__(
        self,
        workflow: Workflow,
        transformation_registry: dict[str, Any],
        model_registry: Path,
    ):
        self.workflow = workflow
        self.transformation_registry = transformation_registry
        # model registry is a temporary implementations.
        self.model_registry = model_registry

    @cached_property
    def input_model(self) -> SchemaPack:
        """Fetch the workflow's input model."""
        file_path = self.model_registry / self.workflow.input
        if not file_path.exists():
            raise FileNotFoundError(f"Input model file not found: {file_path}")
        return load_schemapack(file_path)

    def run(self, data: DataPack) -> WorkflowResult:
        """Run the workflow step by step, transform the model and the data."""
        model = self.input_model

        for step in self.workflow.operations:
            step_handler = WorkflowStepHandler(
                workflow_step=step, input_model=model
            ).run(self.transformation_registry)
            model = step_handler.transformed_model
            data = step_handler.transform_data(data)

        return WorkflowResult(model=model, data=data)
