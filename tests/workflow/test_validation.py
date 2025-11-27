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

from unittest.mock import patch

import pytest
from schemapack.spec.schemapack import SchemaPack

from metldata.transform.base import Config, TransformationDefinition
from metldata.transform.exceptions import (
    PostTransformValidationError,
    PreTransformValidationError,
)
from metldata.transform.handling import NoOpValidator, TransformationHandler
from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.workflow import VALIDATION_TEST_CASES, WorkflowTestCase


def constructor_intercept(
    self,
    transformation_definition: TransformationDefinition[Config],
    transformation_config: Config,
    input_model: SchemaPack,
    validate_input: bool = False,
    validate_output: bool = False,
):
    pass


@pytest.mark.parametrize("test_case", VALIDATION_TEST_CASES, ids=str)
def test_workflow_invalid_models(test_case: WorkflowTestCase):
    """Test validation using an invalid input, intermediate or output model."""
    # patch("metldata.transform.handling.TransformationHandler.__init__", constructor_intercept)

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
        _ = handler.run(data=test_case.input_data, annotation=test_case.annotation)
