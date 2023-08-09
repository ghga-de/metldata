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

"""A transformation that normalizes a model to a canonical form."""

from copy import copy

from linkml_runtime.linkml_model.meta import SlotDefinition

from metldata.model_utils.essentials import MetadataModel


def remove_non_essential(input_dict: dict) -> dict:
    """Recursively remove all 'alias', 'from_schema' and 'domain_of' fields."""
    output_dict = copy(input_dict)
    for key in ("from_schema", "domain_of"):
        if key in output_dict:
            del output_dict[key]
    for key in list(output_dict):
        if isinstance(output_dict[key], dict):
            output_dict[key] = remove_non_essential(output_dict[key])
    return output_dict


def normalize_model(model: MetadataModel) -> MetadataModel:
    """Normalized model to canonical form with all slots being globally defined
    only as empty stubs and all slot definitions being defined in the slot_usage
    of the respective class."""
    output_model = model.as_dict()
    schema_view = model.schema_view

    all_slot_names = set()
    for cls_name, cls in output_model["classes"].items():
        slot_usages = schema_view.class_induced_slots(cls_name)
        slot_names = [slot.name for slot in slot_usages]
        # Integrate all slot information
        cls["slot_usage"] = {slot_def.name: slot_def for slot_def in slot_usages}
        cls["slots"] = slot_names
        # Update all_slot names for globally reduced set of actually used slot
        # names.
        all_slot_names.update(slot_names)
        # Remove inheritance
        cls["is_a"] = None
        cls["mixins"] = []
        cls["attributes"] = []
    # Rewrite slots
    output_model["slots"] = {
        slot_name: SlotDefinition(name=slot_name) for slot_name in all_slot_names
    }

    return MetadataModel(**output_model)
