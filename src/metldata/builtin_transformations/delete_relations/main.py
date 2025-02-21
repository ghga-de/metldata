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

"""A transformation to delete references."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.delete_relations.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.delete_relations.config import (
    DeleteRelationsConfig,
)
from metldata.builtin_transformations.delete_relations.data_transform import (
    delete_data_relations,
)
from metldata.builtin_transformations.delete_relations.model_transform import (
    delete_model_relations,
)
from metldata.transform.base import (
    DataTransformer,
    TransformationDefinition,
)


class DeleteRelationsDataTransformer(DataTransformer[DeleteRelationsConfig]):
    """A transformer that deletes relation from data."""

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return delete_data_relations(
            data=data, instructions_by_class=self._config.instructions_by_class
        )


def check_model_assumptions_wrapper(
    model: SchemaPack, config: DeleteRelationsConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(
        schema=model, instructions_by_class=config.instructions_by_class
    )


def transform_model(model: SchemaPack, config: DeleteRelationsConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return delete_model_relations(
        model=model, instructions_by_class=config.instructions_by_class
    )


DELETE_RELATIONS_TRANSFORMATION = TransformationDefinition[DeleteRelationsConfig](
    config_cls=DeleteRelationsConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=DeleteRelationsDataTransformer,
)
