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

"""Utilities for manipulating the schemas. This extends the functionality provided by
the standard linkml SchemaView class."""

from copy import deepcopy
from typing import Optional, Union

from linkml_runtime.linkml_model.meta import SlotDefinition, ClassDefinition
from regex import F

from metldata.model_utils.anchors import AnchorPoint
from metldata.model_utils.essentials import ExportableSchemaView
from metldata.model_utils.assumptions import ROOT_CLASS


class ModelManipulationError(RuntimeError):
    """A base for exception occurring in the context of model manipulations."""


class ClassNotFoundError(ModelManipulationError):
    """Raised when a class was not found."""

    def __init__(self, class_name: str):
        message = f"The class '{class_name}' does not exist in the metadata model."
        super().__init__(message)


class ClassSlotNotFoundError(ModelManipulationError):
    """Raised when a slot of a class was not found."""

    def __init__(self, class_name: str, slot_name: str):
        message = (
            f"The slot '{slot_name}' does not exist in the class '{class_name}' of the"
            + " metadata model."
        )
        super().__init__(message)


def add_slot_if_not_exists(
    schema_view: ExportableSchemaView, new_slot: SlotDefinition
) -> ExportableSchemaView:
    """Add the new slot only if it does not exist and return a modified copy of the
    provided schema view. If it does already exist, the schema view is returned
    unmodified."""

    if not schema_view.get_slot(slot_name=new_slot.name):
        schema_view_copy = deepcopy(schema_view)
        schema_view_copy.add_slot(new_slot)

        return schema_view_copy

    return schema_view


def upsert_class_slot(
    schema_view: ExportableSchemaView, class_name: str, new_slot: SlotDefinition
) -> ExportableSchemaView:
    """Insert a new or update an existing slot of a class.

    Raises:
        ClassNotFoundError: if the specified class does not exist.
    """

    class_ = schema_view.get_class(class_name=class_name)

    # add slot to list of slots used by the class:
    if not class_:
        raise ClassNotFoundError(class_name=class_name)

    class_copy = deepcopy(class_)

    if class_copy.slots:
        if all(str(slot) != new_slot.name for slot in class_copy.slots):
            class_copy.slots.append(new_slot.name)
    else:
        class_copy.slots = [new_slot.name]

    # update slot usage:
    if class_copy.slot_usage:
        if not isinstance(class_copy.slot_usage, dict):
            raise RuntimeError(f"Unexpected slot usage for class '{class_name}'")
        class_copy.slot_usage[new_slot.name] = new_slot
    else:
        class_copy.slot_usage = {new_slot.name: new_slot}

    # add updated class and a global definition of the slot to a copy of schema view:
    schema_view_copy = deepcopy(schema_view)
    schema_view_copy = add_slot_if_not_exists(
        schema_view=schema_view_copy, new_slot=new_slot
    )
    schema_view_copy.add_class(class_copy)

    return schema_view_copy


def delete_class_slot(
    schema_view: ExportableSchemaView, class_name: str, slot_name: str
) -> ExportableSchemaView:
    """Delete a slot from a class. This slot may not be inherited but must be
    a slot of the class itself.

    Raises:
        ClassNotFoundError: if the specified class does not exist.
        ClassSlotNotFoundError: if the specified slot does not exist in the specified class.
    """

    class_ = schema_view.get_class(class_name=class_name)

    if not class_:
        raise ClassNotFoundError(class_name=class_name)

    class_copy = deepcopy(class_)

    # modify class slots:
    all_slots = schema_view.class_slots(class_name=class_name, direct=True)

    if slot_name not in all_slots:
        raise ClassSlotNotFoundError(class_name=class_name, slot_name=slot_name)

    all_slots_modified = [slot for slot in all_slots if slot != slot_name]

    class_copy.slots = all_slots_modified

    # update slot usage:
    if class_copy.slot_usage:
        if not isinstance(class_copy.slot_usage, dict):
            raise RuntimeError(f"Unexpected slot usage for class '{class_name}'")
        if slot_name in class_copy.slot_usage:
            del class_copy.slot_usage[slot_name]

    # add updated class to a copy of schema view:
    schema_view_copy = deepcopy(schema_view)
    schema_view_copy.add_class(class_copy)

    return schema_view_copy


def add_slot_usage_annotation(
    *,
    schema_view: ExportableSchemaView,
    slot_name: str,
    class_name: str,
    annotation_key: str,
    annotation_value: Union[str, bool, int, float],
) -> ExportableSchemaView:
    """Add annotations to a slot in the context of a class.
    For more details see:
    https://linkml.io/linkml/schemas/metadata.html#arbitrary-annotations
    """

    class_ = schema_view.get_class(class_name=class_name)

    if not class_:
        raise ClassNotFoundError(class_name=class_name)

    class_copy = deepcopy(class_)

    if class_copy.slot_usage:
        if not isinstance(class_copy.slot_usage, dict):
            raise RuntimeError(f"Unexpected slot usage for class '{class_name}'")
        if slot_name not in class_copy.slot_usage:
            raise ClassSlotNotFoundError(class_name=class_name, slot_name=slot_name)

        slot_usage = class_copy.slot_usage[slot_name]

        if slot_usage.annotations:
            slot_usage.annotations[annotation_key] = annotation_value
        else:
            slot_usage.annotations = {annotation_key: annotation_value}

    # add updated class to a copy of schema view:
    schema_view_copy = deepcopy(schema_view)
    schema_view_copy.add_class(class_copy)

    return schema_view_copy

def _get_root_class(*, schema_view: ExportableSchemaView) -> ClassDefinition:
    """A helper function to get the root class of the model."""
    
        root_class = schema_view.get_class(class_name=ROOT_CLASS)
    
        if not root_class:
            raise ClassNotFoundError(class_name=ROOT_CLASS)
    
        return root_class


def add_anchor_point(*, schema_view: ExportableSchemaView, anchor_point: AnchorPoint, description: Optional[str]= None) -> ExportableSchemaView:
    """Add an anchor point for a class to the tree root of the model."""

    class_ = schema_view.get_class(class_name=anchor_point.target_class)

    if not class_:
        raise ClassNotFoundError(class_name=anchor_point.target_class)
    
    root_slot_definition = SlotDefinition(name=anchor_point.root_slot, range=anchor_point.target_class, multivalued=True, required=True, inlined=True, inlined_as_list=False, description=description)

    root_class = _get_root_class(schema_view=schema_view)
    return upsert_class_slot(schema_view=schema_view, class_name=root_class.name, new_slot=root_slot_definition)
