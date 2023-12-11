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

"""A transformation to infer references based on existing ones in the data model."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.schemapack_.builtin_transformations.infer_relations import (
    data_transform,
    model_transform,
)
from metldata.schemapack_.builtin_transformations.infer_relations.config import (
    RelationInferenceConfig,
)
from metldata.schemapack_.transform.base import (
    DataTransformer,
    TransformationDefinition,
)


class RelationInferenceDataTransformer(DataTransformer[RelationInferenceConfig]):
    """A transformer that infers relation in data based on existing ones."""

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return data_transform.add_inferred_relations(
            data=data, instructions=self._config.inference_instructions
        )


def check_model_assumptions(
    model: SchemaPack,
    config: RelationInferenceConfig,
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    pass


def transform_model(model: SchemaPack, config: RelationInferenceConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return model_transform.add_inferred_relations(
        model=model, instructions=config.inference_instructions
    )


RELATION_INFERENCE_TRANSFORMATION = TransformationDefinition[RelationInferenceConfig](
    config_cls=RelationInferenceConfig,
    check_model_assumptions=check_model_assumptions,
    transform_model=transform_model,
    data_transformer_factory=RelationInferenceDataTransformer,
)
