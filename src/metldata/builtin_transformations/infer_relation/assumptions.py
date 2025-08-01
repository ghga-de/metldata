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

"Assumptions for the infer relation transformation."

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    assert_path_classes_and_relations_exist,
    assert_relation_does_not_exist,
)
from metldata.builtin_transformations.common.path.path import RelationPath


def check_model_assumptions(
    *,
    model: SchemaPack,
    class_name: str,
    relation_name: str,
    relation_path: RelationPath,
) -> None:
    """Check model assumptions for the infer relation transformation."""
    assert_path_classes_and_relations_exist(model=model, path=relation_path)
    # check if newly inferred relation already exists and if so, raise an error
    assert_relation_does_not_exist(
        model=model,
        class_name=class_name,
        relation_name=relation_name,
    )
