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

"""Test the handling module. Only edge cases that are not covered by tests
with builtin transformations are tested here."""

import pytest
import schemapack.exceptions
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.schemapack_.builtin_transformations.null import NULL_TRANSFORMATION
from metldata.schemapack_.builtin_transformations.null.config import NullConfig
from metldata.schemapack_.transform.base import (
    DataTransformer,
    ModelAssumptionError,
    ModelTransformationError,
    TransformationDefinition,
    WorkflowDefinition,
    WorkflowStep,
)
from metldata.schemapack_.transform.handling import (
    TransformationHandler,
    WorkflowHandler,
)
from tests.schemapack_.fixtures.data import INVALID_MINIMAL_DATA, VALID_MINIMAL_DATA
from tests.schemapack_.fixtures.models import VALID_MINIMAL_MODEL


def test_transformation_handler_happy():
    """Test the happy path of using a TransformationHandler."""

    transformation_handler = TransformationHandler(
        transformation_definition=NULL_TRANSFORMATION,
        transformation_config=NullConfig(),
        original_model=VALID_MINIMAL_MODEL,
    )

    # Since the null transformation was used, compare with the input:
    assert transformation_handler.transformed_model == VALID_MINIMAL_MODEL

    transformed_data = transformation_handler.transform_data(VALID_MINIMAL_DATA)

    # Since the null transformation was used, compare with the input:
    assert transformed_data == VALID_MINIMAL_DATA


def test_transformation_handler_assumption_error():
    """Test using the TransformationHandling when model assumptions are not met."""

    # make transformation definition always raise an MetadataModelAssumptionError:
    def always_failing_assumptions(model: SchemaPack, config: NullConfig):
        """A function that always raises a MetadataModelAssumptionError."""
        raise ModelAssumptionError

    transformation = TransformationDefinition[NullConfig](
        config_cls=NULL_TRANSFORMATION.config_cls,
        check_model_assumptions=always_failing_assumptions,
        transform_model=NULL_TRANSFORMATION.transform_model,
        data_transformer_factory=NULL_TRANSFORMATION.data_transformer_factory,
    )

    with pytest.raises(ModelAssumptionError):
        _ = TransformationHandler(
            transformation_definition=transformation,
            transformation_config=NullConfig(),
            original_model=VALID_MINIMAL_MODEL,
        )


def test_transformation_handler_model_transformation_error():
    """Test using the TransformationHandling when model transformation fails."""

    # make transformation definition always raise an ModelAssumptionError:
    def always_failing_transformation(original_model: SchemaPack, config: NullConfig):
        """A function that always raises a ModelTransformationError."""
        raise ModelTransformationError

    transformation = TransformationDefinition[NullConfig](
        config_cls=NULL_TRANSFORMATION.config_cls,
        check_model_assumptions=NULL_TRANSFORMATION.check_model_assumptions,
        transform_model=always_failing_transformation,
        data_transformer_factory=NULL_TRANSFORMATION.data_transformer_factory,
    )
    with pytest.raises(ModelTransformationError):
        _ = TransformationHandler(
            transformation_definition=transformation,
            transformation_config=NullConfig(),
            original_model=VALID_MINIMAL_MODEL,
        )


def test_transformation_handler_input_data_invalid():
    """Test the TransformationHandler when used with input data that is not valid
    against the model."""

    transformation_handler = TransformationHandler(
        transformation_definition=NULL_TRANSFORMATION,
        transformation_config=NullConfig(),
        original_model=VALID_MINIMAL_MODEL,
    )

    with pytest.raises(schemapack.exceptions.ValidationError):
        _ = transformation_handler.transform_data(INVALID_MINIMAL_DATA)


def test_transformation_handler_transformed_data_invalid():
    """Test the TransformationHandler when the transformed data fails validation
    against the transformed model."""

    class AlwaysInvalidTransformer(DataTransformer[NullConfig]):
        """A transformer that always returns the same invalid data."""

        def transform(self, data: DataPack) -> DataPack:
            """Transforms data.

            Args:
                data: The data as DataPack to be transformed.

            Raises:
                DataTransformationError:
                    if the transformation fails.
            """
            return INVALID_MINIMAL_DATA

    transformation = TransformationDefinition[NullConfig](
        config_cls=NULL_TRANSFORMATION.config_cls,
        check_model_assumptions=NULL_TRANSFORMATION.check_model_assumptions,
        transform_model=NULL_TRANSFORMATION.transform_model,
        data_transformer_factory=AlwaysInvalidTransformer,
    )

    transformation_handler = TransformationHandler(
        transformation_definition=transformation,
        transformation_config=NullConfig(),
        original_model=VALID_MINIMAL_MODEL,
    )

    with pytest.raises(schemapack.exceptions.ValidationError):
        _ = transformation_handler.transform_data(VALID_MINIMAL_DATA)


def test_workflow_handler_happy():
    """Test the happy path of using a WorkflowHandler."""
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

    workflow_handler = WorkflowHandler(
        workflow_definition=null_workflow,
        workflow_config=null_workflow.config_cls.model_validate(
            {"step1": {}, "step2": {}}
        ),
        original_model=VALID_MINIMAL_MODEL,
    )

    artifacts = workflow_handler.run(data=VALID_MINIMAL_DATA)

    # Since a null workflow was used, compare to the input:
    assert artifacts["step1_output"] == artifacts["step2_output"] == VALID_MINIMAL_DATA
