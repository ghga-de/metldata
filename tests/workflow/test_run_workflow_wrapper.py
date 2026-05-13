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

"""Tests for the public ``run_workflow`` wrapper.

These verify that the wrapper composes ``WorkflowHandler`` construction and
``run`` correctly against the built-in transformation registry, complementing
the ``WorkflowHandler``-level tests in ``test_happy.py``.
"""

import pytest

from metldata import run_workflow
from tests.fixtures.workflow import WORKFLOW_TEST_CASES, WorkflowTestCase
from tests.utils import compare_data, compare_model


@pytest.mark.parametrize("test_case", WORKFLOW_TEST_CASES, ids=str)
def test_run_workflow_matches_expected_outputs(test_case: WorkflowTestCase):
    """``run_workflow`` should produce the expected transformed model and data."""
    if test_case.transformed_model is None or test_case.transformed_data is None:
        raise ValueError(
            f"Missing expected outputs for test case: {test_case.case_name}"
        )

    result = run_workflow(
        workflow=test_case.workflow,
        input_model=test_case.input_model,
        data=test_case.input_data,
        annotation=test_case.annotation,
    )

    compare_model(result.model, test_case.transformed_model)
    compare_data(result.data, test_case.transformed_data)
