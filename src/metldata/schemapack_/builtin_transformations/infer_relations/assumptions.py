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

"""Check model assumptions."""

from schemapack.spec.schemapack import SchemaPack

from metldata.schemapack_.builtin_transformations.infer_relations.path.path import (
    RelationPath,
)
from metldata.schemapack_.builtin_transformations.infer_relations.path.path_elements import (
    RelationPathElementType,
)
from metldata.schemapack_.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)
from metldata.schemapack_.transform.base import ModelAssumptionError


def assert_path_classes_and_relations(model: SchemaPack, path: RelationPath):
    """Make sure that all classes and relations defined in the provided path exist in
    the provided model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    for path_element in path.elements:
        if not path_element.source in model.classes:
            raise ModelAssumptionError(
                f"Class {path_element.source} not found in model."
            )

        if not path_element.target in model.classes:
            raise ModelAssumptionError(
                f"Class {path_element.target} not found in model."
            )

        if path_element.type_ == RelationPathElementType.ACTIVE:
            if (
                not path_element.property
                in model.classes[path_element.source].relations
            ):
                raise ModelAssumptionError(
                    f"Relation property {path_element.property} not found in class"
                    f" {path_element.source}."
                )

            return

        if not path_element.property in model.classes[path_element.target].relations:
            raise ModelAssumptionError(
                f"Relation property {path_element.property} not found in class"
                f" {path_element.target}."
            )


def assert_new_property_not_exists(
    model: SchemaPack, instruction: InferenceInstruction
) -> None:
    """Make sure that new property specified in the instruction does not yet exist in
    the model. The existence of the source class is not checked.
    """
    source_class = model.classes.get(instruction.source)
    if source_class and instruction.new_property in source_class.relations:
        raise ModelAssumptionError(
            f"Property '{instruction.new_property}' of class '{instruction.source}'"
            + ", intended to store an inferred relation, does already exist."
        )


def assert_instructions_match_model(
    *,
    model: SchemaPack,
    instructions: list[InferenceInstruction],
) -> None:
    """Make sure that the provided inference instructions can be applied to the provided
    model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    for instruction in instructions:
        assert_path_classes_and_relations(model=model, path=instruction.path)
        assert_new_property_not_exists(model=model, instruction=instruction)
