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

"""Check model assumptions for the sum operation transformation"""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions import (
    assert_class_is_source,
    assert_object_path_exists,
    assert_path_classes_and_relations_exist,
    assert_relation_target_multiplicity,
)
from metldata.builtin_transformations.count_content_values.assumptions import (
    assert_source_content_path_exists,
)
from metldata.builtin_transformations.sum_operation.instruction import (
    SumOperationInstruction,
)
from metldata.transform.exceptions import ModelAssumptionError


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[SumOperationInstruction]],
) -> None:
    """Check the model assumptions for the sum operation transformation."""
    for _, instructions in instructions_by_class.items():
        for instruction in instructions:
            path = instruction.source.relation_path
            assert_path_classes_and_relations_exist(model=schema, path=path)
            assert_object_path_exists(model=schema, instruction=instruction)
            assert_relation_target_multiplicity(model=schema, path=path)
            assert_source_content_path_exists(schema=schema, instruction=instruction)
            assert_class_is_source(path=path, instruction=instruction)
            assert_data_type(schema, instruction)


def assert_data_type(schema: SchemaPack, instruction: SumOperationInstruction) -> None:
    """Ensure that the slot given as 'content path' of an instruction source
    has a data type allowing arithmetic operations.
    """
    path = instruction.source.relation_path
    content_path = instruction.source.content_path

    referenced_class = path.target

    class_def = schema.classes.get(referenced_class)

    if not class_def:
        raise ModelAssumptionError(
            f"Class {referenced_class} does not exist in the model."
        )

    content_slot = class_def.content["properties"].get(content_path)

    if content_slot["type"] not in {"integer", "number", "boolean"}:
        raise ModelAssumptionError(
            f"The type of the slot {content_slot} of class {referenced_class} does not"
            + " allow arithmetic operations."
        )
