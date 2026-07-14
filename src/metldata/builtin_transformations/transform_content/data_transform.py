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

"""Data transformation logic for the `transform content` transformation"""

from collections.abc import Mapping

import yaml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from schemapack import denormalize, isolate_resource
from schemapack.spec.datapack import DataPack, Resource
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.custom_types import (
    EmbeddingProfile,
    ResourceId,
)
from metldata.builtin_transformations.common.mutate import set_class_resources
from metldata.transform.exceptions import EvitableTransformationError

# configure with StrictUndefined so invalid property/dict access produces errors
# instead of silently inserting a none value
env = SandboxedEnvironment(undefined=StrictUndefined)

# object is too broad for what _denormalization_workaround will accept, define
# something that's closer to the intention of JsonObjectCompatible
ResourceContent = list | str | tuple | Mapping


def transform_data_content(
    *,
    data: DataPack,
    schemapack: SchemaPack,
    class_name: str,
    content_template_yaml: str,
    embedding_profile: EmbeddingProfile,
) -> DataPack:
    """Denormalize data using the configured class as root and perform content data transformation."""
    if class_name not in data.resources:
        raise EvitableTransformationError()

    # loop-invariant: the template and these class-level names do not depend on the
    # individual resource, so compile/compute them once before iterating.
    template = env.from_string(content_template_yaml)
    id_property_name = schemapack.classes[class_name].id.propertyName
    content_property_names = list(
        schemapack.classes[class_name].content["properties"].keys()
    )
    relation_property_names = list(schemapack.classes[class_name].relations.keys())

    updated_resources: dict[ResourceId, Resource] = {}
    for resource_id, resource in data.resources[class_name].items():
        # while isolating and thus rooting the datapack here, the way this is applied
        # to all resources will result in a datapack that IS NOT rooted
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

        # evaluate data template using jinja
        transformed_content = template.render(
            original=denormalized_content,
            id_property_name=id_property_name,
            content_property_names=content_property_names,
            relation_property_names=relation_property_names,
        )

        # replace resource content with the transformed version; the rendered
        # content comes from a user-supplied template, so it is validated (and
        # thereby deeply frozen) on construction, while the resource's existing
        # relations pass through by reference
        updated_resources[resource_id] = Resource.model_validate(
            {
                "content": yaml.safe_load(transformed_content),
                "relations": resource.relations,
            }
        )

    return set_class_resources(
        data=data, class_name=class_name, resources=updated_resources
    )
