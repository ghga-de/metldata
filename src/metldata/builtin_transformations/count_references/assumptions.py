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

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)
from metldata.transform.base import ModelAssumptionError


def assert_class_is_source(
    model: SchemaPack, instruction: AddReferenceCountPropertyInstruction
):
    """Make sure that the source class is the one being modified with the count property"""
    if instruction.class_name != instruction.source_relation_path.source:
        raise ModelAssumptionError(
            f"Class {instruction.class_name} does not correspond to the relation source {
                instruction.source_relation_path.source}."
        )


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

        if path_element.type_ == RelationPathElementType.ACTIVE and (
            path_element.property not in model.classes[path_element.source].relations
        ):
            raise ModelAssumptionError(
                f"Relation property {path_element.property} not found in class"
                f" {path_element.source}."
            )


def assert_summary_exists(
    schema: SchemaPack,
    instruction: AddReferenceCountPropertyInstruction,
) -> None:
    """Make sure that the source class (the class being modified) and the object_path exists in the model."""
    class_name = instruction.class_name
    class_def = schema.classes.get(class_name)

    # Check if the class exists in the model
    if not class_def:
        raise ModelAssumptionError(
            f"Class {class_name} does not exist in the model.")

    # Check if the object_path already exists in the model
    try:
        target_schema = resolve_schema_object_path(
            json_schema=class_def.content.json_schema_dict,
            path=instruction.target_content.object_path,
        )
    except KeyError as err:
        raise ModelAssumptionError(
            f"Object path {
                instruction.target_content.object_path} does not exist"
            + f" in class {class_name}."
        ) from err
    if instruction.target_content.property_name in target_schema.get("properties", {}):
        raise ModelAssumptionError(
            f"Property {
                instruction.target_content.property_name} already exists"
            + f" in class {class_name}."
        )


def check_model_assumptions(
    schema: SchemaPack, instructions: list[AddReferenceCountPropertyInstruction]
) -> None:
    """Check the model assumptions for the count references transformation."""
    for instruction in instructions:
        assert_class_is_source(schema, instruction)
        assert_path_classes_and_relations_exist(
            schema, instruction.source_relation_path
        )
        assert_summary_exists(schema, instruction)
