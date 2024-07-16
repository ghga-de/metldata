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

from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.transform.base import ModelAssumptionError


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

        if path_element.type_ == RelationPathElementType.ACTIVE:
            if (
                path_element.property
                not in model.classes[path_element.source].relations
            ):
                raise ModelAssumptionError(
                    f"Relation property {path_element.property} not found in class"
                    f" {path_element.source}."
                )

            return


def check_model_assumptions(schema: SchemaPack, instructions_by_class: Any) -> None:
    """Check the model assumptions for the count references transformation."""
    return None
