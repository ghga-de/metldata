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

"Assumptions for the merge relations transformation."

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    assert_relation_does_not_exist,
    check_class_exists,
    check_relation_exists,
)
from metldata.builtin_transformations.merge_relations.config import MergeRelationsConfig
from metldata.transform.exceptions import ModelAssumptionError


def check_model_assumptions(
    model: SchemaPack, transformation_config: MergeRelationsConfig
) -> None:
    """Check model assumptions for the merge relations transformation."""
    assert_class_and_relations_exists(
        model=model, transformation_config=transformation_config
    )
    # check if new relation already exists
    assert_relation_does_not_exist(
        model=model,
        class_name=transformation_config.class_name,
        relation_name=transformation_config.target_relation,
    )
    assert_same_target_class_across_relations(
        model=model, transformation_config=transformation_config
    )


def assert_class_and_relations_exists(
    *, model: SchemaPack, transformation_config: MergeRelationsConfig
) -> None:
    """Make sure that the class and relations defined in the configuration exist in the
    provided model.

    Raises:
        ModelAssumptionError:
            if the model does not fulfill the assumptions.
    """
    check_class_exists(model=model, class_name=transformation_config.class_name)
    for relation_name in transformation_config.source_relations:
        check_relation_exists(
            model=model,
            class_name=transformation_config.class_name,
            relation=relation_name,
        )


def assert_same_target_class_across_relations(
    *, model: SchemaPack, transformation_config: MergeRelationsConfig
):
    """Ensure that all source relations have the same target class."""
    class_relations = model.classes[transformation_config.class_name].relations
    target_classes = [
        class_relations[relation_name].targetClass
        for relation_name in transformation_config.source_relations
    ]
    if len(set(target_classes)) > 1:
        raise ModelAssumptionError(
            "All source relations must have the same target class, "
            f"but found: {set(target_classes)}"
        )
