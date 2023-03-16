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

"""All classes that shall be referenced by ID must be linked in the root class of the
model. The slot in the root that links to a specific class is called the anchor point of
that class. This module provides logic for handling these anchor points.
"""

from pydantic import BaseModel, Field

from metldata.custom_types import Json
from metldata.model_utils.essentials import ROOT_CLASS


class AnchorPoint(BaseModel):
    """A model for describing an anchor point for the specified target class."""

    target_class: str = Field(..., description="The name of the class to be targeted.")
    root_slot: str = Field(
        ...,
        description=(
            "The name of the slot in the root class used to link to the target class."
        ),
    )


def get_anchor_points(*, model: Json) -> tuple[AnchorPoint]:
    """Get all anchor points of the specified model."""

    raise NotImplementedError()
