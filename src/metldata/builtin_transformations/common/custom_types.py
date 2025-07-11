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


"""A collection of custom types used for builtin transformations."""

from collections.abc import Callable, Mapping
from typing import Any, TypeAlias

from metldata.builtin_transformations.common.path.path import RelationPath

ResourceId: TypeAlias = str
MutableDatapack: TypeAlias = dict[str, Any]
MutableResource: TypeAlias = dict[str, dict]
MutableClassResources: TypeAlias = dict[ResourceId, MutableResource]
MutableResourceContent: TypeAlias = dict[str, Any]
ResolveRelations: TypeAlias = Callable[
    [ResourceId, RelationPath], frozenset[ResourceId]
]
MutableClassRelations: TypeAlias = dict[str, dict]
# needs to be a TypeAliasType so Pydantic can deal with the recursive definition
type EmbeddingProfile = Mapping[str, "bool | EmbeddingProfile"] | None
