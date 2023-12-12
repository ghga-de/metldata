# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Logic for transforming metadata models."""

from contextlib import suppress

from schemapack.spec.schemapack import (
    ClassDefinition,
    SchemaPack,
)
from schemapack.utils import FrozenDict

from metldata.schemapack_.transform.base import EvitableTransformationError


def delete_properties(
    *, model: SchemaPack, properties_by_class: dict[str, list[str]]
) -> SchemaPack:
    """Delete content properties from a model.

    Args:
        model:
            The model based on SchemaPack to add the inferred relations to.
        properties_by_class:
            A dictionary mapping class names to lists of content properties to delete.

    Returns:
        The model with the specified content properties being deleted.
    """

    updated_class_defs: dict[str, ClassDefinition] = {}
    for class_name, properties in properties_by_class.items():
        class_def = model.classes.get(class_name)

        if not class_def:
            raise EvitableTransformationError()

        content_schema = class_def.content.json_schema_dict

        for property in properties:
            if not "properties" in content_schema:
                raise EvitableTransformationError()

            content_schema["properties"].pop(property, None)

            if "required" in content_schema:
                with suppress(ValueError):
                    content_schema["required"].remove(property)

        updated_class_defs[class_name] = class_def.model_validate(
            {**class_def.model_dump(), "content": content_schema}
        )

    return model.model_copy(
        update={"classes": FrozenDict({**model.classes, **updated_class_defs})}
    )
