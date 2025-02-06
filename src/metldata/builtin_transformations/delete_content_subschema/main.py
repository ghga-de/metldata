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

"""A transformation to delete content properties."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.delete_content_subschema.assumptions import (
    assert_classes_and_properties_exist,
)
from metldata.builtin_transformations.delete_content_subschema.config import (
    DeleteContentSubschemaConfig,
)
from metldata.builtin_transformations.delete_content_subschema.data_transform import (
    delete_subschema_properties,
)
from metldata.builtin_transformations.delete_content_subschema.model_transform import (
    delete_content_subschema,
)
from metldata.transform.base import (
    DataTransformer,
    TransformationDefinition,
)


class PropertyDeletionDataTransformer(DataTransformer[DeleteContentSubschemaConfig]):
    """A transformer that deletes content properties from data."""

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return delete_subschema_properties(
            data=data, instructions_by_class=self._config.instructions_by_class()
        )


def check_model_assumptions(
    model: SchemaPack,
    config: DeleteContentSubschemaConfig,
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    assert_classes_and_properties_exist(
        schema=model, instructions_by_class=config.instructions_by_class()
    )


def transform_model(
    model: SchemaPack, config: DeleteContentSubschemaConfig
) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return delete_content_subschema(
        model=model, instructions_by_class=config.instructions_by_class()
    )


DELETE_CONTENT_SUBSCHEMA_TRANSFORMATION = TransformationDefinition[
    DeleteContentSubschemaConfig
](
    config_cls=DeleteContentSubschemaConfig,
    check_model_assumptions=check_model_assumptions,
    transform_model=transform_model,
    data_transformer_factory=PropertyDeletionDataTransformer,
)
