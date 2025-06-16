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

"""Data transformation logic for the `transform content` transformation"""

import yaml
from jinja2.sandbox import ImmutableSandboxedEnvironment
from schemapack import denormalize, isolate_resource
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.transform_content.config import (
    TransformContentConfig,
)
from metldata.transform.exceptions import EvitableTransformationError

env = ImmutableSandboxedEnvironment()


def _format_denormalized(denormalized_content: dict[str, object]) -> dict[str, object]:
    """TODO"""
    top_resource_id = denormalized_content.pop("alias")
    content = {top_resource_id: {"content": dict()}}  # type: ignore
    for key, value in denormalized_content.items():
        if isinstance(value, list) and isinstance(value[0], dict):
            content[top_resource_id]["content"][key] = [
                _format_denormalized(resource_content) for resource_content in value
            ]
        else:
            content[top_resource_id]["content"][key] = value
    return content  # type: ignore


def transform_data_class(
    *,
    data: DataPack,
    schemapack: SchemaPack,
    transformation_config: TransformContentConfig,
) -> DataPack:
    """Denormalize data using the configured class as root and perform content data transformation."""
    class_name = transformation_config.class_name
    embedding_profile = transformation_config.embedding_profile
    resource_id = transformation_config.resource_id

    rooted_datapack = isolate_resource(
        datapack=data,
        class_name=class_name,
        resource_id=resource_id,
        schemapack=schemapack,
    )
    denormalized_content = denormalize(
        datapack=rooted_datapack,
        schemapack=schemapack,
        embedding_profile=embedding_profile,
    )
    denormalized_content = _format_denormalized(denormalized_content)
    rooted_data = data_to_dict(rooted_datapack)

    transformed_data = env.from_string(transformation_config.data_template).render(
        original=denormalized_content[transformation_config.resource_id]
    )

    try:
        rooted_data["resources"][class_name][resource_id] = yaml.safe_load(
            transformed_data
        )
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    return DataPack.model_validate(rooted_data)
