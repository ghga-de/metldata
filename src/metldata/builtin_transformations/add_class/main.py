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

"""A transformation to add classes."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_class.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.add_class.config import (
    AddClassConfig,
)
from metldata.builtin_transformations.add_class.data_transform import (
    add_data_class,
)
from metldata.builtin_transformations.add_class.model_transform import (
    add_model_class,
)
from metldata.builtin_transformations.registry import register_transformation
from metldata.transform.base import (
    DataTransformer,
    SubmissionAnnotation,
    TransformationDefinition,
)


class AddClassTransformer(DataTransformer[AddClassConfig, SubmissionAnnotation]):
    """A transformer that adds a class to data."""

    def transform(self, data: DataPack, annotation: SubmissionAnnotation) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return add_data_class(
            data=data,
            annotation=annotation,
            class_name=self._config.class_name,
            content_schema=self._config.content_schema,
            relations=self._config.relations,
        )


def check_model_assumptions_wrapper(model: SchemaPack, config: AddClassConfig) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(model=model, config=config)


def transform_model(model: SchemaPack, config: AddClassConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return add_model_class(
        model=model,
        class_name=config.class_name,
        id_property_name=config.id_property_name,
        content_schema=config.content_schema,
        description=config.description,
        relations=config.relations,
    )


ADD_CLASS_TRANSFORMATION = TransformationDefinition[AddClassConfig](
    config_cls=AddClassConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=AddClassTransformer,
)


@register_transformation("add_class")
def add_class_transformation() -> TransformationDefinition[AddClassConfig]:
    """Get the transformation definition for the add_class transformation."""
    return ADD_CLASS_TRANSFORMATION
