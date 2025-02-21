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

"Combines functions controlling target-instruction dependent common assumptions."

from collections.abc import Mapping
from typing import Any

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.instruction import (
    TargetInstructionProtocol,
)
from metldata.builtin_transformations.common.model_transform import (
    resolve_schema_object_path,
)
from metldata.transform.exceptions import ModelAssumptionError


def assert_object_path_required(json_schema: Mapping[str, Any], path: str) -> None:
    """Ensures that a given object path in a JSON schema is marked as required.
    This validates that any transformation relying on that path can depend on its
    presence in a datapack.

    If the path is an empty string, no validation is required.
    """
    if not path:
        return
    for key in path.split("."):
        required_keys = json_schema.get("required", [])
        if key not in required_keys:
            raise ModelAssumptionError(f"'{key}' is not marked as required.")
        json_schema = json_schema["properties"][key]


def assert_object_path_exists(
    *,
    model: SchemaPack,
    instruction: TargetInstructionProtocol,
) -> None:
    """Make sure that the source class (the class being modified) and the object_path
    exist in the model, and object_path properties are marked as required.
    Assumption fails if the content path is present in the model before the transformation.
    """
    class_name = instruction.class_name
    class_def = model.classes.get(class_name)

    # Check if the class exists in the model
    if not class_def:
        raise ModelAssumptionError(f"Class {class_name} does not exist in the model.")

    # Check if the object_path already exists in the model
    try:
        target_schema = resolve_schema_object_path(
            json_schema=class_def.content,
            path=instruction.target_content.object_path,
        )
    except KeyError as exc:
        raise ModelAssumptionError(
            f"Object path {instruction.target_content.object_path} does not exist"
            + f" in class {class_name}."
        ) from exc
    else:
        assert_object_path_required(
            json_schema=class_def.content,
            path=instruction.target_content.object_path,
        )
    # Check if the property_name already exists in the model and raise an error if so
    if instruction.target_content.property_name in target_schema.get("properties", {}):
        raise ModelAssumptionError(
            f"Property {instruction.target_content.property_name} already exists"
            + f" in class {class_name}."
        )
