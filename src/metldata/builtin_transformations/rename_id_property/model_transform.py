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

"""Model transformation logic for the 'rename id property' transformation"""

from schemapack.spec.schemapack import IDSpec, SchemaPack

from metldata.builtin_transformations.common.utils import model_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def rename_model_id_property(
    *,
    model: SchemaPack,
    class_name: str,
    id_property_name: str,
    description: str | None,
) -> SchemaPack:
    """Rename the id property of the model."""
    mutable_model = model_to_dict(model)
    try:
        mutable_model["classes"][class_name]["id"] = IDSpec(
            propertyName=id_property_name,
            description=description,
        )
    except KeyError as exc:
        raise EvitableTransformationError() from exc
    return SchemaPack.model_validate(mutable_model)
