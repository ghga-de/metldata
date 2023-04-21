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

"""Logic to build REST APIs for querying artifacts."""

from fastapi import HTTPException
from fastapi.routing import APIRouter

from metldata.artifacts_rest.artifact_info import ArtifactQueryInfo


def get_artifact_info_dict(
    *, artifact_infos: list[ArtifactQueryInfo]
) -> dict[str, ArtifactQueryInfo]:
    """Build a dictionary from artifact name to artifact info."""

    # check if artifact names are unique:
    artifact_names = [artifact_info.name for artifact_info in artifact_infos]
    if len(artifact_names) != len(set(artifact_names)):
        raise ValueError("Artifact names must be unique.")

    return {artifact_info.name: artifact_info for artifact_info in artifact_infos}


def artifact_rest_factory(*, artifact_infos: list[ArtifactQueryInfo]) -> APIRouter:
    """Factory to build a REST API for a querying the provided artifact.

    Args:
        artifact_info: Information on the artifact to build the REST API for.
    """

    artifact_info_dict = get_artifact_info_dict(artifact_infos=artifact_infos)

    router = APIRouter()

    @router.options("/artifacts")
    def get_artifacts_info() -> list[ArtifactQueryInfo]:
        """Get information on available artifacts."""

        return artifact_infos

    @router.options("/artifacts/{artifact_name}")
    def get_artifact_info(artifact_name: str) -> ArtifactQueryInfo:
        """Get information on the artifact with the given name."""

        artifact_info = artifact_info_dict.get(artifact_name)
        if artifact_info is None:
            raise HTTPException(status_code=404, detail="Artifact not found.")

        return artifact_info

    @router.get("/artifacts/{artifact_name}/resources/{resource_id}")
    def get_artifact_resource(artifact_name: str, resource_id: str):
        """Get the resource with the given id from the artifact with the given name."""

        raise NotImplementedError

    return router
