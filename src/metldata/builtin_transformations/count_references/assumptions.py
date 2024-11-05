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

from metldata.builtin_transformations.common.assumptions import (
    assert_class_is_source,
    assert_object_path_exists,
    assert_only_direct_relations,
    assert_path_classes_and_relations_exist,
    assert_target_multiplicity,
)
from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[AddReferenceCountPropertyInstruction]],
) -> None:
    """Check the model assumptions for the count references transformation."""
    for _, instructions in instructions_by_class.items():
        for instruction in instructions:
            path = instruction.source_relation_path
            assert_path_classes_and_relations_exist(model=schema, path=path)
            assert_only_direct_relations(path=path)
            assert_class_is_source(path=path, instruction=instruction)
            assert_object_path_exists(model=schema, instruction=instruction)
            assert_target_multiplicity(model=schema, path=path)
