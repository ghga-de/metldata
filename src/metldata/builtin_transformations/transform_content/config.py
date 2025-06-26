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

"""Configuration for the `transform content` transformation."""

from typing import Annotated, Any

import yaml
from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings

from metldata.builtin_transformations.common.utils import EmbeddingProfile


def convert_dict_compatible(value: Any) -> Any:
    """Convert json serialized representation to dict."""
    if isinstance(value, str) and value.startswith("{"):
        return yaml.safe_load(value)
    return value


class TransformContentConfig(BaseSettings):
    """A config for arbitrary modifications of content schemas and data."""

    class_name: str = Field(
        default=...,
        description="Name of the class containing the content to be transformed.",
    )
    content_schema: Annotated[
        dict[str, object], BeforeValidator(convert_dict_compatible)
    ] = Field(
        default=...,
        description="Schemapack compatible JSON Schema the transformed content needs to adhere to.",
    )
    embedding_profile: Annotated[
        EmbeddingProfile, BeforeValidator(convert_dict_compatible)
    ] = Field(
        default=...,
        description="Embedding profile for denormalization. All relations are embedded by default and nested relations need to be specified explicitly for exclusion.",
    )
    data_template: str = Field(
        default=...,
        description="Jinja template used to transform existing content data.",
    )
