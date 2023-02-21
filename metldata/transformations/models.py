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

"""Data models"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class InboundReference(BaseModel):
    """A model describing a reference in a metadata model class (local class) that
    originates from an other class (remote class). I.e. the remote class references
    the local class. This reference shall be reflected in local class."""

    local_slot_name: str = Field(
        ...,
        description=(
            "The name of the slot that hold the reference to the remote class in the"
            + " local class."
        ),
    )
    remote_reference_origin: str = Field(
        ..., description="The location of the reference origin in the remote class."
    )


class ClassReferences(BaseModel):
    """A model describing the references of one class of a metadata model to other
    classes."""

    inbound: list
    outbound: list


# A type describing references between classes of a metadata model:
# each key refers to a class name and the value describes the references of that class
# to other classes
ReferenceMap = dict[str, ClassReferences]
