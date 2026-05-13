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

"""One-shot entry point for executing a workflow."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.registry import get_transformation_registry
from metldata.workflow.base import Workflow
from metldata.workflow.handling import WorkflowHandler, WorkflowResult


def run_workflow(
    workflow: Workflow,
    input_model: SchemaPack,
    data: DataPack,
    annotation: object = None,
) -> WorkflowResult:
    """Run a workflow end-to-end using the built-in transformation registry.

    Applies the sequence of transformations defined by ``workflow`` to the
    given ``input_model`` and ``data`` and returns the transformed model and
    data. ``annotation`` is forwarded to transformations that need submission
    metadata and may be omitted when no transformation requires it.
    """
    handler: WorkflowHandler = WorkflowHandler(
        workflow=workflow,
        transformation_registry=get_transformation_registry(),
        input_model=input_model,
    )
    return handler.run(data=data, annotation=annotation)
