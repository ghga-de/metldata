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

"""Model transformation logic for the `transform content` transformation"""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import model_to_dict
from metldata.builtin_transformations.transform_content.config import (
    TransformContentConfig,
)
from metldata.transform.exceptions import EvitableTransformationError


def transform_model_class(
    *,
    model: SchemaPack,
    transformation_config: TransformContentConfig,
) -> SchemaPack:
    """Replace the content schema with the schema given in the config."""
    class_name = transformation_config.class_name
    mutable_model = model_to_dict(model)

    try:
        mutable_model["classes"][class_name]["content"] = (
            transformation_config.content_schema
        )
        # need to explicitly delete relations, if there are any
        # else this will error due to duplicate keys in relations and content, as the
        # set of relation and content property names inside a class has to be unique
        if "relations" in mutable_model["classes"][class_name]:
            del mutable_model["classes"][class_name]["relations"]
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    return SchemaPack.model_validate(mutable_model)
