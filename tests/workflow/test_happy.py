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

"""Test workflow execution using pre-defined test cases."""

import pytest

from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.workflow import WORKFLOW_TEST_CASES, WorkflowTestCase


@pytest.mark.parametrize("workflow_case", WORKFLOW_TEST_CASES, ids=str)
def test_workflow_outputs(workflow_case: WorkflowTestCase):
    """Test the happy path of running a workflow."""
    workflow_result = WorkflowHandler(
        workflow=workflow_case.workflow,
        model_registry=workflow_case.model_registry,
        transformation_registry=workflow_case.transformation_registry,
    ).run(data=workflow_case.input_data)
    assert workflow_result.data == workflow_case.transformed_data
    assert workflow_result.model == workflow_case.transformed_model
