# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Test the base module."""


import pytest
from pydantic import ValidationError

from metldata.schemapack_.builtin_transformations.null import NULL_TRANSFORMATION
from metldata.schemapack_.transform.base import (
    WorkflowDefinition,
    WorkflowStep,
)


def test_workflow_definition_invalid_step_refs():
    """Test that an invalid step reference raises an error."""
    with pytest.raises(ValidationError):
        WorkflowDefinition(
            description="A workflow for testing.",
            steps={
                "step1": WorkflowStep(
                    description="A dummy step.",
                    transformation_definition=NULL_TRANSFORMATION,
                    input=None,
                ),
                "step2": WorkflowStep(
                    description="Another dummy step.",
                    transformation_definition=NULL_TRANSFORMATION,
                    input="non_existing_step",
                ),
            },
            artifacts={
                "step1_output": "step1",
                "step2_output": "step2",
            },
        )


def test_workflow_definition_invalid_multiple_first_steps():
    """Test that specifying multiple steps without input raises an exception."""
    with pytest.raises(ValidationError):
        WorkflowDefinition(
            description="A workflow for testing.",
            steps={
                "step1": WorkflowStep(
                    description="A dummy step.",
                    transformation_definition=NULL_TRANSFORMATION,
                    input=None,
                ),
                "step2": WorkflowStep(
                    description="Another dummy step.",
                    transformation_definition=NULL_TRANSFORMATION,
                    input=None,
                ),
            },
            artifacts={
                "step1_output": "step1",
                "step2_output": "step2",
            },
        )


def test_workflow_definition_invalid_artifacts():
    """Test that artifacts referencing non-existing steps raise an exception."""
    with pytest.raises(ValidationError):
        WorkflowDefinition(
            description="A workflow for testing.",
            steps={
                "step1": WorkflowStep(
                    description="A dummy step.",
                    transformation_definition=NULL_TRANSFORMATION,
                    input=None,
                ),
                "step2": WorkflowStep(
                    description="Another dummy step.",
                    transformation_definition=NULL_TRANSFORMATION,
                    input="step1",
                ),
            },
            artifacts={
                "step1_output": "non_existing_step",
                "step2_output": "step2",
            },
        )


def test_workflow_definition_step_order_happy():
    """Test that the step order is correctly inferred from the workflow definition."""

    workflow_definition = WorkflowDefinition(
        description="A workflow for testing.",
        steps={
            "step3": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step2",
            ),
            "step2": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step1",
            ),
            "step1": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input=None,
            ),
            "step4": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step2",
            ),
        },
        artifacts={
            "output3": "step3",
            "output4": "step4",
        },
    )

    assert workflow_definition.step_order in (
        [
            "step1",
            "step2",
            "step3",
            "step4",
        ],
        [
            "step1",
            "step2",
            "step4",
            "step3",
        ],
    )


def test_workflow_definition_step_order_circular():
    """Test that initialization of a WorkflowDefinition with a circularly dependent
    steps fails."""

    workflow_definition = WorkflowDefinition(
        description="A workflow for testing.",
        steps={
            "step1": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input=None,
            ),
            "step2": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step4",
            ),
            "step3": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step2",
            ),
            "step4": WorkflowStep(
                description="A test step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step3",
            ),
        },
        artifacts={
            "output3": "step3",
            "output4": "step4",
        },
    )

    with pytest.raises(RuntimeError):
        _ = workflow_definition.step_order


def test_workflow_definition_config_cls():
    """Test that the config_cls of the WorkflowDefinition generates a concatenated
    config class correctly."""

    null_workflow = WorkflowDefinition(
        description="A workflow for testing.",
        steps={
            "step1": WorkflowStep(
                description="A dummy step.",
                transformation_definition=NULL_TRANSFORMATION,
                input=None,
            ),
            "step2": WorkflowStep(
                description="Another dummy step.",
                transformation_definition=NULL_TRANSFORMATION,
                input="step1",
            ),
        },
        artifacts={
            "step1_output": "step1",
            "step2_output": "step2",
        },
    )

    config_fields = null_workflow.config_cls.model_fields

    assert "step1" in config_fields
    assert "step2" in config_fields
    assert (
        config_fields["step1"].annotation
        == config_fields["step2"].annotation
        == NULL_TRANSFORMATION.config_cls
    )
