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

"""Event publisher for population and deletion events to MASS, WPS and claims repository"""

import json
from abc import ABC, abstractmethod

from ghga_event_schemas.configs import DatasetEventsConfig, ResourceEventsConfig
from ghga_event_schemas.configs.stateful import ArtifactEventsConfig
from ghga_event_schemas.pydantic_ import (
    Artifact,
    ArtifactTag,
    MetadataDatasetID,
    MetadataDatasetOverview,
    SearchableResource,
    SearchableResourceInfo,
)
from hexkit.protocols.eventpub import EventPublisherProtocol
from pydantic import Field


class EventPubTranslatorConfig(
    DatasetEventsConfig, ResourceEventsConfig, ArtifactEventsConfig
):
    """Config for publishing population/deletion events to other services"""

    primary_artifact_name: str = Field(
        ...,
        description="Name of the artifact from which the information for outgoing"
        + " change events is derived.",
        examples=["embedded_public"],
    )
    primary_dataset_name: str = Field(
        ...,
        description="Name of the resource class corresponding to the embedded_dataset slot.",
        examples=["EmbeddedDataset"],
    )


class EventPublisherPort(ABC):
    """A port through which events are communicated with the outside."""

    @abstractmethod
    async def process_dataset_deletion(self, *, accession: str):
        """Communicate the deletion of an embedded dataset resource"""

    @abstractmethod
    async def process_resource_deletion(self, *, accession: str, class_name: str):
        """Communicate the deletion of an artifact resource"""

    @abstractmethod
    async def process_artifact_deletion(
        self,
        *,
        artifact_name: str,
        study_accession: str,
    ):
        """Communicate the deletion of an entire artifact"""

    @abstractmethod
    async def process_dataset_upsert(
        self, *, dataset_overview: MetadataDatasetOverview
    ):
        """Communicate the upsert of an embedded dataset resource"""

    @abstractmethod
    async def process_resource_upsert(self, *, resource: SearchableResource):
        """Communicate the upsert of an artifact resource"""

    @abstractmethod
    async def process_artifact_upsert(
        self,
        *,
        artifact: Artifact,
    ):
        """Communicate the upsert of an entire artifact"""

    @abstractmethod
    def is_primary_dataset_source(
        self, *, artifact_name: str, resource_class_name: str
    ) -> bool:
        """Checks if combination of artifact name and resource class name describe the
        configured source for outbound change events
        """


class EventPubTranslator(EventPublisherPort):
    """A translator according to  the triple hexagonal architecture implementing
    the EventPublisherPort.
    """

    def __init__(
        self, *, config: EventPubTranslatorConfig, provider: EventPublisherProtocol
    ):
        """Initialize with config and a provider of the EventPublisherProtocol."""
        self._config = config
        self._provider = provider

    async def process_dataset_deletion(self, *, accession: str):
        """Communicate the deletion of an embedded dataset resource

        Fires an event that should be processed by the claims repository
        """
        dataset_id = MetadataDatasetID(accession=accession)

        payload = json.loads(dataset_id.model_dump_json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.dataset_deletion_type,
            key=f"dataset_embedded_{dataset_id.accession}",
            topic=self._config.dataset_change_topic,
        )

    async def process_resource_deletion(self, *, accession: str, class_name: str):
        """Communicate the deletion an artifact resource

        Fires an event that should be processed by MASS
        """
        resource_info = SearchableResourceInfo(
            accession=accession, class_name=class_name
        )

        payload = json.loads(resource_info.model_dump_json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.resource_deletion_type,
            key=f"dataset_embedded_{resource_info.accession}",
            topic=self._config.resource_change_topic,
        )

    async def process_artifact_deletion(
        self,
        *,
        artifact_name: str,
        study_accession: str,
    ):
        """Communicate the deletion of an entire artifact"""
        artifact_tag = ArtifactTag(
            artifact_name=artifact_name, study_accession=study_accession
        )
        await self._provider.publish(
            payload=artifact_tag.model_dump(),
            type_="deleted",
            key=f"{artifact_name}:{study_accession}",
            topic=self._config.artifact_topic,
        )

    async def process_dataset_upsert(
        self, *, dataset_overview: MetadataDatasetOverview
    ):
        """Communicate the upsert of an embedded dataset resource

        Fires an event that should be processed by the WPS
        """
        payload = json.loads(dataset_overview.model_dump_json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.dataset_upsertion_type,
            key=f"dataset_embedded_{dataset_overview.accession}",
            topic=self._config.dataset_change_topic,
        )

    async def process_resource_upsert(self, *, resource: SearchableResource):
        """Communicate the upsert of an artifact resource

        Fires an event that should be processed by MASS
        """
        payload = json.loads(resource.model_dump_json())
        await self._provider.publish(
            payload=payload,
            type_=self._config.resource_upsertion_type,
            key=f"dataset_embedded_{resource.accession}",
            topic=self._config.resource_change_topic,
        )

    async def process_artifact_upsert(
        self,
        *,
        artifact: Artifact,
    ):
        """Communicate the upsert of an entire artifact"""
        payload = json.loads(artifact.model_dump_json())
        await self._provider.publish(
            payload=payload,
            type_="upserted",
            key=f"{artifact.artifact_name}:{artifact.study_accession}",
            topic=self._config.artifact_topic,
        )

    def is_primary_dataset_source(
        self, *, artifact_name: str, resource_class_name: str
    ) -> bool:
        """Checks if combination of artifact name and resource class name describe the
        configured source for outbound dataset change events
        """
        return (
            self._config.primary_artifact_name == artifact_name
            and self._config.primary_dataset_name == resource_class_name
        )
