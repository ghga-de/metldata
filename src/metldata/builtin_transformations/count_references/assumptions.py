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
from metldata.transform.base import ModelAssumptionError, MultiplicityError


def validate_modification_class(path_element, expected_class_name):
    """Check whether the class specified to be modified with the reference count
    matches the source or target class in the provided `path_element`, depending on the
    type of the relation path (i.e., active or passive). If the class does not match,
    an exception is raised.
    """
    modification_class_name = (
        path_element.source
        if path_element.type_ == RelationPathElementType.ACTIVE
        else path_element.target
    )
    if expected_class_name != modification_class_name:
        raise ModelAssumptionError(
            f"Class {
                expected_class_name} does not correspond to the relation source "
            f"{modification_class_name}."
        )


def check_class_exists(model: SchemaPack, class_name: str) -> None:
    """Check if a class exists in the model and raise an error if not"""
    if class_name not in model.classes:
        raise ModelAssumptionError(f"Class {class_name} not found in model.")


def check_relation_exists(model: SchemaPack, class_name: str, relation: str):
    """Check if a relation exists in a class and raise an error if not"""
    if relation not in model.classes[class_name].relations:
        raise ModelAssumptionError(
            f"Relation property {
                relation} not found in class {class_name}."
        )


def assert_class_is_source(instruction: AddReferenceCountPropertyInstruction):
    """Ensure that the class being modified with the reference count property is the expected class.
    This function iterates over the elements of the relation path in the given instruction
    and validates that the class being modified with the reference count property matches
    the class specified in the relation path.
    """
    for path_element in instruction.source_relation_path.elements:
        validate_modification_class(path_element, instruction.class_name)


def assert_path_classes_and_relations_exist(model: SchemaPack, path: RelationPath):
    """Make sure that all classes and relations defined in the provided path exist in
    the provided model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    for path_element in path.elements:
        check_class_exists(model, path_element.source)
        check_class_exists(model, path_element.target)

        if path_element.type_ == RelationPathElementType.ACTIVE:
            check_relation_exists(model, path_element.source, path_element.property)

        if path_element.type_ == RelationPathElementType.PASSIVE:
            check_relation_exists(model, path_element.target, path_element.property)


def assert_multiplicity(model: SchemaPack, path: RelationPath):
    """Make sure the target of the relation contributes multiple instances to the relation."""
    for path_element in path.elements:
        if path_element.type_ == RelationPathElementType.ACTIVE:
            relation = model.classes[path_element.source].relations[
                path_element.property
            ]
            if not relation.multiple.target:
                raise MultiplicityError(
                    f"The target of the relation {
                        path_element.property} does not contribute multiple instances to the relation."
                )


def assert_summary_exists(
    model: SchemaPack,
    instruction: AddReferenceCountPropertyInstruction,
) -> None:
    """Make sure that the source class (the class being modified) and the object_path exists in the model."""
    class_name = instruction.class_name
    class_def = model.classes.get(class_name)

    # Check if the class exists in the model
    if not class_def:
        raise ModelAssumptionError(f"Class {class_name} does not exist in the model.")

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

    # Check if the propert_name already exists in the model
    if instruction.target_content.property_name not in target_schema.get(
        "properties", {}
    ):
        raise ModelAssumptionError(
            f"Property {
                instruction.target_content.property_name} does not exist"
            + f" in class {class_name}."
        )


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[AddReferenceCountPropertyInstruction]],
) -> None:
    """Check the model assumptions for the count references transformation."""
    for _, instructions in instructions_by_class.items():
        for instruction in instructions:
            assert_class_is_source(instruction)
            assert_path_classes_and_relations_exist(
                schema, instruction.source_relation_path
            )
            assert_multiplicity(schema, instruction.source_relation_path)
            assert_summary_exists(schema, instruction)
