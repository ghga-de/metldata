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

from metldata.builtin_transformations.common.model_transform import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.delete_content_subschema.instruction import (
    DeleteContentSubschemaInstruction,
)
from metldata.transform.exceptions import ModelAssumptionError


def assert_classes_and_properties_exist(
    *,
    schema: SchemaPack,
    instructions_by_class: dict[str, list[DeleteContentSubschemaInstruction]],
) -> None:
    """Assert that all classes and properties exist in the model.

    Args:
        model:
            The model based on SchemaPack to check.
        instructions_by_class:
            A dictionary mapping class names to instructions describing which content should be deleted.

    Raises:
        ModelAssumptionError:
            If the assumptions are not met.
    """
    for class_name, instructions in instructions_by_class.items():
        class_def = schema.classes.get(class_name)

        if not class_def:
            raise ModelAssumptionError(
                f"Class to be modified {class_name} does not exist in the model."
            )

        for instruction in instructions:
            # Ensure the property schema at the given path exists in the model
            try:
                _ = resolve_schema_object_path(
                    json_schema=class_def.content,
                    path=instruction.content_path,
                )
            except KeyError as exc:
                raise ModelAssumptionError(
                    f"No property exists at the given content path {instruction.content_path}"
                ) from exc
