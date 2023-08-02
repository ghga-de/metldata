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

import json
from abc import ABC, abstractmethod

from ghga_event_schemas.pydantic_ import (MetadataDatasetID,
                                          MetadataDatasetOverview,
                                          SearchableResource,
                                          SearchableResourceInfo)
from hexkit.protocols.eventpub import EventPublisherProtocol
from pydantic import BaseSettings, Field


class EventPubTranslatorConfig(BaseSettings):
    """Config for publishing population/deletion events to other services

    dataset_overview events should
    """

    resource_change_event_topic: str = Field(
        ...,
        description="Name of the topic used for events informing other services about"
        + " resource changes, i.e. deletion or insertion.",
        example="searchable_resources",
    )
    resource_deletion_event_type: str = Field(
        ...,
        description="Type used for events indicating the deletion of a previously"
        + " existing resource.",
        example="searchable_resource_deleted",
    )
    resource_upsertion_type: str = Field(
        ...,
        description="Type used for events indicating the upsert of a resource.",
        example="searchable_resource_upserted",
    )

    dataset_change_event_topic: str = Field(
        ...,
        description="Name of the topic announcing, among other things, the list of"
        + " files included in a new dataset.",
        example="metadata_datasets",
    )
    dataset_deletion_type: str = Field(
        ...,
        description="Type used for events announcing a new dataset overview.",
        example="dataset_overview_deleted",
    )
    dataset_upsertion_type: str = Field(
        ...,
        description="Type used for events announcing a new dataset overview.",
        example="dataset_overview_created",
    )


class EventPublisherPort(ABC):
    """ """

    @abstractmethod
    async def process_dataset_deletion(self, *, accession: str):
        """ """

    @abstractmethod
    async def process_resource_deletion(self, *, accession: str, class_name: str):
        """ """

    @abstractmethod
    async def process_dataset_upsert(
        self, *, dataset_overview: MetadataDatasetOverview
    ):
        """ """

    @abstractmethod
    async def process_resource_upsert(self, *, resource: SearchableResource):
        """ """


class EventPubTranslator(EventPublisherPort):
    """ """

    def __init__(
        self, *, config: EventPubTranslatorConfig, provider: EventPublisherProtocol
    ):
        """Initialize with config and a provider of the EventPublisherProtocol."""

        self._config = config
        self._provider = provider

    async def process_dataset_deletion(self, *, accession: str):
        """ """

        dataset_id = MetadataDatasetID(accession=accession)

        payload = json.loads(dataset_id.json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.dataset_deletion_type,
            key=f"dataset_embedded_{dataset_id.accession}",
            topic=self._config.dataset_change_event_topic,
        )

    async def process_resource_deletion(self, *, accession: str, class_name: str):
        """ """

        resource_info = SearchableResourceInfo(
            accession=accession, class_name=class_name
        )

        payload = json.loads(resource_info.json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.resource_deletion_event_type,
            key=f"dataset_embedded_{resource_info.accession}",
            topic=self._config.resource_change_event_topic,
        )

    async def process_dataset_upsert(
        self, *, dataset_overview: MetadataDatasetOverview
    ):
        """ """

        payload = json.loads(dataset_overview.json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.dataset_upsertion_type,
            key=f"dataset_embedded_{dataset_overview.accession}",
            topic=self._config.dataset_change_event_topic,
        )

    async def process_resource_upsert(self, *, resource: SearchableResource):
        """ """

        payload = json.loads(resource.json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.resource_upsertion_type,
            key=f"dataset_embedded_{resource.accession}",
            topic=self._config.resource_change_event_topic,
        )
