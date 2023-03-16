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

"""Models to describe transformations."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

# shortcut:
# pylint: disable=unused-import
from metldata.custom_types import Json
from metldata.model_utils.assumptions import MetadataModelAssumptionError  # noqa: F401


class MetadataModelTransformationError(RuntimeError):
    """Raised when a transformation failed when applied to the metadata model."""


class MetadataTransformationError(RuntimeError):
    """Raised when a transformation failed when applied to metadata."""


class TransformationBase(ABC):
    """A base class specifying the interface of transformations."""

    # contains the transformed model:
    transformed_model: Json

    @abstractmethod
    def __init__(self, *, model: Json, config: BaseModel):
        """Initialize the transformation with transformation-specific config params and
        the metadata model. The transformed model will be immediately available in the
        `transformed_model` attribute.

        Raises:
            MetadataModelAssumptionError:
                if assumptions about the metadata model are not met.
            MetadataModelTransformationError:
                if the transformation of the metadata model fails.
        """
        ...

    @abstractmethod
    def transform_metadata(self, metadata: Json) -> Json:
        """Transforms metadata and returns it.

        Raises:
            MetadataTransformationError:
                if the transformation of the metadata fails.
        """
        ...
