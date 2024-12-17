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

"Assumptions utilized in more than one transformation"

from collections.abc import Mapping
from typing import Any

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.common.instruction import InstructionProtocol
from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElement,
    RelationPathElementType,
)
from metldata.transform.exceptions import ModelAssumptionError, MultiplicityError


def assert_path_classes_and_relations_exist(
    *, model: SchemaPack, path: RelationPath
) -> None:
    """Make sure that all classes and relations defined in the provided path exist in
    the provided model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    for path_element in path.elements:
        _check_class_exists(model, path_element.source)
        _check_class_exists(model, path_element.target)

        if path_element.type_ == RelationPathElementType.ACTIVE:
            _check_relation_exists(model, path_element.source, path_element.property)

        if path_element.type_ == RelationPathElementType.PASSIVE:
            _check_relation_exists(model, path_element.target, path_element.property)


def _check_class_exists(model: SchemaPack, class_name: str) -> None:
    """Check if a class exists in the model and raise an error if not"""
    if class_name not in model.classes:
        raise ModelAssumptionError(f"Class {class_name} not found in model.")


def _check_relation_exists(model: SchemaPack, class_name: str, relation: str) -> None:
    """Check if a relation exists in a class and raise an error if not"""
    if relation not in model.classes[class_name].relations:
        raise ModelAssumptionError(
            f"Relation property {relation} not found in class {class_name}."
        )


def assert_only_direct_relations(*, path: RelationPath) -> None:
    """Ensure that only direct relations are supported which should be the case if the
    relation path only contains one path element.
    """
    num_elements = len(path.elements)
    if num_elements != 1:
        raise ModelAssumptionError(
            f"The provided relation path {path.path_str}"
            f"does not describe a direct relation, but contains {num_elements}"
            + " different relations"
        )


def assert_class_is_source(
    *, path: RelationPath, instruction: InstructionProtocol
) -> None:
    """Iterate over the elements of the relation path in the given instruction
    and validate that the class being modified matches the class specified in the
    relation path.
    """
    for path_element in path.elements:
        _validate_modification_class(path_element, instruction.class_name)


def _validate_modification_class(
    path_element: RelationPathElement, expected_class_name: str
) -> None:
    """Check whether the class specified to be modified matches the source or target
    class in the provided `path_element`, depending on the type of the relation path
    (i.e., active or passive). If the class does not match, an exception is raised.
    """
    modification_class_name = (
        path_element.source
        if path_element.type_ == RelationPathElementType.ACTIVE
        else path_element.target
    )
    if expected_class_name != modification_class_name:
        raise ModelAssumptionError(
            f"Class {expected_class_name} does not correspond to the relation source "
            f"{modification_class_name}."
        )


def assert_object_path_required(json_schema: Mapping[str, Any], path: str) -> None:
    """Ensures that a given object path in a JSON schema is marked as required.
    This validates that any transformation relying on that path can depend on its
    presence in a datapack.

    If the path is an empty string, no validation is required.
    """
    if not path:
        return
    for key in path.split("."):
        required_keys = json_schema.get("required", [])
        if key not in required_keys:
            raise ModelAssumptionError(f"'{key}' is not marked as required.")
        json_schema = json_schema["properties"][key]


def assert_object_path_exists(
    *,
    model: SchemaPack,
    instruction: InstructionProtocol,
) -> None:
    """Make sure that the source class (the class being modified) and the object_path
    exist in the model, and object_path properties are marked as required.
    Assumption fails if the content path is present in the model before the transformation.
    """
    class_name = instruction.class_name
    class_def = model.classes.get(class_name)

    # Check if the class exists in the model
    if not class_def:
        raise ModelAssumptionError(f"Class {class_name} does not exist in the model.")

    # Check if the object_path already exists in the model
    try:
        target_schema = resolve_schema_object_path(
            json_schema=class_def.content,
            path=instruction.target_content.object_path,
        )
    except KeyError as exc:
        raise ModelAssumptionError(
            f"Object path {instruction.target_content.object_path} does not exist"
            + f" in class {class_name}."
        ) from exc
    else:
        assert_object_path_required(
            json_schema=class_def.content,
            path=instruction.target_content.object_path,
        )
    # Check if the property_name already exists in the model and raise an error if so
    if instruction.target_content.property_name in target_schema.get("properties", {}):
        raise ModelAssumptionError(
            f"Property {instruction.target_content.property_name} already exists"
            + f" in class {class_name}."
        )


def assert_target_multiplicity(*, model: SchemaPack, path: RelationPath) -> None:
    """Make sure the target of the relation contributes multiple instances to the relation."""
    for path_element in path.elements:
        if path_element.type_ == RelationPathElementType.ACTIVE:
            relation = model.classes[path_element.source].relations[
                path_element.property
            ]
            if not relation.multiple.target:
                raise MultiplicityError(
                    f"The target of the relation {path_element.property} does not"
                    + " contribute multiple instances to the relation."
                )
