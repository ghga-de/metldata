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

"""Tests for validate_workflow_against_registry function."""

import pytest
from pydantic import BaseModel, Field
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.transform.base import DataTransformer, TransformationDefinition
from metldata.workflow.base import Workflow, WorkflowStep
from metldata.workflow.exceptions import WorkflowValidationError
from metldata.workflow.validate import validate_workflow_against_registry


# Test configuration classes
class SimpleConfig(BaseModel):
    """A simple config for testing."""

    name: str = Field(..., description="A name field")
    value: int = Field(..., description="A value field")


class AnotherConfig(BaseModel):
    """Another config for testing."""

    field_a: str = Field(..., description="Field A")
    field_b: bool = Field(default=True, description="Field B")


class ComplexConfig(BaseModel):
    """A more complex config for testing."""

    required_field: str = Field(..., description="Required field")
    optional_field: str = Field(default="default", description="Optional field")
    number_field: int = Field(default=42, description="Number field")


# Mock functions for transformation definitions
def dummy_check_model_assumptions(model: SchemaPack, config: BaseModel) -> None:
    """Mock function for checking model assumptions."""
    pass


def dummy_transform_model(model: SchemaPack, config: BaseModel) -> SchemaPack:
    """Mock function for transforming models."""
    return model


# Mock classes for transformation definitions
class DummyDataTransformer(DataTransformer):
    """Mock data transformer for testing."""

    def transform(self, data: DataPack, annotation: BaseModel) -> DataPack:
        """Mock transform method."""
        return data


# Test fixtures
@pytest.fixture
def simple_transformation():
    """Create a simple transformation definition."""
    return TransformationDefinition(
        config_cls=SimpleConfig,
        check_model_assumptions=dummy_check_model_assumptions,
        transform_model=dummy_transform_model,
        data_transformer_factory=DummyDataTransformer,
    )


@pytest.fixture
def another_transformation():
    """Create another transformation definition."""
    return TransformationDefinition(
        config_cls=AnotherConfig,
        check_model_assumptions=dummy_check_model_assumptions,
        transform_model=dummy_transform_model,
        data_transformer_factory=DummyDataTransformer,
    )


@pytest.fixture
def complex_transformation():
    """Create a complex transformation definition."""
    return TransformationDefinition(
        config_cls=ComplexConfig,
        check_model_assumptions=dummy_check_model_assumptions,
        transform_model=dummy_transform_model,
        data_transformer_factory=DummyDataTransformer,
    )


@pytest.fixture
def transformation_registry(
    simple_transformation: TransformationDefinition,
    another_transformation: TransformationDefinition,
    complex_transformation: TransformationDefinition,
):
    """Create a transformation registry with test transformations."""
    return {
        "simple_transform": simple_transformation,
        "another_transform": another_transformation,
        "complex_transform": complex_transformation,
    }


def test_valid_workflow_single_operation(
    transformation_registry: dict[str, TransformationDefinition],
):
    """Test validation succeeds for a valid workflow with a single operation."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="simple_transform",
                description="A simple transformation",
                args=SimpleConfig(name="test", value=123),
            )
        ]
    )

    validate_workflow_against_registry(workflow, transformation_registry)


def test_valid_workflow_multiple_operations(
    transformation_registry: dict[str, TransformationDefinition],
):
    """Test validation succeeds for a valid workflow with multiple operations."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="simple_transform",
                description="First transformation",
                args=SimpleConfig(name="first", value=1),
            ),
            WorkflowStep(
                name="another_transform",
                description="Second transformation",
                args=AnotherConfig(field_a="test", field_b=False),
            ),
            WorkflowStep(
                name="complex_transform",
                description="Third transformation",
                args=ComplexConfig(required_field="required"),
            ),
        ]
    )

    validate_workflow_against_registry(workflow, transformation_registry)


def test_valid_workflow_with_dict_args(
    transformation_registry: dict[str, TransformationDefinition],
):
    """Test validation succeeds when args are provided as a dict (not config instance)."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="simple_transform",
                description="A simple transformation",
                args={"name": "test", "value": 123},
            )
        ]
    )

    validate_workflow_against_registry(workflow, transformation_registry)


def test_config_with_optional_fields_omitted(
    transformation_registry: dict[str, TransformationDefinition],
):
    """Test validation succeeds when optional fields are omitted."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="complex_transform",
                description="Only required field provided",
                args={"required_field": "value"},
                # optional_field and number_field will use defaults
            )
        ]
    )

    validate_workflow_against_registry(workflow, transformation_registry)


def test_unknown_transformation_name(
    transformation_registry: dict[str, TransformationDefinition],
):
    """Test validation fails when workflow references an unknown transformation."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="nonexistent_transform",
                description="Unknown transformation",
                args={"some": "config"},
            )
        ]
    )

    with pytest.raises(
        WorkflowValidationError,
        match="Unknown transformation 'nonexistent_transform' referenced in workflow",
    ):
        validate_workflow_against_registry(workflow, transformation_registry)


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(
            {"name": "test"},
            id="missing_required_field",
        ),
        pytest.param(
            {"name": "test", "value": "not_an_int"},
            id="wrong_field_type",
        ),
        pytest.param(
            {"completely": "wrong", "structure": "here"},
            id="wrong_structure",
        ),
    ],
)
def test_invalid_simple_config(
    args: dict, transformation_registry: dict[str, TransformationDefinition]
):
    """Test validation fails when config for simple_transform is invalid."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="simple_transform",
                description="Invalid config",
                args=args,
            )
        ]
    )

    with pytest.raises(
        WorkflowValidationError,
        match="Invalid configuration for transformation 'simple_transform'",
    ):
        validate_workflow_against_registry(workflow, transformation_registry)


def test_invalid_operation(
    transformation_registry: dict[str, TransformationDefinition],
):
    """Test validation fails on an invalid operation."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="simple_transform",
                description="Valid first operation",
                args=SimpleConfig(name="test", value=123),
            ),
            WorkflowStep(
                name="nonexistent_transform",
                description="Invalid second operation",
                args={"some": "config"},
            ),
        ]
    )

    with pytest.raises(
        WorkflowValidationError,
        match="Unknown transformation 'nonexistent_transform' referenced in workflow",
    ):
        validate_workflow_against_registry(workflow, transformation_registry)


def test_empty_transformation_registry():
    """Test validation fails when transformation registry is empty."""
    workflow = Workflow(
        operations=[
            WorkflowStep(
                name="any_transform",
                description="Any transformation",
                args={"some": "config"},
            )
        ]
    )

    with pytest.raises(
        WorkflowValidationError, match="Transformation registry cannot be empty"
    ):
        validate_workflow_against_registry(workflow, {})
