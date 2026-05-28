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

"""Tests for the public ``validate_workflow`` wrapper.

These exercise the wrapper against the built-in transformation registry,
complementing the unit tests in ``test_workflow_validation.py`` which target
``validate_workflow_against_registry`` with synthetic registries.
"""

import pytest

from metldata import validate_workflow
from metldata.workflow.base import Workflow, WorkflowStep
from metldata.workflow.exceptions import WorkflowValidationError
from tests.fixtures.workflow import WORKFLOW_TEST_CASES, WorkflowTestCase


@pytest.mark.parametrize("test_case", WORKFLOW_TEST_CASES, ids=str)
def test_validate_workflow_accepts_built_in_workflows(test_case: WorkflowTestCase):
    """Every example workflow should validate against the built-in registry."""
    validate_workflow(test_case.workflow)


def test_validate_workflow_rejects_unknown_transformation():
    """An unknown transformation name should raise WorkflowValidationError."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="nonexistent_transform",
                description="References a transformation not in the built-in registry",
                args={"some": "config"},
            )
        ]
    )

    with pytest.raises(
        WorkflowValidationError,
        match="Unknown transformation 'nonexistent_transform'",
    ):
        validate_workflow(workflow)


def test_validate_workflow_rejects_invalid_args_for_built_in_transformation():
    """A built-in transformation referenced with invalid args should be rejected."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="transform_content",
                description="Built-in transformation with invalid args",
                args={"clearly": "wrong"},
            )
        ]
    )

    with pytest.raises(
        WorkflowValidationError,
        match="Invalid configuration for transformation 'transform_content'",
    ):
        validate_workflow(workflow)
