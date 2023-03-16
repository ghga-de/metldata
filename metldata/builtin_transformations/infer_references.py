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

"""A transformation to infer references based on existing ones in the metadata model."""

from metldata.reference.config import ReferenceMapConfig
from metldata.reference.reference import InferredReference
from metldata.transform.base import Json, TransformationBase


def transform_metadata_model(
    *, model: Json, references_to_infer: list[InferredReference]
) -> Json:
    """Transform the metadata model and return the tranformed one.

    Raises:
            MetadataModelTransformationError:
                if the transformation of the metadata model fails.
    """

    raise NotImplementedError()


def check_model_assumptions(
    *, model: Json, references_to_infer: list[InferredReference]
) -> Json:
    """Check whether the assumptions made about the metadata model are met.

    Raises:
        MetadataModelAssumptionError:
            if assumptions about the metadata model are not met.
    """

    raise NotImplementedError()


class ReferenceInferenceConfig(ReferenceMapConfig):
    """Config parameters and their defaults."""


class ReferenceInferenceTransformation(TransformationBase):
    """A transformation to infer references based on existing ones in the metadata
    model."""

    def __init__(self, *, model: Json, config: ReferenceInferenceConfig):
        """Initialize the transformation with transformation-specific config params and
        the metadata model. The transformed model will be immediately available in the
        `transformed_model` attribute (may be a property).

        Raises:
            MetadataModelAssumptionError:
                if assumptions about the metadata model are not met.
            MetadataModelTransformationError:
                if the transformation of the metadata model fails.
        """

        self._original_model = model
        self._references_to_infer = config.inferred_references

        check_model_assumptions(
            model=self._original_model, references_to_infer=self._references_to_infer
        )

        self.transformed_model = transform_metadata_model(
            model=self._original_model, references_to_infer=self._references_to_infer
        )

    def transform_metadata(self, metadata: Json) -> Json:
        """Transforms metadata and returns it.

        Raises:
            MetadataTransformationError:
                if the transformation of the metadata fails.
        """

        raise NotImplementedError()
