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

import json

from metldata.workflow.base import (
    Workflow,
    WorkflowStep,
    WorkflowStepPrecursor,
    WorkflowTemplate,
)
from metldata.workflow.template_utils import apply_template


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
        expanded_steps = []
        for precursor in precursors:
            expanded_steps.extend(self.expand_loop(precursor))
        return expanded_steps

    def expand_loop(self, precursor: WorkflowStepPrecursor) -> list[WorkflowStep]:
        """Expand a loop in a workflow step precursor, producing multiple workflow steps."""
        precursor_json = precursor.model_dump()
        del precursor_json["loop"]
        return [
            WorkflowStep.model_validate_json(
                apply_template(json.dumps(precursor_json), item=value)
            )
            for value in precursor.loop
        ]
