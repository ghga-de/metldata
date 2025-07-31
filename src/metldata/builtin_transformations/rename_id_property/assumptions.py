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

"Assumptions for the `rename id property` transformation"

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    check_class_exists,
)
from metldata.transform.exceptions import ModelAssumptionError


def check_model_assumptions(
    model: SchemaPack, class_name: str, new_id_property: str
) -> None:
    """Check model assumptions for the `rename id property` transformation."""
    check_class_exists(model=model, class_name=class_name)
    check_id_is_different_from_existing(
        model=model,
        class_name=class_name,
        new_id_property=new_id_property,
    )


def check_id_is_different_from_existing(
    model: SchemaPack, class_name: str, new_id_property: str
) -> None:
    """Check that the current id is not the same as the new one."""
    existing_id_property = model.classes[class_name].id.propertyName
    if existing_id_property == new_id_property:
        raise ModelAssumptionError(
            f"The id property '{new_id_property}' already exists in the model."
        )
