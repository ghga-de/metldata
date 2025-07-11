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

"""Logic to build a workflow from a template."""

from metldata.workflow.base import (
    Workflow,
    WorkflowStep,
    WorkflowStepPrecursor,
    WorkflowTemplate,
)
from metldata.workflow.template_utils import apply_loop

PROBLEMATIC_PROPERTY = "data_template"


class WorkflowBuilder:
    """A builder class for constructing Workflow objects from WorkflowTemplate instances.

    Attributes:
        template (WorkflowTemplate): The workflow template used as the basis for building the workflow.
    """

    def __init__(self, template: WorkflowTemplate):
        self.template = template

    def build(self) -> Workflow:
        """Build and return a Workflow object based on the template, with all loops expanded."""
        precursors = self.generate_step_precursors()
        operations = self.expand_loops(precursors)
        return Workflow(
            operations=operations,
        )

    def generate_step_precursors(self) -> list[WorkflowStepPrecursor]:
        """Generate workflow step precursors from the template's operations."""
        return [
            WorkflowStepPrecursor.model_validate(operation)
            for operation in self.template.operations
        ]

    def expand_loops(
        self, precursors: list[WorkflowStepPrecursor]
    ) -> list[WorkflowStep]:
        """Expand all loops in a list of workflow step precursors."""
        precursor_dicts = [
            precursor.model_dump(mode="json") for precursor in precursors
        ]
        step_dicts = [
            step
            for precursor_dict in precursor_dicts
            for step in apply_loop(precursor_dict)
        ]
        return [WorkflowStep.model_validate(step_dict) for step_dict in step_dicts]

    def convert_precursor_without_loop(
        self, precursor: WorkflowStepPrecursor
    ) -> WorkflowStep:
        """Convert a step precursor without a loop into a proper WorkflowStep"""
        return WorkflowStep.model_validate_json(precursor.model_dump_json())
