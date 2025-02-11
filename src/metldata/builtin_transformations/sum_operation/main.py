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

"""A transformation to sum up the values of content properties."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.sum_operation.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.sum_operation.config import SumOperationConfig
from metldata.builtin_transformations.sum_operation.data_transform import (
    sum_content,
)
from metldata.builtin_transformations.sum_operation.model_transform import (
    add_sum_content_properties,
)
from metldata.transform.base import DataTransformer, TransformationDefinition


class SumOperationDataTransformer(DataTransformer[SumOperationConfig]):
    """A transformer that sums the values of a specified property within an object and
    adds them to the content of a target object.
    """

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.
        """
        return sum_content(
            data=data, instructions_by_class=self._config.instructions_by_class
        )


def check_model_assumptions_wrapper(
    model: SchemaPack, config: SumOperationConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(
        schema=model, instructions_by_class=config.instructions_by_class
    )


def transform_model(model: SchemaPack, config: SumOperationConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return add_sum_content_properties(
        model=model, instructions_by_class=config.instructions_by_class
    )


SUM_OPERATION_TRANSFORMATION = TransformationDefinition[SumOperationConfig](
    config_cls=SumOperationConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=SumOperationDataTransformer,
)
