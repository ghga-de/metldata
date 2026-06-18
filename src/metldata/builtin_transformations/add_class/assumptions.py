# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Assumptions for the 'add class' transformation."""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_class.config import (
    AddClassConfig,
)
from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    check_class_does_not_exist,
    check_class_exists,
)
from metldata.transform.exceptions import ModelAssumptionError


def check_model_assumptions(model: SchemaPack, config: AddClassConfig) -> None:
    """Check model assumptions for the add class transformation."""
    # Check that the new class does not already exist in the model
    check_class_does_not_exist(model=model, class_name=config.class_name)
    check_globally_unique_ids(model=model)

    # Check that the target classes of relations exist in the model."""
    for relation in config.relations:
        check_class_exists(model=model, class_name=relation.targetClass)


def check_globally_unique_ids(model: SchemaPack) -> None:
    """Check that the input model does not contain duplicate resource ids across classes.
    Not conforming to globally unique id would cause ambiguities when mapping the
    relations of the new class to the existing resources.
    """
    if not model.globallyUniqueIds:
        raise ModelAssumptionError(
            "The input model must have globally unique ids across all classes to use"
            "the 'add class' transformation. Please ensure that the 'globallyUniqueIds'"
            "flag is set to True in the model."
        )
