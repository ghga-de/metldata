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
"""Check model assumptions for the add content properties transformation."""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_content_properties.instruction import (
    AddContentPropertyInstruction,
)
from metldata.builtin_transformations.add_content_properties.path import (
    resolve_object_path,
)
from metldata.transform.base import ModelAssumptionError


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[AddContentPropertyInstruction]],
) -> None:
    """Check the model assumptions for the add content properties transformation."""
    for class_name, instructions in instructions_by_class.items():
        class_def = schema.classes.get(class_name)

        # Check if the class exists in the model
        if not class_def:
            raise ModelAssumptionError(
                f"Class {class_name} does not exist in the model."
            )

        for instruction in instructions:
            # Check if the property already exists in the target schema
            try:
                target_schema = resolve_object_path(
                    json_schema=class_def.content.json_schema_dict,
                    path=instruction.target_content.object_path,
                )
            except KeyError:
                continue
            if instruction.target_content.property_name in target_schema.get(
                "properties", {}
            ):
                raise ModelAssumptionError(
                    f"Property {instruction.target_content.property_name} already exists"
                    + " in class {instruction.class_name}."
                )
