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

"""Helpers for deriving modified DataPacks via structural sharing (path copying).

DataPack instances are deeply frozen. Instead of converting the whole pack into
mutable dictionaries and re-validating the result (which costs time and memory
proportional to the entire dataset on every transformation step), these helpers
construct new frozen objects only along the path from the DataPack root to the
values that actually change. Everything else is shared by reference with the
input, which is safe precisely because it is immutable. Nothing is ever thawed
or mutated; the input DataPack remains valid and unchanged.

Since ``model_copy`` bypasses pydantic validation, these helpers must uphold the
field types themselves (in particular wrapping mappings in ``FrozenDict``), and
callers remain responsible for datapack-level invariants such as referential
integrity. Small nested models such as ``ResourceRelation`` are still validated
on construction.
"""

from collections.abc import Mapping

from arcticfreeze import FrozenDict
from schemapack.spec.custom_types import ResourceId
from schemapack.spec.datapack import DataPack, Resource


def set_class_resources(
    *, data: DataPack, class_name: str, resources: Mapping[ResourceId, Resource]
) -> DataPack:
    """Return a new DataPack in which ``class_name`` holds the given resources.

    If the class already exists in the input DataPack, it is replaced;
    otherwise it is added. All other classes are shared by reference with the
    input DataPack rather than copied.
    """
    all_resources = dict(data.resources)
    all_resources[class_name] = FrozenDict(resources)
    return data.model_copy(update={"resources": FrozenDict(all_resources)})
