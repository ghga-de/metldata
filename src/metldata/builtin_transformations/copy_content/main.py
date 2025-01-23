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

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.copy_content.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.copy_content.config import CopyContentConfig
from metldata.builtin_transformations.copy_content.data_transform import copy_content
from metldata.builtin_transformations.copy_content.model_transform import (
    add_content_schema_copy,
)
from metldata.transform.base import DataTransformer, TransformationDefinition


class CopyContentTransformer(DataTransformer[CopyContentConfig]):
    """A transformer that counts the occurrences of a specified property within an object and
    adds the value to the content of a target object.
    """

    def transform(self, data: DataPack) -> DataPack:  # type: ignore
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.
        """
        return copy_content(
            data=data, instructions_by_class=self._config.instructions_by_class()
        )


def check_model_assumptions_wrapper(
    model: SchemaPack, config: CopyContentConfig
) -> None:
    """Check all assumptions hold for a given model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill all assumptions.
    """
    check_model_assumptions(
        schema=model, instructions_by_class=config.instructions_by_class()
    )


def transform_model(model: SchemaPack, config: CopyContentConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return add_content_schema_copy(
        model=model, instructions_by_class=config.instructions_by_class()
    )


COUNT_CONTENT_VALUES_TRANSFORMATION = TransformationDefinition[CopyContentConfig](
    config_cls=CopyContentConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=CopyContentTransformer,
)
