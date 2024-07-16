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

"Assumptions for count references transformation"

from typing import Any

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.builtin_transformations.count_references.instruction import (
    AddCountPropertyInstruction,
)
from metldata.transform.base import ModelAssumptionError


def assert_path_classes_and_relations_exist(model: SchemaPack, path: RelationPath):
    """Make sure that all classes and relations defined in the provided path exist in
    the provided model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    for path_element in path.elements:
        if path_element.source not in model.classes:
            raise ModelAssumptionError(
                f"Class {path_element.source} not found in model."
            )

        if path_element.target not in model.classes:
            raise ModelAssumptionError(
                f"Class {path_element.target} not found in model."
            )

        if path_element.type_ == RelationPathElementType.ACTIVE:
            if (
                path_element.property
                not in model.classes[path_element.source].relations
            ):
                raise ModelAssumptionError(
                    f"Relation property {path_element.property} not found in class"
                    f" {path_element.source}."
                )

            return


def assert_new_property_not_exists(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[AddCountPropertyInstruction]],
) -> None:
    """Check the model assumptions for the add content properties transformation."""
    # the existence of the class getting the new property is already checked in the previous assumption.
    for class_name, instructions in instructions_by_class.items():
        # class_def = schema.classes.get(class_name)

        # # Check if the class exists in the model
        # if not class_def:
        #     raise ModelAssumptionError(
        #         f"Class {class_name} does not exist in the model."
        #     )

        for instruction in instructions:
            # Check if the property already exists in the target schema
            try:
                target_schema = resolve_schema_object_path(
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
                    + f" in class {class_name}."
                )


def check_model_assumptions(schema: SchemaPack, instructions_by_class: Any) -> None:
    """Check the model assumptions for the count references transformation."""
    return None
