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

"""Logic for loading artifact resources."""


from metldata.artifacts_rest.artifact_dao import ArtifactDaoCollection
from metldata.artifacts_rest.load_resources import (
    extract_all_resources_from_artifact,
    load_artifact_resources,
)
from metldata.artifacts_rest.models import ArtifactInfo
from metldata.load.models import ArtifactResourceDict


class ArtifactResourcesInvalid(RuntimeError):
    """Raised when artifact resources are invalid."""


def check_artifact_resources(
    artifact_resources: ArtifactResourceDict, artifact_infos: dict[str, ArtifactInfo]
) -> None:
    """Check the provided artifact resources against the given artifact info.

    Raises:
        ArtifactResourcesInvalid: If the artifact resources are invalid.
    """

    for artifact_name in artifact_resources:
        if artifact_name not in artifact_infos:
            raise ArtifactResourcesInvalid(f"Artifact '{artifact_name}' is unknown.")


async def get_current_artifacts_using_dao(dao_collection) -> None:
    """Get artifact resources currently present using the given dao collection"""


async def load_artifacts_using_dao(
    artifact_resources: ArtifactResourceDict,
    artifact_info_dict: dict[str, ArtifactInfo],
    dao_collection: ArtifactDaoCollection,
) -> None:
    """Load artifact resources from multiple submissions using the given dao collection."""

    existing_resources = await dao_collection.get_all_resource_ids()

    for artifact_name, artifact_contents in artifact_resources.items():
        for artifact_content in artifact_contents:
            resources = extract_all_resources_from_artifact(
                artifact_content=artifact_content,
                artifact_info=artifact_info_dict[artifact_name],
            )

            for resource in resources:
                

            await load_artifact_resources(
                artifact_content=artifact_content,
                artifact_info=artifact_info_dict[artifact_name],
                dao_collection=dao_collection,
            )
