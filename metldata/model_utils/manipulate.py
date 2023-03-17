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

from linkml_runtime.linkml_model.meta import SlotDefinition

from metldata.model_utils.essentials import ExportableSchemaView


class ModelManipulationError(RuntimeError):
    """A base for exception occuring in the context of model manipulations."""


class ClassNotFoundError(ModelManipulationError):
    """Raised when a class was not found."""

    def __init__(self, class_name: str):
        message = f"The class '{class_name}' does not exist in the metadata model."
        super().__init__(message)


def add_slot_if_not_exists(
    schema_view: ExportableSchemaView, new_slot: SlotDefinition
) -> ExportableSchemaView:
    """Add the new slot only if it does not exist and return a modified copy of the
    provided schema view. If it does already exist, the schema view is return
    unmodified."""

    if not schema_view.get_slot(slot_name=new_slot.name):
        schema_view_copy = deepcopy(schema_view)
        schema_view_copy.add_slot(new_slot)

        return schema_view_copy

    return schema_view


def upsert_class_slot(
    schema_view: ExportableSchemaView, class_name: str, new_slot: SlotDefinition
) -> ExportableSchemaView:
    """Insert a new or update and existing slot of a class.

    Raises:
        ClassNotFoundError: if the specified class does not exist.
    """

    class_ = schema_view.get_class(class_name=class_name)

    # add slot to list of slots used by the class:
    if not class_:
        raise ClassNotFoundError(class_name=class_name)

    if class_.slots:
        if new_slot.name not in [str(slot) for slot in class_.slots]:
            class_.slots.append(new_slot.name)
    else:
        class_.slots = [new_slot.name]

    # update slot usage:
    if class_.slot_usage:
        if isinstance(class_.slot_usage, dict):
            class_.slot_usage[new_slot.name] = new_slot
        else:
            raise RuntimeError(f"Unexpected slot usage for class '{class_name}'")
    else:
        class_.slot_usage = {new_slot.name: new_slot}

    # add updated class and a global definition of the slot to a copy of schema view:
    schema_view_copy = deepcopy(schema_view)
    schema_view_copy = add_slot_if_not_exists(
        schema_view=schema_view_copy, new_slot=new_slot
    )
    schema_view_copy.add_class(class_)

    return schema_view_copy
