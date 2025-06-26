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
#

"""Models to describe transformations and workflows."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias, TypeVar

from pydantic import (
    BaseModel,
    Field,
)
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

ArtifactName: TypeAlias = str


ConfigT = TypeVar("ConfigT", bound=BaseModel)


class DataTransformer[ConfigT](ABC):
    """A base class for a data transformer."""

    def __init__(
        self,
        *,
        config: ConfigT,
        input_model: SchemaPack,
        transformed_model: SchemaPack,
    ):
        """Initialize the transformer with config params, the input model, and the
        transformed model.
        """
        self._config = config
        self._input_model = input_model
        self._transformed_model = transformed_model

    @abstractmethod
    def transform(self, data: DataPack) -> DataPack:
        """Transforms data.

        Args:
            data: The data as DataPack to be transformed.

        Raises:
            DataTransformationError:
                if the transformation fails.
        """
        ...


class TransformationDefinition[ConfigT](BaseModel):
    """A model for describing a transformation."""

    config_cls: type[ConfigT] = Field(
        default=..., description="The config model of the transformation."
    )
    check_model_assumptions: Callable[[SchemaPack, ConfigT], None] = Field(
        default=...,
        description=(
            "A function that checks the assumptions made about the input model."
            + " Raises a ModelAssumptionError if the assumptions are not met."
        ),
    )
    transform_model: Callable[[SchemaPack, ConfigT], SchemaPack] = Field(
        default=...,
        description=(
            "A function to transform the model. Raises a"
            + " ModelTransformationError if the transformation fails."
        ),
    )
    data_transformer_factory: type[DataTransformer] = Field(
        default=...,
        description=(
            "A class for transforming data. Raises a DataTransformationError"
            + " if the transformation fails."
        ),
    )
