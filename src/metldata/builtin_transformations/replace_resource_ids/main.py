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

"""A transformation to replace resource ids in the data."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.replace_resource_ids.assumptions import (
    check_model_assumptions,
)
from metldata.builtin_transformations.replace_resource_ids.config import (
    ReplaceResourceIdsConfig,
)
from metldata.builtin_transformations.replace_resource_ids.data_transform import (
    replace_data_resource_ids,
)
from metldata.builtin_transformations.replace_resource_ids.model_transform import (
    replace_model_resource_ids,
)
from metldata.transform.base import (
    DataTransformer,
    SubmissionAnnotation,
    TransformationDefinition,
)


class ReplaceResourceIdsTransformer(
    DataTransformer[ReplaceResourceIdsConfig, SubmissionAnnotation]
):
    """A transformer that replaces the resource IDs in the data with the ones coming
    from an annotation.
    """

    def transform(self, data: DataPack, annotation: SubmissionAnnotation) -> DataPack:
        """Transforms data.
        The expected format of the 'annotation' parameter is:
        {
            'accession_map': {
                <class_name>: {
                    <old_id>: <new_id>,
                    ...
                },
                ...
            }
        }

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return replace_data_resource_ids(
            data=data, class_name=self._config.class_name, annotation=annotation
        )


def check_model_assumptions_wrapper(
    model: SchemaPack, config: ReplaceResourceIdsConfig
) -> None:
    """Check the assumptions of the model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_model_assumptions(model=model, class_name=config.class_name)


def transform_model(model: SchemaPack, config: ReplaceResourceIdsConfig) -> SchemaPack:
    """Transform the data model.

    Raises:
        DataModelTransformationError:
            if the transformation fails.
    """
    return replace_model_resource_ids(model=model)


REPLACE_RESOURCE_IDS_TRANSFORMATION = TransformationDefinition[
    ReplaceResourceIdsConfig
](
    config_cls=ReplaceResourceIdsConfig,
    check_model_assumptions=check_model_assumptions_wrapper,
    transform_model=transform_model,
    data_transformer_factory=ReplaceResourceIdsTransformer,
)
