# Copyright 2021 - 2024 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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
#

"""Test the builtin transformations using pre-defined test cases."""

import pytest

from metldata.transform.handling import TransformationHandler
from tests.fixtures.transformations import (
    TRANSFORMATION_TEST_CASES,
    TransformationTestCase,
)


@pytest.mark.parametrize(
    "test_case",
    TRANSFORMATION_TEST_CASES,
    ids=str,
)
def test_model_transformations(
    test_case: TransformationTestCase,
):
    """Test the happy path of transforming a model."""
    handler = TransformationHandler(
        transformation_definition=test_case.transformation_definition,
        transformation_config=test_case.config,
        input_model=test_case.input_model,
    )
    transformed_model = handler.transformed_model

    assert transformed_model == test_case.transformed_model


@pytest.mark.parametrize("test_case", TRANSFORMATION_TEST_CASES, ids=str)
def test_data_transformations(
    test_case: TransformationTestCase,
):
    """Test the happy path of transforming data for a model."""
    handler = TransformationHandler(
        transformation_definition=test_case.transformation_definition,
        transformation_config=test_case.config,
        input_model=test_case.input_model,
    )
    transformed_data = handler.transform_data(test_case.input_data)

    assert transformed_data == test_case.transformed_data
