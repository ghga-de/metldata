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

"""Public entry point for executing a workflow."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.registry import get_transformation_registry
from metldata.workflow.base import Workflow
from metldata.workflow.handling import WorkflowHandler


class WorkflowRunner[SubmissionAnnotation]:
    """Public, registry-aware entry point for running a workflow.

    Model transformations are applied eagerly during construction and exposed
    via :attr:`model`. Data transformations are deferred to
    :meth:`run_workflow`, which may be called once or many times against the
    same transformed model.
    """

    def __init__(self, *, workflow: Workflow, input_model: SchemaPack):
        self._handler: WorkflowHandler[SubmissionAnnotation] = WorkflowHandler(
            workflow=workflow,
            transformation_registry=get_transformation_registry(),
            input_model=input_model,
        )

    @property
    def model(self) -> SchemaPack:
        """The transformed schema model produced by the workflow."""
        return self._handler.output_model

    def run_workflow(
        self, *, data: DataPack, annotation: SubmissionAnnotation
    ) -> DataPack:
        """Apply the workflow's data transformations and return the result."""
        return self._handler.run(data=data, annotation=annotation)
