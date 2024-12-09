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
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from schemapack import dumps_datapack, dumps_schemapack
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack


def model_to_dict(model: SchemaPack) -> dict[str, Any]:
    """Converts the provided SchemaPack model to a dictionary."""
    return json.loads(dumps_schemapack(model, yaml_format=False))


def data_to_dict(data: DataPack) -> dict[str, Any]:
    """Converts the provided DataPack data to a dictionary."""
    return json.loads(dumps_datapack(data, yaml_format=False))


def _thaw_content(frozen_dict: Mapping | tuple) -> dict:
    """Recursively converts a nested FrozenDict and frozenset to mutable types.
    This will be removed after we implement a FrozenDict validation to Schemapack lib.
    """
    if isinstance(frozen_dict, Mapping):
        return {key: _thaw_content(value) for key, value in frozen_dict.items()}
    elif isinstance(frozen_dict, tuple):
        return [_thaw_content(item) for item in frozen_dict]  # type: ignore
    return frozen_dict
