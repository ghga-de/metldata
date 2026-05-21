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


"""Test the workflow handling module."""

from unittest.mock import patch

import pytest

from metldata.transform.exceptions import ModelAssumptionError
from metldata.transform.handling import TransformationHandler
from metldata.workflow.exceptions import WorkflowExecutionError
from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.workflow import WORKFLOW_TEST_CASES


def test_run_raises_workflow_execution_error_on_transform_failure():
    """WorkflowExecutionError is raised when transform_data fails."""
    test_case = WORKFLOW_TEST_CASES[0]
    handler: WorkflowHandler = WorkflowHandler(
        workflow=test_case.workflow,
        transformation_registry=test_case.transformation_registry,
        input_model=test_case.input_model,
    )
    with patch.object(
        TransformationHandler,
        "transform_data",
        side_effect=ModelAssumptionError("Error"),
    ):
        with pytest.raises(WorkflowExecutionError):
            handler.run(data=test_case.input_data, annotation=test_case.annotation)


def test_workflow_handler_input_model_invalid():
    """Test."""
    # test if the correct error message is returned if the workflow input model is not supported
    pass


# test to implement if we keep an output model registry, like supported egress models.
def test_output_data_against_workflow_output_model():
    """Test."""
    # test if the correct error message is returned when the data at the end of the
    # workflow execution fails to match the workflow output model
    pass
