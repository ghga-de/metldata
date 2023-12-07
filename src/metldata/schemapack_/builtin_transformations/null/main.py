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

"""Contains the transformation definition."""

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.event_handling.models import SubmissionAnnotation
from metldata.schemapack_.builtin_transformations.null.config import NullConfig
from metldata.schemapack_.transform.base import (
    DataTransformer,
    TransformationDefinition,
)


def null_model_assumptions(model: SchemaPack, config: NullConfig):
    """No assumptions made."""
    return


def null_transform_model(model: SchemaPack, config: NullConfig) -> SchemaPack:
    """The model is returned unchanged."""
    return model


class NullTransformer(DataTransformer[NullConfig]):
    """A Null transformer that returns the input model and data unchanged. Useful e.g.
    for testing."""

    def transform(
        self, *, data: DataPack, annotation: SubmissionAnnotation
    ) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.
            annotation: The annotation on the data.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        return data


NULL_TRANSFORMATION = TransformationDefinition(
    config_cls=NullConfig,
    check_model_assumptions=lambda schemapack, config: None,
    transform_model=lambda schemapack, config: schemapack,
    data_transformer_factory=NullTransformer,
)
