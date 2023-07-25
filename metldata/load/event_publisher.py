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

"""Event publisher for population and deletion events to MASS, WPS and claims repository"""

from abc import ABC, abstractmethod

from ghga_event_schemas.pydantic_ import (
    MetadataDataset,
    MetadataDatasetFile,
    MetadataDatasetID,
    MetadataDatasetOverview,
    MetadataDatasetStage,
)
from hexkit.protocols.eventpub import EventPublisherProtocol
from pydantic import BaseSettings, Field

from metldata.artifacts_rest.models import ArtifactResource


class EventPubTranslatorConfig(BaseSettings):
    """Config for publishing population/deletion events to other services

    dataset_overview events should
    """

    dataset_change_topic: str = Field(
        ...,
        description="Name of the topic used for events informing other services about"
        + " dataset changes, i.e. deletion or insertion.",
        example="metadata_dataset_change",
    )
    dataset_deletion_type: str = Field(
        ...,
        description="Type used for events indicating the deletion of a previously"
        + " existing dataset.",
        example="deletion",
    )
    dataset_insertion_type: str = Field(
        ...,
        description="Type used for events indicating the insertion of a new dataset.",
        example="insertion",
    )

    dataset_overview_topic: str = Field(
        ...,
        description="Name of the topic announcing, among other things, the list of"
        + " files included in a new dataset.",
        example="metadata_dataset_overview",
    )
    dataset_overview_type: str = Field(
        ...,
        description="Type used for events announcing a new dataset overview.",
        example="overview_creation",
    )


class EventPubTranslatorPort(ABC):
    """ """

    @abstractmethod
    async def datasets_created(
        self, *, artifact_name: str, resources: list[ArtifactResource]
    ):
        """ """

    @abstractmethod
    async def datasets_deleted(self, *, datasets: list[str]):
        """ """


class EventPubTranslator(EventPubTranslatorPort):
    """ """

    def __init__(
        self, *, config: EventPubTranslatorConfig, provider: EventPublisherProtocol
    ):
        """Initialize with config and a provider of the EventPublisherProtocol."""

        self._config = config
        self._provider = provider

    async def datasets_created(self, *, resources: list[ArtifactResource]):
        """ """

        for resource in resources:
            # population event for MASS
            payload = MetadataDataset(
                accession=resource.id_,
                class_name=resource.class_name,
                content=resource.content,
            ).dict()

            await self._provider.publish(
                payload=payload,
                type_=self._config.dataset_insertion_type,
                key=f"dataset_embedded_{resource.id_}",
                topic=self._config.dataset_change_topic,
            )

            files = []
            resource.content["embedded_dataset"]
            MetadataDatasetFile(accession="", description="", file_extension="")

            payload = MetadataDatasetOverview(
                accession=resource.id_,
                description="",
                files="",
                stage=MetadataDatasetStage.DOWNLOAD,
                title="",
            )

    async def datasets_deleted(self, *, resource_ids: list[str]):
        """ """
        for resource_id in resource_ids:
            payload = MetadataDatasetID(accession=resource_id).dict()

            await self._provider.publish(
                payload=payload,
                type_=self._config.dataset_deletion_type,
                key=f"dataset_embedded_{resource_id}",
                topic=self._config.dataset_change_topic,
            )
