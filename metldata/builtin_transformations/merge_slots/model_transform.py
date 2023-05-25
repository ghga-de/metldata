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

"""Logic for transforming metadata models."""


from metldata.builtin_transformations.merge_slots.models import SlotMergeInstruction
from metldata.model_utils.essentials import ExportableSchemaView, MetadataModel
from metldata.transform.base import MetadataModelTransformationError


def get_source_range(
    *, schema_view: ExportableSchemaView, class_name: str, source_slot: str
) -> str:
    """Get the range of a source slot for the provided class.

    Raises:
        MetadataModelTransformationError:
            If the slot has no defined range, or if the slot is using a union range
            with the `all_of` or `any_of` properties.
    """

    slot = schema_view.induced_slot(class_name=class_name, slot_name=source_slot)

    if not slot.range:
        raise MetadataModelTransformationError(
            f"Source slot {source_slot} of class {class_name} has no defined range."
        )

    if slot.all_of is not None or slot.any_of is not None:
        raise MetadataModelTransformationError(
            f"Source slot {source_slot} of class {class_name} is using a union range."
        )

    return str(slot.range)


def get_source_ranges(
    *, schema_view: ExportableSchemaView, class_name: str, source_slots: list[str]
) -> set[str]:
    """Get the ranges of the given source slots."""

    return {
        get_source_range(
            schema_view=schema_view, class_name=class_name, source_slot=source_slot
        )
        for source_slot in source_slots
    }


def apply_merge_instruction(
    *, schema_view: ExportableSchemaView, merge_instruction: SlotMergeInstruction
) -> ExportableSchemaView:
    """Apply the provided merge instructions to the provided schema_view."""

    raise NotImplementedError


def merge_slots_in_model(
    *, model: MetadataModel, merge_instructions: list[SlotMergeInstruction]
) -> MetadataModel:
    """Merge slots in the provided model according to the provided instructions."""

    schema_view = model.schema_view

    for merge_instruction in merge_instructions:
        schema_view = apply_merge_instruction(
            schema_view=schema_view, merge_instruction=merge_instruction
        )

    return schema_view.export_model()
