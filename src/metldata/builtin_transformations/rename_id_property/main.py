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

"""A transformation to modify the content schema and data of a given class."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.rename_id_property.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.rename_id_property.config import (
    RenameIdPropertyConfig,
)
from metldata.builtin_transformations.rename_id_property.data_transform import (
    rename_data_id_property,
)
from metldata.builtin_transformations.rename_id_property.model_transform import (
    rename_model_id_property,
)
from metldata.transform.base import (
    DataTransformer,
    SubmissionAnnotation,
    TransformationDefinition,
)


class RenameIdPropertyTransformer(
    DataTransformer[RenameIdPropertyConfig, SubmissionAnnotation]
):
    """A transformer that does not apply any changes to data since the id property name
    is not a part of a DataPack.
    """

    def transform(self, data: DataPack, annotation: SubmissionAnnotation) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return rename_data_id_property(data=data)


def check_model_assumptions_wrapper(
    model: SchemaPack, config: RenameIdPropertyConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(
        model=model,
        class_name=config.class_name,
        new_id_property=config.id_property_name,
    )


def transform_model(model: SchemaPack, config: RenameIdPropertyConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return rename_model_id_property(
        model=model,
        class_name=config.class_name,
        id_property_name=config.id_property_name,
        description=config.description,
    )


RENAME_ID_PROPERTY_TRANSFORMATION = TransformationDefinition[RenameIdPropertyConfig](
    config_cls=RenameIdPropertyConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=RenameIdPropertyTransformer,
)
