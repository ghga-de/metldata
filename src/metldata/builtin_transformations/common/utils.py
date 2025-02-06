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

"""Helper functions to transform Schemapack models and Datapack data
into JSON-serializable dictionaries, as well as thawing frozen structures.
"""

import json
from typing import Any

from schemapack import dumps_datapack, dumps_schemapack
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import (
    ClassDefinition,
    Relation,
    SchemaPack,
)

from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElement,
    RelationPathElementType,
)


def model_to_dict(model: SchemaPack) -> dict[str, Any]:
    """Converts the provided SchemaPack model to a dictionary."""
    return json.loads(dumps_schemapack(model, yaml_format=False))


def data_to_dict(data: DataPack) -> dict[str, Any]:
    """Converts the provided DataPack data to a dictionary."""
    return json.loads(dumps_datapack(data, yaml_format=False))


def content_to_dict(class_def: ClassDefinition) -> dict[str, Any]:
    """Converts a content schema into a dictionary."""
    class_def_dict = json.loads(class_def.model_dump_json())
    return class_def_dict["content"]


def relations_to_dict(class_def: ClassDefinition) -> dict[str, Any]:
    """Converts a relation schema into a dictionary."""
    class_def_dict = json.loads(class_def.model_dump_json())
    return class_def_dict["relations"]


def get_relation(element: RelationPathElement, schema: SchemaPack) -> Relation:
    """Get the relation object for a path element.

    Args:
        element: The path element to get the relation for.
        schema: The underlying schema.

    Returns:
        The relation object.
    """
    element_active = element.type_ == RelationPathElementType.ACTIVE
    class_name = element.source if element_active else element.target
    return schema.classes[class_name].relations[element.property]
