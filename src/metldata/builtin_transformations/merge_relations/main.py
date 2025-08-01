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

"A transformation to merge relations."

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.merge_relations.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.merge_relations.config import (
    MergeRelationsConfig,
)
from metldata.builtin_transformations.merge_relations.data_transform import (
    merge_data_relations,
)
from metldata.builtin_transformations.merge_relations.model_transform import (
    RelationSpecificationParams,
    merge_model_relations,
)
from metldata.transform.base import (
    DataTransformer,
    SubmissionAnnotation,
    TransformationDefinition,
)


class MergeRelationsTransformer(
    DataTransformer[MergeRelationsConfig, SubmissionAnnotation]
):
    """A transformer that merges relations within data."""

    def transform(self, data: DataPack, annotation: SubmissionAnnotation) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return merge_data_relations(
            data=data,
            target_class=self._config.class_name,
            target_relation=self._config.target_relation,
            source_relations=self._config.source_relations,
        )


def check_model_assumptions_wrapper(
    model: SchemaPack, config: MergeRelationsConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(
        model=model,
        class_name=config.class_name,
        target_relation=config.target_relation,
        source_relations=config.source_relations,
    )


def transform_model(model: SchemaPack, config: MergeRelationsConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return merge_model_relations(
        model=model,
        class_name=config.class_name,
        target_relation=config.target_relation,
        source_relations=config.source_relations,
        relation_spec=RelationSpecificationParams(
            mandatory=config.mandatory,
            multiple=config.multiple,
            description=config.description,
        ),
    )


MERGE_RELATIONS_TRANSFORMATION = TransformationDefinition[MergeRelationsConfig](
    config_cls=MergeRelationsConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=MergeRelationsTransformer,
)
