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
#

"""Check model assumptions."""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions import (
    assert_path_classes_and_relations_exist,
)
from metldata.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)
from metldata.transform.exceptions import ModelAssumptionError


def assert_new_property_not_exists(
    model: SchemaPack, instruction: InferenceInstruction
) -> None:
    """Make sure that new property specified in the instruction does not yet exist in
    the model. The existence of the source class is not checked.
    """
    source_class = model.classes.get(instruction.source)
    if source_class and instruction.new_property in source_class.relations:
        raise ModelAssumptionError(
            f"Property {instruction.new_property} of class {instruction.source}"
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
        assert_path_classes_and_relations_exist(model=model, path=instruction.path)
        assert_new_property_not_exists(model=model, instruction=instruction)
