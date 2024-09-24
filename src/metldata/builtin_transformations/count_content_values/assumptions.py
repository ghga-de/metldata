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

"""Check model assumptions for the count content values transformation."""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions import (
    assert_class_is_source,
    assert_multiplicity,
    assert_object_path_exists,
    assert_only_direct_relations,
    assert_path_classes_and_relations_exist,
)
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.builtin_transformations.count_content_values.instruction import (
    CountContentValueInstruction,
)
from metldata.transform.base import ModelAssumptionError


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[CountContentValueInstruction]],
) -> None:
    """Check the model assumptions for the add content properties transformation."""
    for _, instructions in instructions_by_class.items():
        for instruction in instructions:
            path = instruction.source.relation_path
            assert_path_classes_and_relations_exist(model=schema, path=path)
            assert_only_direct_relations(path=path)
            assert_class_is_source(path=path, instruction=instruction)
            assert_object_path_exists(model=schema, instruction=instruction)
            assert_multiplicity(model=schema, path=path)
            assert_source_content_path_exists(schema, instruction)


def assert_source_content_path_exists(
    schema: SchemaPack, instruction: CountContentValueInstruction
):
    """Ensure that the slot given as 'content path' of the source in the
    'count content values' transformation config exists in the content schema of
    the class that is referred in the 'relation path'.
    """
    path = instruction.source.relation_path
    content_path = instruction.source.content_path

    for path_element in path.elements:
        if path_element.type_ == RelationPathElementType.ACTIVE:
            # check if path.target has the slot content_path in the path.target's content schema
            referenced_class = path.target
        elif path_element.type_ == RelationPathElementType.PASSIVE:
            referenced_class = path.source

        class_def = schema.classes.get(referenced_class)

        if not class_def:
            raise ModelAssumptionError(
                f"Class {referenced_class} does not exist in the model."
            )

        content_slot = class_def.content.json_schema_dict.get(content_path)

        if not content_slot:
            raise ModelAssumptionError(
                f"Class {referenced_class} does not have {content_path} in its content schema."
            )
