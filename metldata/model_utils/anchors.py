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

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SlotDefinition
from pydantic import BaseModel, Field

from metldata.model_utils.essentials import ROOT_CLASS, MetadataModel


class AnchorPoint(BaseModel):
    """A model for describing an anchor point for the specified target class."""

    target_class: str = Field(..., description="The name of the class to be targeted.")
    root_slot: str = Field(
        ...,
        description=(
            "The name of the slot in the root class used to link to the target class."
        ),
    )

    class Config:
        """Pydantic Configs."""

        frozen = True


class InvalidAnchorPointError(RuntimeError):
    """Raised when an anchor point defined in a model is invalid."""


def check_root_slot(slot: SlotDefinition):
    """Make sure that the given root slot is a valid anchor point. Validates that the
    slot is multivalued and required but not inlined.

    Raises:
        InvalidAnchorPointError: if validation fails.
    """

    if not slot.multivalued:
        raise InvalidAnchorPointError(
            f"The anchor point at the slot '{slot.name}' is not multivalued."
        )

    if slot.inlined is None:
        raise InvalidAnchorPointError(
            f"The inlined attribute for slot '{slot.name}' is not defined."
        )

    if slot.inlined:
        raise InvalidAnchorPointError(
            f"The inlined attribute for slot '{slot.name}' is set to True,"
            + " however, slots in the root class may not be inlined."
        )

    if slot.inlined_as_list:
        raise InvalidAnchorPointError(
            f"The inlined_as_list attribute for slot '{slot.name}' is set to True,"
            + " however, slots in the root class may not be inlined."
        )

    if not slot.required:
        raise InvalidAnchorPointError(
            f"The anchor point at the slot '{slot.name}' is not required."
        )


def get_slot_target_class(*, slot: SlotDefinition, schema_view: SchemaView) -> str:
    """Checks that the specified slot refers to another class and returns the name
    of that class."""

    if slot.range is None:
        raise InvalidAnchorPointError(
            f"The slot '{slot.name}', which is used as anchor point, has no range"
            + " defined."
        )

    target_class = schema_view.get_class(class_name=slot.range)

    if target_class is None:
        raise InvalidAnchorPointError(
            f"The range of slot '{slot.name}', which is used as anchor point, does not"
            + " point to a valid class."
        )

    return slot.range


def get_anchor_points(*, model: MetadataModel) -> set[AnchorPoint]:
    """Get all anchor points of the specified model."""

    schema_view = model.schema_view
    root_slots = schema_view.class_induced_slots(class_name=ROOT_CLASS)

    # validation root slots:
    for root_slot in root_slots:
        check_root_slot(root_slot)

    return {
        AnchorPoint(
            target_class=get_slot_target_class(slot=root_slot, schema_view=schema_view),
            root_slot=root_slot.name,
        )
        for root_slot in root_slots
    }
