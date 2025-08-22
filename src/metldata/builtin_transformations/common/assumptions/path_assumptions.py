# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"Combines functions controlling Path dependent common assumptions."

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.builtin_transformations.common.utils import get_relation
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
        check_class_exists(model=model, class_name=path_element.source)
        check_class_exists(model=model, class_name=path_element.target)

        if path_element.type_ == RelationPathElementType.ACTIVE:
            check_relation_exists(
                model=model,
                class_name=path_element.source,
                relation=path_element.property,
            )

        if path_element.type_ == RelationPathElementType.PASSIVE:
            check_relation_exists(
                model=model,
                class_name=path_element.target,
                relation=path_element.property,
            )


def check_class_exists(*, model: SchemaPack, class_name: str) -> None:
    """Check if a class exists in the model and raise an error if not"""
    if class_name not in model.classes:
        raise ModelAssumptionError(f"Class {class_name} not found in model.")


def check_class_does_not_exist(*, model: SchemaPack, class_name: str) -> None:
    """Ensure a class does not exist in the model and raise an error else"""
    if class_name in model.classes:
        raise ModelAssumptionError(f"Unexcpected class {class_name} found in model.")


def check_relation_exists(*, model: SchemaPack, class_name: str, relation: str) -> None:
    """Check if a relation exists in a class and raise an error if not"""
    if relation not in model.classes[class_name].relations:
        raise ModelAssumptionError(
            f"Relation property {relation} not found in class {class_name}."
        )


def assert_relation_does_not_exist(
    *, model: SchemaPack, class_name: str, relation_name: str
) -> None:
    """Ensure a relation does not exist in a class and raise an error else."""
    if relation_name in model.classes[class_name].relations:
        raise ModelAssumptionError(
            f"Unexpected relation property {relation_name} found in class {class_name}."
        )


def assert_relation_target_multiplicity(
    *, model: SchemaPack, path: RelationPath
) -> None:
    """Make sure the target of the relation contributes multiple instances to the relation."""
    for element in path.elements:
        relation = get_relation(element, model)
        if element.type_ == RelationPathElementType.ACTIVE and relation.multiple.target:
            return
        if (
            element.type_ == RelationPathElementType.PASSIVE
            and relation.multiple.origin
        ):
            return

    raise MultiplicityError(
        f"Along the path {path} there is no target that contributes"
        + " multiple instances to the relation"
    )


def assert_no_relation_target_multiplicity(
    *, model: SchemaPack, path: RelationPath
) -> None:
    """Make sure relation targets contribute no more than one instance to the relation."""
    for element in path.elements:
        relation = get_relation(element, model)
        if element.type_ == RelationPathElementType.ACTIVE and relation.multiple.target:
            raise MultiplicityError(
                "Encountered target contributing multiple instances to a relation"
                + f" along path {path} while no multiplicity was expected."
            )
        if (
            element.type_ == RelationPathElementType.PASSIVE
            and relation.multiple.origin
        ):
            raise MultiplicityError(
                "Encountered target contributing multiple instances to a relation"
                + f" along path {path} while no multiplicity was expected."
            )
