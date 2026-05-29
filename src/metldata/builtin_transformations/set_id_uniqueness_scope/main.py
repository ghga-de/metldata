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

"""A transformation to set the ID uniqueness scope on the schema."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.registry import register_transformation
from metldata.builtin_transformations.set_id_uniqueness_scope.config import (
    SetIdUniquenessScopeConfig,
)
from metldata.builtin_transformations.set_id_uniqueness_scope.model_transform import (
    set_id_uniqueness_scope_on_schema,
)
from metldata.transform.base import (
    DataTransformer,
    SubmissionAnnotation,
    TransformationDefinition,
)


class SetIdUniquenessScopeTransformer(
    DataTransformer[SetIdUniquenessScopeConfig, SubmissionAnnotation]
):
    """A transformer that passes data through unchanged."""

    def transform(self, data: DataPack, annotation: SubmissionAnnotation) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return data


def transform_model(
    model: SchemaPack, config: SetIdUniquenessScopeConfig
) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return set_id_uniqueness_scope_on_schema(
        model=model, globally_unique_ids=config.globally_unique_ids
    )


SET_ID_UNIQUENESS_SCOPE_TRANSFORMATION = TransformationDefinition[
    SetIdUniquenessScopeConfig
](
    config_cls=SetIdUniquenessScopeConfig,
    check_model_assumptions=lambda model, config: None,
    transform_model=transform_model,
    data_transformer_factory=SetIdUniquenessScopeTransformer,
)


@register_transformation("set_id_uniqueness_scope")
def set_id_uniqueness_scope_transformation() -> TransformationDefinition[
    SetIdUniquenessScopeConfig
]:
    """Get the transformation definition for the set_id_uniqueness_scope transformation."""
    return SET_ID_UNIQUENESS_SCOPE_TRANSFORMATION
