# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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
#

"""Models used to describe embedding profiles."""

from pydantic import BaseSettings, Field, validator

from metldata.builtin_transformations.custom_embeddings.embedding_profile import (
    EmbeddingProfile,
)


class CustomEmbeddingConfig(BaseSettings):
    """Config to describe profiles for custom embeddings of classes from a metadata
    model."""

    embedding_profiles: list[EmbeddingProfile] = Field(
        ...,
        description=(
            "A list of custom embedding profiles for classes from a metadata model."
        ),
    )

    # pylint: disable=no-self-argument
    @validator("embedding_profiles")
    def check_embedding_profiles_unique(
        cls,
        value: list[EmbeddingProfile],
    ) -> list[EmbeddingProfile]:
        """Check that names for embedded classes are unique among the embedding_profiles."""

        embedded_classes: list[str] = []
        for profile in value:
            embedded_classes.append(profile.embedded_class)
            for referenced_profile in profile.embedded_references.values():
                if isinstance(referenced_profile, EmbeddingProfile):
                    embedded_classes.append(referenced_profile.embedded_class)

        if len(embedded_classes) != len(set(embedded_classes)):
            raise ValueError("Names for embedded classes must be unique.")

        return value
