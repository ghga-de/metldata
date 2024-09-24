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
#

"""Check model assumptions."""

from schemapack.spec.schemapack import SchemaPack

from metldata.transform.base import ModelAssumptionError


def assert_classes_and_properties_exist(
    *, model: SchemaPack, properties_by_class: dict[str, list[str]]
) -> None:
    """Assert that all classes and properties exist in the model.

    Args:
        model:
            The model based on SchemaPack to check.
        properties_by_class:
            A dictionary mapping class names to lists of content properties to delete.

    Raises:
        ModelAssumptionError:
            If the assumptions are not met.
    """
    for class_name, properties in properties_by_class.items():
        if class_name not in model.classes:
            raise ModelAssumptionError(
                f"Class {class_name} does not exist in the model."
            )

        for property in properties:
            if property not in model.classes[class_name].content.json_schema_dict.get(
                "properties", {}
            ):
                raise ModelAssumptionError(
                    f"Property {property} does not exist in class {
                        class_name}."
                )
