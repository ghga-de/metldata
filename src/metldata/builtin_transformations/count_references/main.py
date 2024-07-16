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

"""A transformation to count references."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.count_references.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.count_references.config import (
    CountReferencesConfig,
)
from metldata.builtin_transformations.count_references.data_transform import (
    count_references,
)
from metldata.builtin_transformations.count_references.model_transform import (
    add_count_references,
)
from metldata.transform.base import DataTransformer, TransformationDefinition


class CountReferencesTransformer(DataTransformer[CountReferencesConfig]):
    """A transformer that counts the references and adds them to content properties."""

    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.
        """
        return count_references(data=data)


def check_model_assumptions_wrapper(
    model: SchemaPack, config: CountReferencesConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(schema=model, instructions_by_class=config.count_references)


def transform_model(model: SchemaPack, config: CountReferencesConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return add_count_references(
        model=model, instructions_by_class=config.count_references
    )


COUNT_REFERENCES_TRANSFORMATION = TransformationDefinition[CountReferencesConfig](
    config_cls=CountReferencesConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=CountReferencesTransformer,
)
