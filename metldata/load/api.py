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

"""API for loading artifacts into running services."""

from fastapi import HTTPException
from fastapi.routing import APIRouter
from hexkit.protocols.dao import DaoFactoryProtocol

from metldata.artifacts_rest.artifact_dao import ArtifactDaoCollection
from metldata.artifacts_rest.artifact_info import get_artifact_info_dict
from metldata.artifacts_rest.load_resources import load_artifact_resources
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

    for artifact_name in artifact_resources.values():
        if not artifact_name in artifact_infos:
            raise ArtifactResourcesInvalid(f"Artifact '{artifact_name}' is unknown.")


async def load_artifacts_using_dao(
    artifact_resources: ArtifactResourceDict,
    artifact_info_dict: dict[str, ArtifactInfo],
    dao_collection: ArtifactDaoCollection,
) -> None:
    """Load artifact resources from multiple submissions using the given dao collection."""

    for artifact_name, artifact_contents in artifact_resources.items():
        for artifact_content in artifact_contents:
            await load_artifact_resources(
                artifact_content=artifact_content,
                artifact_info=artifact_info_dict[artifact_name],
                dao_collection=dao_collection,
            )


async def rest_api_factory(
    *, artifact_infos: list[ArtifactInfo], dao_factory: DaoFactoryProtocol
) -> APIRouter:
    """Return a router for an API for loading artifacts."""

    artifact_info_dict = get_artifact_info_dict(artifact_infos=artifact_infos)
    dao_collection = await ArtifactDaoCollection.construct(
        dao_factory=dao_factory, artifact_infos=artifact_infos
    )

    router = APIRouter()

    @router.post("/rpc/load_artifacts")
    async def load_artifacts(artifact_resources: ArtifactResourceDict):
        """Load artifacts into running services."""

        try:
            check_artifact_resources(
                artifact_resources=artifact_resources, artifact_infos=artifact_info_dict
            )
        except ArtifactResourcesInvalid as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        await load_artifacts_using_dao(
            artifact_resources=artifact_resources,
            artifact_info_dict=artifact_info_dict,
            dao_collection=dao_collection,
        )
