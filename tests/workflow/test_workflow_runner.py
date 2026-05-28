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

"""Tests for the public ``WorkflowRunner`` API.

These verify that ``WorkflowRunner`` preserves the separation between model
and data transformations against the built-in transformation registry,
complementing the ``WorkflowHandler``-level tests in ``test_happy.py``.
"""

import pytest

from metldata import WorkflowRunner
from metldata.workflow.base import Workflow, WorkflowStep
from metldata.workflow.exceptions import WorkflowExecutionError
from tests.fixtures.models import ADVANCED_MODEL
from tests.fixtures.workflow import WORKFLOW_TEST_CASES, WorkflowTestCase
from tests.utils import compare_data, compare_model


def test_workflow_runner_error_identifies_failing_step():
    """WorkflowExecutionError names the correct step index and step name when a step fails."""
    failing_step_index = 1
    failing_step_name = "duplicate_class"

    workflow = Workflow(
        operations=[
            WorkflowStep.model_validate(
                {
                    "name": "rename_id_property",
                    "description": "step 0",
                    "args": {"class_name": "File", "id_property_name": "accession"},
                }
            ),
            WorkflowStep.model_validate(
                {
                    "name": "duplicate_class",
                    "description": "step 1 — invalid: source class does not exist",
                    "args": {
                        "source_class_name": "NonExistentClass",
                        "target_class_name": "FileCopy",
                    },
                }
            ),
            WorkflowStep.model_validate(
                {
                    "name": "delete_class",
                    "description": "step 2",
                    "args": {"class_name": "Dataset"},
                }
            ),
        ]
    )

    with pytest.raises(WorkflowExecutionError) as error:
        WorkflowRunner(workflow=workflow, input_model=ADVANCED_MODEL)

    assert failing_step_index == error.value._step_index
    assert failing_step_name == error.value._step_name


@pytest.mark.parametrize("test_case", WORKFLOW_TEST_CASES, ids=str)
def test_workflow_runner_separates_model_and_data(test_case: WorkflowTestCase):
    """``WorkflowRunner`` should expose the transformed model eagerly and let
    callers run data transformations independently on the same runner.
    """
    assert test_case.transformed_model is not None
    assert test_case.transformed_data is not None

    runner: WorkflowRunner = WorkflowRunner(
        workflow=test_case.workflow, input_model=test_case.input_model
    )

    compare_model(runner.model, test_case.transformed_model)

    transformed_data = runner.run_workflow(
        data=test_case.input_data, annotation=test_case.annotation
    )
    compare_data(transformed_data, test_case.transformed_data)
