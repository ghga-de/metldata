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
from metldata.artifacts_rest.load_resources import extract_all_resources_from_artifact
from metldata.artifacts_rest.models import ArtifactInfo, ArtifactResource
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


async def load_artifacts_using_dao(
    artifact_resources: ArtifactResourceDict,
    artifact_info_dict: dict[str, ArtifactInfo],
    dao_collection: ArtifactDaoCollection,
) -> None:
    """Load artifact resources from multiple submissions using the given dao collection."""

    (
        removed_resource_tags,
        new_resources,
        changed_resources,
    ) = await _get_changed_resources(
        artifact_resources=artifact_resources,
        artifact_info_dict=artifact_info_dict,
        dao_collection=dao_collection,
    )

    await _process_removed_resources(
        resource_tags=removed_resource_tags, dao_collection=dao_collection
    )

    await _process_new_resources(
        new_resources=new_resources, dao_collection=dao_collection
    )

    await _process_changed_resources(
        changed_resources=changed_resources, dao_collection=dao_collection
    )


async def _get_changed_resources(  # pylint: disable=too-many-locals
    artifact_resources: ArtifactResourceDict,
    artifact_info_dict: dict[str, ArtifactInfo],
    dao_collection: ArtifactDaoCollection,
) -> tuple[set[str], dict[str, ArtifactResource], dict[str, ArtifactResource]]:
    """Extract changed resources using DAOs and currently submitted artifacts

    Returns the following collections in order:
     - A set of resource tags for artifact resources that have been removed
     - A dict of new artifact resources indexed by the corresponding resource_tag
     - A dict of changed artifact resources indexed by the corresponding resource_tag
    """

    # only need to collect resource tag to check if something needs to be deleted
    seen_resource_tags = []

    # collect new/changed resources indexed by their resource_tag for insert/upsert
    new_resources = {}
    changed_resources = {}

    existing_resource_tags = await dao_collection.get_all_resource_tags()

    for artifact_name, artifact_contents in artifact_resources.items():
        for artifact_content in artifact_contents:
            resources = extract_all_resources_from_artifact(
                artifact_content=artifact_content,
                artifact_info=artifact_info_dict[artifact_name],
            )

            # check for each resource if it does already exist and is changed
            for resource in resources:
                resource_tag = f"{artifact_name}#{resource.class_name}#{resource.id_}"
                seen_resource_tags.append(resource_tag)

                if resource_tag not in existing_resource_tags:
                    new_resources[resource_tag] = resource
                else:
                    dao = await dao_collection.get_dao(
                        artifact_name=artifact_name, class_name=resource.class_name
                    )
                    old_resource = await dao.get_by_id(resource.id_)
                    if old_resource != resource:
                        changed_resources[resource_tag] = resource

    removed_resource_tags = existing_resource_tags - set(seen_resource_tags)

    return removed_resource_tags, new_resources, changed_resources


async def _process_removed_resources(
    resource_tags: set[str], dao_collection: ArtifactDaoCollection
):
    """Delete no longer needed artifact resources from DB and send corresponding events"""

    for resource_tag in resource_tags:
        artifact_name, class_name, resource_id = resource_tag.split("#")
        dao = await dao_collection.get_dao(
            artifact_name=artifact_name, class_name=class_name
        )
        # resource tag was obtained from querying the db, so resource with given ID
        # should be present
        await dao.delete(id_=resource_id)

    # needs event publisher and corresponding outgoing models here


async def _process_new_resources(
    new_resources: dict[str, ArtifactResource], dao_collection: ArtifactDaoCollection
):
    """Insert newly received artifact resources into DB and send corresponding events"""

    for resource_tag, resource in new_resources.items():
        artifact_name, class_name, _ = resource_tag.split("#")
        dao = await dao_collection.get_dao(
            artifact_name=artifact_name, class_name=class_name
        )
        # no resource tag was obtained from querying the db, so the resource with the
        # given ID should not be present
        await dao.insert(resource)

    # needs event publisher and corresponding outgoing models here


async def _process_changed_resources(
    changed_resources: dict[str, ArtifactResource],
    dao_collection: ArtifactDaoCollection,
):
    """Upsert changed artifact resources into DB and send corresponding events"""

    for resource_tag, resource in changed_resources.items():
        artifact_name, class_name, _ = resource_tag.split("#")
        dao = await dao_collection.get_dao(
            artifact_name=artifact_name, class_name=class_name
        )
        # resource tag was obtained from querying the db, so resource with given ID
        # should be present
        await dao.upsert(resource)

    # needs event publisher and corresponding outgoing models here
