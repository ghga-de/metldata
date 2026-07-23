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
from arcticfreeze import FrozenDict
from schemapack.spec.datapack import DataPack

from metldata.transform.exceptions import DataTransformationError
from metldata.transform.handling import TransformationHandler
from metldata.workflow.exceptions import (
    DataPackModelValidationError,
    WorkflowExecutionError,
)
from metldata.workflow.handling import WorkflowHandler
from tests.fixtures.workflow import WORKFLOW_TEST_CASES


def _datapack_with_dangling_reference() -> DataPack:
    """Build a datapack whose relation targets a non-existent resource id.

    The dangling reference is introduced with ``model_copy`` so it bypasses DataPack
    model validation, mimicking how the builtin transformations construct datapacks via
    structural sharing. ``SchemaPackValidator`` does not catch this; only DataPack model
    validation does.
    """
    valid = DataPack.model_validate(
        {
            "datapack": "4.2.0",
            "resources": {
                "Sample": {"sample_x": {"content": {}}},
                "Dataset": {
                    "dataset_1": {
                        "content": {},
                        "relations": {
                            "sample": {
                                "targetClass": "Sample",
                                "targetResources": "sample_x",
                            }
                        },
                    }
                },
            },
        }
    )
    dataset = valid.resources["Dataset"]["dataset_1"]
    dangling = dataset.relations["sample"].model_copy(
        update={"targetResources": "DOES_NOT_EXIST"}
    )
    broken_dataset = dataset.model_copy(
        update={"relations": FrozenDict({"sample": dangling})}
    )
    return valid.model_copy(
        update={
            "resources": FrozenDict(
                {
                    **valid.resources,
                    "Dataset": FrozenDict({"dataset_1": broken_dataset}),
                }
            )
        }
    )


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
        side_effect=DataTransformationError("Error"),
    ):
        with pytest.raises(WorkflowExecutionError):
            handler.run(data=test_case.input_data, annotation=test_case.annotation)


def test_run_revalidates_final_datapack_through_datapack_model():
    """The final datapack is re-validated through the DataPack model.

    A referentially broken result (a relation targeting a non-existent resource) is
    caught even though ``SchemaPackValidator`` does not check referential integrity, and
    surfaces as a ``WorkflowExecutionError`` wrapping a ``DataPackModelValidationError``.
    """
    test_case = WORKFLOW_TEST_CASES[0]
    handler: WorkflowHandler = WorkflowHandler(
        workflow=test_case.workflow,
        transformation_registry=test_case.transformation_registry,
        input_model=test_case.input_model,
    )
    corrupt = _datapack_with_dangling_reference()
    with patch.object(TransformationHandler, "transform_data", return_value=corrupt):
        with pytest.raises(WorkflowExecutionError) as exc_info:
            handler.run(data=test_case.input_data, annotation=test_case.annotation)

    assert isinstance(exc_info.value.error, DataPackModelValidationError)
