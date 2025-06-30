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

"""A transformation to infer and add a relation."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.infer_relation.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.infer_relation.config import (
    InferRelationConfig,
)
from metldata.builtin_transformations.infer_relation.data_transform import (
    infer_data_relation,
)
from metldata.builtin_transformations.infer_relation.model_transform import (
    infer_model_relation,
)
from metldata.transform.base import (
    DataTransformer,
    TransformationDefinition,
)


class InferRelationTransformer(DataTransformer[InferRelationConfig]):
    """A transformer that infers relations based on a path and adds them to the data."""

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return infer_data_relation(
            data=data, model=self._transformed_model, transformation_config=self._config
        )


def check_model_assumptions_wrapper(
    model: SchemaPack, config: InferRelationConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(model=model, transformation_config=config)


def transform_model(model: SchemaPack, config: InferRelationConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return infer_model_relation(model=model, transformation_config=config)


INFER_RELATION_TRANSFORMATION = TransformationDefinition[InferRelationConfig](
    config_cls=InferRelationConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=InferRelationTransformer,
)
