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
"Resolve (nested) object paths and return the appropriate property or subschema."

from collections.abc import Mapping
from typing import Any


def resolve_data_object_path(data: Mapping, path: str) -> Any:
    """Given a mapping, resolve the dot-separated path to a property. Return the
    property value.

    Args:
        data:
            The JSON object.
        path:
            The dot-separated path to the property.

    Raises:
        KeyError:
            If the path does not exist in the data.

    Returns: The value of the property at the given path.
    """
    if path:
        for key in path.split("."):
            data = data[key]
    return data


def resolve_schema_object_path(json_schema: Mapping[str, Any], path: str) -> Any:
    """Given a JSON schema describing an object, resolve the dot-separated path to a
    property. Return the property schema.

    Args:
        json_schema:
            The JSON schema of the object.
        path:
            The dot-separated path to the property.

    Raises:
        KeyError:
            If the path does not exist in the schema.

    Returns: The schema of the property at the given path.
    """
    if path:
        for key in path.split("."):
            json_schema = json_schema["properties"][key]
    return json_schema
