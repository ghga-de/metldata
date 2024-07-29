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

from schemapack.spec.schemapack import ClassDefinition, SchemaPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.count_content_values.instruction import (
    CountContentValuesInstruction,
)
from metldata.builtin_transformations.count_content_values.path.path import RelationPath
from metldata.builtin_transformations.count_content_values.path.path_elements import (
    RelationPathElementType,
)
from metldata.transform.base import ModelAssumptionError


def check_model_assumptions(
    schema: SchemaPack,
    instructions: list[CountContentValuesInstruction],
) -> None:
    """Check the model assumptions for the add content properties transformation."""
    for instruction in instructions:
        class_name = instruction.class_name
        class_def = schema.classes.get(class_name)

        # Check if the class exists in the model
        if not class_def:
            raise ModelAssumptionError(
                f"Class {class_name} does not exist in the model."
            )

        assert_target_path_assumptions(
            class_def=class_def, class_name=class_name, instruction=instruction
        )
        assert_relation_path_assumptions(
            model=schema, path=instruction.source.relation_path
        )


def assert_target_path_assumptions(
    *,
    class_def: ClassDefinition,
    class_name: str,
    instruction: CountContentValuesInstruction,
):
    """Assert object path exists and property does not already exists in the target content"""
    object_path = instruction.target_content.object_path
    property_name = instruction.target_content.property_name

    # check if content schema exists for given object path
    try:
        target_schema = resolve_schema_object_path(
            json_schema=class_def.content.json_schema_dict,
            path=object_path,
        )
    except KeyError as error:
        raise ModelAssumptionError(
            f"Target object path {
                object_path} does not exist in class {class_name}."
        ) from error

    if property_name in target_schema.get("properties", {}):
        raise ModelAssumptionError(
            f"Property {property_name} already exists for object path {
                object_path} in class {class_name}."
        )


def assert_relation_path_assumptions(model: SchemaPack, path: RelationPath):
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
                    f"Relation property {
                        path_element.property} not found in class"
                    f" {path_element.source}."
                )

            return

        if path_element.property not in model.classes[path_element.target].relations:
            raise ModelAssumptionError(
                f"Relation property {path_element.property} not found in class"
                f" {path_element.target}."
            )


def assert_relational_multiplicity(
    model: SchemaPack, relation_path: RelationPath, content_path: str
):
    """TODO"""
    for path_element in relation_path.elements:
        if path_element.type_ == RelationPathElementType.ACTIVE:
            multiplicity = (
                model.classes[path_element.source]
                .relations[path_element.property]
                .multiple
            )
            if not multiplicity.origin or not multiplicity.target:
                raise ModelAssumptionError(
                    f"Relation property {
                        path_element.property} not found in class"
                    f" {path_element.target}."
                )

            target_content_schema = model.classes[
                path_element.target
            ].content.json_schema_dict

            try:
                target_schema = resolve_schema_object_path(
                    json_schema=target_content_schema,
                    path=content_path,
                )
            except KeyError as error:
                raise ModelAssumptionError(
                    f"{path_element.target} does not contain the property {
                        content_path}"
                ) from error

            if target_schema["type"] != "integer":
                raise ModelAssumptionError(f"{content_path} of class {
                                           path_element.target} is not an integer property.")

        else:
            multiplicity = (
                model.classes[path_element.target]
                .relations[path_element.property]
                .multiple
            )
            if not multiplicity.origin or multiplicity.target:
                raise ModelAssumptionError(
                    f"Relation property {
                        path_element.property} not found in class"
                    f" {path_element.target}."
                )
