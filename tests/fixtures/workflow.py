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

from pathlib import Path

import pytest
import yaml
from schemapack import load_datapack, load_schemapack

from metldata.builtin_transformations.delete_class.main import (
    DELETE_CLASS_TRANSFORMATION,
)
from metldata.workflow.base import WorkflowTemplate
from metldata.workflow.builder import WorkflowBuilder
from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.utils import BASE_DIR

EXAMPLE_WORKFLOW_DIR = BASE_DIR / "example_workflows"
TRANSFORMATION_REGISTRY = {"delete_class": DELETE_CLASS_TRANSFORMATION}
MODEL_REGISTRY = Path("/workspace/tests/fixtures/example_models")


def _get_example_workflow(name: str) -> WorkflowTemplate:
    """Get example workflow from a YAML file."""
    with open(EXAMPLE_WORKFLOW_DIR / f"{name}.workflow.yaml") as file:
        workflow_template = yaml.safe_load(file)
    return WorkflowTemplate.model_validate(workflow_template)


SIMPLE_TEMPLATE = _get_example_workflow("simple")
SIMPLE_WORKFLOW = WorkflowBuilder(template=SIMPLE_TEMPLATE).build()


@pytest.fixture
def expected_workflow_output_data():
    """Fixture that loads and returns the expected workflow output data
    from a datapack YAML file.
    """
    return load_datapack(
        Path("/workspace/tests/fixtures/example_workflows/transformed.datapack.yaml")
    )


@pytest.fixture
def expected_workflow_output_model():
    """Fixture that loads and returns the expected workflow output model
    from a schemapack YAML file.
    """
    return load_schemapack(
        Path("/workspace/tests/fixtures/example_workflows/transformed.schemapack.yaml")
    )


@pytest.fixture
def workflow_handler():
    """Fixture that creates and returns a WorkflowHandler instance
    with a simple workflow and the necessary registries.
    """
    return WorkflowHandler(
        workflow=SIMPLE_WORKFLOW,
        model_registry=MODEL_REGISTRY,
        transformation_registry=TRANSFORMATION_REGISTRY,
    )
