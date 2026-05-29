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

"""Model transformation logic for the 'set id uniqueness scope' transformation."""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import model_to_dict


def set_id_uniqueness_scope_on_schema(
    *, model: SchemaPack, globally_unique_ids: bool
) -> SchemaPack:
    """Set globallyUniqueIds on the schema to the given value."""
    mutable_model = model_to_dict(model)
    mutable_model["globallyUniqueIds"] = globally_unique_ids
    return SchemaPack.model_validate(mutable_model)
