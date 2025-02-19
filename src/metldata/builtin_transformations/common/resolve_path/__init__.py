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

"""Common relation and object path related functionality."""

from metldata.builtin_transformations.common.resolve_path.resolve_path_elements import (
    resolve_path,  # noqa: F401
)
from metldata.builtin_transformations.common.resolve_path.resolve_path_properties import (
    resolve_data_object_path,  # noqa: F401
    resolve_schema_object_path,  # noqa: F401
)
