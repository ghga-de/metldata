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

"""A transformation to add content properties."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_content_properties.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.add_content_properties.config import (
    AddContentPropertiesConfig,
)
from metldata.builtin_transformations.add_content_properties.data_transform import (
    add_properties,
)
from metldata.builtin_transformations.add_content_properties.model_transform import (
    add_content_properties,
)
from metldata.transform.base import (
    DataTransformer,
    TransformationDefinition,
)


class AddContentPropertiesTransformer(DataTransformer[AddContentPropertiesConfig]):
    """A transformer that deletes content properties from data."""

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.
        """
        return add_properties(
            data=data, instructions_by_class=self._config.instructions_by_class()
        )


def check_model_assumptions_wrapper(
    model: SchemaPack,
    config: AddContentPropertiesConfig,
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(
        schema=model, instructions_by_class=config.instructions_by_class()
    )


def transform_model(
    model: SchemaPack, config: AddContentPropertiesConfig
) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return add_content_properties(
        model=model, instructions_by_class=config.instructions_by_class()
    )


ADD_CONTENT_PROPERTIES_TRANSFORMATION = TransformationDefinition[
    AddContentPropertiesConfig
](
    config_cls=AddContentPropertiesConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=AddContentPropertiesTransformer,
)