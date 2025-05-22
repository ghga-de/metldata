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

from pathlib import Path

from schemapack import load_datapack, load_schemapack

from metldata.builtin_transformations.delete_class.main import (
    DELETE_CLASS_TRANSFORMATION,
)
from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.data import ADVANCED_DATA
from tests.fixtures.models import ADVANCED_MODEL
from tests.fixtures.workflow_templates import SIMPLE_WORKFLOW

TRANSFORMATION_REGISTRY = {"delete_class": DELETE_CLASS_TRANSFORMATION}
MODEL_REGISTRY = Path("/workspace/tests/fixtures/example_models")


def test_workflow_outputs():
    """Test the data created after workflow execution."""
    expected_workflow_output_data = load_datapack(
        Path("/workspace/tests/fixtures/example_workflows/transformed.datapack.yaml")
    )
    expected_workflow_output_model = load_schemapack(
        Path("/workspace/tests/fixtures/example_workflows/transformed.schemapack.yaml")
    )

    workflow_result = WorkflowHandler(
        workflow=SIMPLE_WORKFLOW,
        model_registry=MODEL_REGISTRY,
        transformation_registry=TRANSFORMATION_REGISTRY,
    ).run(data=ADVANCED_DATA)

    assert workflow_result.data == expected_workflow_output_data
    assert workflow_result.model == expected_workflow_output_model
