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
#

"""Data models."""

from typing import TypeAlias, TypedDict

from metldata.custom_types import Json


class ArtifactJson(TypedDict):
    """A model representing a single artifact instance.

    The content is a JSON object containing the resources of the artifact.
    """

    study_accession: str
    artifact_name: str
    content: Json


# A dictionary of artifacts. The keys on the first correspond to artifact names.
# The values are lists of artifact instances for different submissions.
ArtifactResourceDict: TypeAlias = dict[str, list[ArtifactJson]]
