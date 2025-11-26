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
from pydantic import BaseModel
from schemapack import load_datapack, load_schemapack
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations import (
    DELETE_CLASS_TRANSFORMATION,
    DUPLICATE_CLASS_TRANSFORMATION,
)
from metldata.builtin_transformations.infer_relation.main import (
    INFER_RELATION_TRANSFORMATION,
)
from metldata.builtin_transformations.merge_relations.main import (
    MERGE_RELATIONS_TRANSFORMATION,
)
from metldata.builtin_transformations.rename_id_property.main import (
    RENAME_ID_PROPERTY_TRANSFORMATION,
)
from metldata.builtin_transformations.replace_resource_ids.main import (
    REPLACE_RESOURCE_IDS_TRANSFORMATION,
)
from metldata.builtin_transformations.transform_content.main import (
    TRANSFORM_CONTENT_TRANSFORMATION,
)
from metldata.workflow.base import Workflow, WorkflowTemplate
from metldata.workflow.builder import WorkflowBuilder
from tests.fixtures.annotation import AccessionAnnotation, EmptySubmissionAnnotation
from tests.fixtures.data import ADVANCED_DATA
from tests.fixtures.models import ADVANCED_MODEL
from tests.fixtures.utils import BASE_DIR, read_yaml

EXAMPLE_WORKFLOW_DIR = BASE_DIR / "example_workflows"
WORKFLOW_VALIDATION_DIR = BASE_DIR / "workflow_validation"
WORKFLOW_BY_NAME = [
    "add_multiple_content_properties",
    "count_references",
    "duplicate_one_delete_multiple",
    "duplicate_multiple_delete_one",
    "delete_multiple",
    "infer_multiple",
    "duplicate_multiple_delete_one_embed_relation",
    "duplicate_infer_delete_merge",
    "rename_id_property_multiple",
    "rename_id_property_transform_content_update_resource_ids",
    "ghga_aggregation_workflow",
]
VALIDATION_WORKFLOWS = ["invalid_input_model", "invalid_output_model"]
TRANSFORMATION_REGISTRY = {
    "delete_class": DELETE_CLASS_TRANSFORMATION,
    "duplicate_class": DUPLICATE_CLASS_TRANSFORMATION,
    "infer_relation": INFER_RELATION_TRANSFORMATION,
    "merge_relations": MERGE_RELATIONS_TRANSFORMATION,
    "transform_content": TRANSFORM_CONTENT_TRANSFORMATION,
    "rename_id_property": RENAME_ID_PROPERTY_TRANSFORMATION,
    "replace_resource_ids": REPLACE_RESOURCE_IDS_TRANSFORMATION,
}


@dataclass(frozen=False)
class WorkflowTestCase:
    """A test case for a workflow."""

    case_name: str
    workflow: Workflow
    input_model: SchemaPack
    input_data: DataPack
    transformed_model: SchemaPack | None
    transformed_data: DataPack | None
    annotation: BaseModel
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
    *, workflow_dir: Path, case_name: str, load_transformed: bool = True
) -> WorkflowTestCase:
    """Read a test case for a workflow."""
    case_dir = workflow_dir / case_name
    workflow_path = case_dir / "workflow.yaml"
    input_model_path = case_dir / "input.schemapack.yaml"
    input_data_path = case_dir / "input.datapack.yaml"
    transformed_model_path = case_dir / "transformed.schemapack.yaml"
    transformed_data_path = case_dir / "transformed.datapack.yaml"
    annotation_path = case_dir / "annotation.yaml"

    input_model = (
        load_schemapack(input_model_path)
        if input_model_path.exists()
        else ADVANCED_MODEL
    )
    input_data = (
        load_datapack(input_data_path) if input_data_path.exists() else ADVANCED_DATA
    )

    transformed_model = (
        load_schemapack(transformed_model_path) if load_transformed else None
    )
    transformed_data = (
        load_datapack(transformed_data_path) if load_transformed else None
    )
    workflow = _get_workflow(workflow_path)
    annotation = (
        AccessionAnnotation(**read_yaml(annotation_path))
        if annotation_path.exists()
        else EmptySubmissionAnnotation()
    )

    return WorkflowTestCase(
        case_name=case_name,
        workflow=workflow,
        input_model=input_model,
        input_data=input_data,
        transformed_model=transformed_model,
        transformed_data=transformed_data,
        annotation=annotation,
    )


def _read_validation_test_cases() -> list[WorkflowTestCase]:
    """Read validation test cases."""
    return [
        _read_test_case(
            workflow_dir=WORKFLOW_VALIDATION_DIR,
            case_name=case_name,
            load_transformed=False,
        )
        for case_name in VALIDATION_WORKFLOWS
    ]


def _read_all_test_cases() -> list[WorkflowTestCase]:
    """Read all test cases for a workflow execution."""
    return [
        _read_test_case(workflow_dir=EXAMPLE_WORKFLOW_DIR, case_name=case_name)
        for case_name in WORKFLOW_BY_NAME
    ]


WORKFLOW_TEST_CASES = _read_all_test_cases()
VALIDATION_TEST_CASES = _read_validation_test_cases()
