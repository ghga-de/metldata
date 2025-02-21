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
#

"""Data models"""

from enum import Enum

from pydantic import BaseModel, Field


class RelationPathElementType(Enum):
    """The type of RelationPathElements.

    Can be active, meaning the source class is referencing the target class using the
    specified slot.
    Or passive, meaning that the source class is referenced by the target class and the
    slot is part of the target class.
    """

    ACTIVE = "active"
    PASSIVE = "passive"


class RelationPathElement(BaseModel):
    """A model describing an element of a relation path between classes of a
    metadata model as further explained by the RelationPath.
    """

    type_: RelationPathElementType = Field(
        default=...,
        description=(
            "The type of relation. Active or passive as explained in the"
            + " RelationPathElementType enum."
        ),
    )
    source: str = Field(
        default=..., description="The name of the source class that is referencing."
    )
    target: str = Field(
        default=..., description="The name of the target class that is referenced."
    )
    property: str = Field(
        default=...,
        description=(
            "The name of the property that holds the relation."
            + " In case of a active type, the property is part of the source class."
            + " In case of a passive type, the property is part of the target class."
        ),
    )
