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

from typing import Any, Callable

from pydantic import BaseModel, Field

JSON = dict[str, Any]


class Transformation(BaseModel):
    """Model describing a metadata transformation."""

    model: JSON = Field(..., description="The model of the input metadata.")
    model_assumptions: list[Callable[[JSON], None]] = Field(
        ...,
        description=(
            "A list of callables that are used to check assumption regarding the input"
            + " model. Each callable receives the model as input and raises an"
            + " ModelAssumptionError if the assumption is not met."
        ),
    )
    model_transform: Callable[[JSON], JSON] = Field(
        ..., description="A callable that transforms the input model."
    )
    metadata_transform: Callable[[JSON], JSON] = Field(
        ..., description="A callable that transforms the input metadata."
    )
