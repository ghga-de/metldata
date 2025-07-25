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

"""DAO for managing artifacts."""

from typing import TypeAlias

from ghga_event_schemas.pydantic_ import Artifact
from hexkit.protocols.dao import Dao, DaoFactoryProtocol

from metldata.artifacts_rest.artifact_info import get_artifact_info_dict
from metldata.artifacts_rest.models import ArtifactInfo, ArtifactResource

ArtifactResourceDao: TypeAlias = Dao[ArtifactResource]
ArtifactDao: TypeAlias = Dao[Artifact]


class DaoNotFoundError(RuntimeError):
    """Raised when a DAO is not found."""

    def __init__(self, artifact_name: str, class_name: str):
        super().__init__(
            f"Could not find DAO for artifact '{artifact_name}' and class '{class_name}'."
        )


class ArtifactDaoCollection:
    """A collection of DAOs for managing artifacts and their resources."""

    @classmethod
    async def construct(
        cls,
        dao_factory: DaoFactoryProtocol,
        artifact_infos: list[ArtifactInfo],
        publishable_artifacts: list[str] | None = None,
    ):
        """Initialize the collection of DAOs."""
        artifact_info_dict = get_artifact_info_dict(artifact_infos=artifact_infos)

        # Cannot use comprehensions because of bug: https://bugs.python.org/issue33346
        artifact_resource_daos: dict[str, dict[str, ArtifactResourceDao]] = {}
        for artifact_name, artifact_info in artifact_info_dict.items():
            artifact_resource_daos[artifact_name] = {}
            for class_name in artifact_info.resource_classes:
                artifact_resource_daos[artifact_name][
                    class_name
                ] = await dao_factory.get_dao(
                    name=cls._get_dao_name(
                        artifact_name=artifact_name, class_name=class_name
                    ),
                    dto_model=ArtifactResource,
                    id_field="id_",
                )

        # Add a DAO for each entire artifact configured to be published
        whole_artifact_daos: dict[str, ArtifactDao] = {
            artifact_name: await dao_factory.get_dao(
                name=artifact_name,  # each artifact type gets its own collection and DAO
                dto_model=Artifact,
                id_field="study_accession",
            )
            for artifact_name in publishable_artifacts or []
        }

        return cls(
            artifact_resource_daos=artifact_resource_daos,
            whole_artifact_daos=whole_artifact_daos,
        )

    def __init__(
        self,
        artifact_resource_daos: dict[str, dict[str, ArtifactResourceDao]],
        whole_artifact_daos: dict[str, ArtifactDao] | None = None,
    ):
        """Initialize the collection of DAOs.

        Please note, don't use this constructor directly. Use the construct method
        instead.
        """
        self._artifact_resource_daos = artifact_resource_daos
        self._whole_artifact_daos = whole_artifact_daos or {}

    @staticmethod
    def _get_dao_name(*, artifact_name: str, class_name: str) -> str:
        """The dao name is a combination of the name of the artifact and the name of
        the class of the resource.
        """
        return f"art_{artifact_name}_class_{class_name}"

    async def get_all_whole_artifact_tags(self) -> set[tuple[str, str]]:
        """Retrieve all artifact tags currently present in the db.

        An artifact tag combines artifact name and submission ID into a tuple,
        i.e. (artifact name, submission_id)
        """
        all_artifact_tags: set[tuple[str, str]] = {
            (artifact_name, artifact.study_accession)
            for artifact_name, dao in self._whole_artifact_daos.items()
            async for artifact in dao.find_all(mapping={})
        }

        return all_artifact_tags

    async def get_all_resource_tags(self) -> set[tuple[str, str, str]]:
        """Retrieve resource tags for all artifacts currently present in the db.

        A resource tag combines artifact_name, class_name and resource ID (accession)
        into a tuple, i.e. it has the form '(artifact_name,class_name,resource_ID)'.
        This is done to flatten the nested artifact information to simplify keeping track
        of changes.
        """
        all_resource_tags: list[tuple[str, str, str]] = []
        for artifact_type, class_name_dao in self._artifact_resource_daos.items():
            for class_name, resource_dao in class_name_dao.items():
                # empty mapping should yield all resources
                resource_ids = [
                    resource.id_ async for resource in resource_dao.find_all(mapping={})
                ]
                all_resource_tags.extend(
                    (artifact_type, class_name, resource_id)
                    for resource_id in resource_ids
                )

        return set(all_resource_tags)

    async def get_dao(
        self, *, artifact_name: str, class_name: str
    ) -> ArtifactResourceDao:
        """Get the DAO for the given class in the given artifact.

        Raises:
            DaoNotFoundError: If the DAO could not be found.
        """
        try:
            return self._artifact_resource_daos[artifact_name][class_name]
        except KeyError as error:
            raise DaoNotFoundError(
                artifact_name=artifact_name, class_name=class_name
            ) from error

    async def get_whole_artifact_dao(self, *, artifact_name: str) -> ArtifactDao:
        """Get the DAO for the whole artifact."""
        try:
            return self._whole_artifact_daos[artifact_name]
        except KeyError as error:
            raise DaoNotFoundError(
                artifact_name=artifact_name, class_name=""
            ) from error
