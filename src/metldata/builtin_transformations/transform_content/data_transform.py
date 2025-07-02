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

from collections.abc import Mapping

import yaml
from jinja2 import StrictUndefined
from jinja2.sandbox import ImmutableSandboxedEnvironment
from schemapack import denormalize, isolate_resource
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.transform_content.config import (
    TransformContentConfig,
)
from metldata.transform.exceptions import EvitableTransformationError

env = ImmutableSandboxedEnvironment(undefined=StrictUndefined)


def _format_denormalized(denormalized_content: dict[str, object]) -> dict[str, object]:
    """Reformat denormalized content for attachment into datapack.

    This does not convert the alias based representation back into a resource ID to
    resource mapping, but only converts frozen dicts back into normal dictionaries
    to work around a schemapack isssue for now.
    """
    content = dict()

    for key, value in denormalized_content.items():
        if (
            isinstance(value, list | tuple)
            and len(value) > 0
            and isinstance(value[0], Mapping)
        ):
            content[key] = [
                _format_denormalized(resource_content) for resource_content in value
            ]
        elif isinstance(value, Mapping):
            content[key] = _format_denormalized(value)  # type: ignore
        elif isinstance(value, tuple):
            content[key] = [resource_content for resource_content in value]
        else:
            content[key] = value  # type: ignore
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

    mutable_data = data_to_dict(data)

    if class_name not in data.resources:
        raise EvitableTransformationError()

    for resource_id in data.resources[class_name]:
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

        # remove the top level alias before embedding
        del denormalized_content["alias"]
        denormalized_content = _format_denormalized(denormalized_content)

        transformed_content = env.from_string(
            transformation_config.data_template
        ).render(original=denormalized_content)

        mutable_data["resources"][class_name][resource_id]["content"] = yaml.safe_load(
            transformed_content
        )
        # prune relations from data as these are also removed from the model and
        # the set of relation and content property names inside a class has to be unique
        if "relations" in mutable_data["resources"][class_name][resource_id]:
            del mutable_data["resources"][class_name][resource_id]["relations"]

    return DataPack.model_validate(mutable_data)
