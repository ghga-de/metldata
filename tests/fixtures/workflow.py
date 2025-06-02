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

"""Example workflow templates."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from schemapack import load_datapack, load_schemapack
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations import (
    DELETE_CLASS_TRANSFORMATION,
    DUPLICATE_CLASS_TRANSFORMATION,
)
from metldata.workflow.base import Workflow, WorkflowTemplate
from metldata.workflow.builder import WorkflowBuilder
from tests.fixtures.data import ADVANCED_DATA
from tests.fixtures.models import ADVANCED_MODEL
from tests.fixtures.utils import BASE_DIR

EXAMPLE_WORKFLOW_DIR = BASE_DIR / "example_workflows"
WORKFLOW_BY_NAME: list[str] = ["duplicate_and_delete", "simple_workflow"]
TRANSFORMATION_REGISTRY = {
    "delete_class": DELETE_CLASS_TRANSFORMATION,
    "duplicate_class": DUPLICATE_CLASS_TRANSFORMATION,
}


@dataclass(frozen=False)
class WorkflowTestCase:
    """A test case for a workflow."""

    case_name: str
    workflow: Workflow
    input_model: SchemaPack
    input_data: DataPack
    transformed_model: SchemaPack
    transformed_data: DataPack
    transformation_registry: dict[str, Any] = field(
        default_factory=lambda: TRANSFORMATION_REGISTRY
    )

    def __str__(self) -> str:  # noqa: D105
        return f"{self.case_name}"


def _get_workflow(workflow_path: Path) -> Workflow:
    """Get example workflow from a YAML file."""
    with open(workflow_path) as file:
        workflow_template = yaml.safe_load(file)
    template = WorkflowTemplate.model_validate(workflow_template)
    return WorkflowBuilder(template=template).build()


def _read_test_case(
    *,
    case_name: str,
) -> WorkflowTestCase:
    """Read a test case for a workflow."""
    case_dir = EXAMPLE_WORKFLOW_DIR / case_name
    workflow_path = case_dir / "workflow.yaml"
    input_model_path = case_dir / "input.schemapack.yaml"
    input_data_path = case_dir / "input.datapack.yaml"
    transformed_model_path = case_dir / "transformed.schemapack.yaml"
    transformed_data_path = case_dir / "transformed.datapack.yaml"

    input_model = (
        load_schemapack(input_model_path)
        if input_model_path.exists()
        else ADVANCED_MODEL
    )
    input_data = (
        load_datapack(input_data_path) if input_data_path.exists() else ADVANCED_DATA
    )
    transformed_model = load_schemapack(transformed_model_path)
    transformed_data = load_datapack(transformed_data_path)
    workflow = _get_workflow(workflow_path)

    return WorkflowTestCase(
        case_name=case_name,
        workflow=workflow,
        input_model=input_model,
        input_data=input_data,
        transformed_model=transformed_model,
        transformed_data=transformed_data,
    )


def _read_all_test_cases() -> list[WorkflowTestCase]:
    """Read all test cases for a workflow execution."""
    return [_read_test_case(case_name=case_name) for case_name in WORKFLOW_BY_NAME]


WORKFLOW_TEST_CASES = _read_all_test_cases()
