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

"""Test the workflow execution using pre-defined test cases."""

from tests.fixtures.data import ADVANCED_DATA


def test_workflow_outputs(
    workflow_handler,
    expected_workflow_output_data,
    expected_workflow_output_model,
):
    """Test the data created after workflow execution."""
    workflow_result = workflow_handler.run(data=ADVANCED_DATA)
    assert workflow_result.data == expected_workflow_output_data
    assert workflow_result.model == expected_workflow_output_model
