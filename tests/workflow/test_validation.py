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

from metldata.transform.exceptions import (
    PostTransformValidationError,
    PreTransformValidationError,
)
from metldata.transform.handling import TransformationHandler
from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.workflow import VALIDATION_TEST_CASES, WorkflowTestCase

EXPECTED_CALL_ARGS = {
    "invalid_input_model": [{"validate_input": True, "validate_output": False}],
    "invalid_intermediate_model": [
        {"validate_input": True, "validate_output": False},
        {"validate_input": False, "validate_output": False},
        {"validate_input": False, "validate_output": True},
    ],
    "invalid_single_step_model": [{"validate_input": True, "validate_output": True}],
    "invalid_output_model": [
        {"validate_input": True, "validate_output": False},
        {"validate_input": False, "validate_output": False},
        {"validate_input": False, "validate_output": True},
    ],
}


class CapturedContext:
    """Container to store results from capture_constructor_args"""

    def __init__(self):
        self.call_args = []


@pytest.fixture()
def capture_constructor_args():
    """Intercepts TransformationHandler constructor to capture call args.

    Allows to check in which order and with which values the TransformationHandler was instantiated.
    """
    context = CapturedContext()

    def capture(self, *args, **kwargs):
        context.call_args.append(
            {
                "validate_input": kwargs["validate_input"],
                "validate_output": kwargs["validate_output"],
            }
        )
        self._real_init(*args, **kwargs)

    TransformationHandler._real_init = TransformationHandler.__init__  # type: ignore
    TransformationHandler.__init__ = capture  # type: ignore

    yield context

    TransformationHandler.__init__ = TransformationHandler._real_init  # type: ignore
    del TransformationHandler._real_init  # type: ignore


@pytest.mark.parametrize("test_case", VALIDATION_TEST_CASES, ids=str)
def test_workflow_invalid_models(test_case: WorkflowTestCase, capture_constructor_args):
    """Test validation using an invalid input, intermediate or output model."""
    handler: WorkflowHandler = WorkflowHandler(
        workflow=test_case.workflow,
        transformation_registry=test_case.transformation_registry,
        input_model=test_case.input_model,
    )
    exception_type = (
        PreTransformValidationError
        if test_case.case_name == "invalid_input_model"
        else PostTransformValidationError
    )
    with pytest.raises(exception_type):
        handler.run(data=test_case.input_data, annotation=test_case.annotation)

    assert capture_constructor_args.call_args == EXPECTED_CALL_ARGS[test_case.case_name]
