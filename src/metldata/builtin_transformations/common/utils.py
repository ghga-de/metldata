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


import json
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from schemapack import dumps_datapack, dumps_schemapack
from schemapack._internals.spec.datapack import Resource
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack


def model_to_dict(
    model: SchemaPack,
) -> dict[str, Any]:
    """Converts the provided SchemaPack model to a JSON-serializable dictionary.

    Returns:
        A dictionary representation of the provided model.
    """
    return json.loads(dumps_schemapack(deepcopy(model), yaml_format=False))


def data_to_dict(data:DataPack):
    """Converts the provided DataPack data to a JSON-serializable dictionary.

    Returns:
        A dictionary representation of the provided data.
        """
    return json.loads(dumps_datapack(deepcopy(data), yaml_format=False))


def thaw_content(frozen_dict: Mapping ) -> dict:
    """Recursively convert a nested FrozenDict, frozenset to mutable types.
    This will be removed after we implement a FrozenDict validation to Schemapack lib.
    """
    if isinstance(frozen_dict, Mapping):
        return {key: thaw_content(value) for key, value in frozen_dict.items()}
    elif isinstance(frozen_dict, tuple):
        return [thaw_content(item) for item in frozen_dict]
    return frozen_dict

