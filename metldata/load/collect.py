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

"""Functionality for collect available artifacts."""

from collections import defaultdict
from typing import Callable

from hexkit.custom_types import Ascii, JsonObject
from hexkit.protocols.eventsub import EventSubscriberProtocol
from pydantic import BaseModel, Field

from metldata.custom_types import Json
from metldata.load.models import ArtifactResourceDict


class ArtifactConsumerConfig(BaseModel):
    """Config parameters and their defaults."""

    artifact_topic_prefix: str = Field(
        ...,
        description=(
            "The prefix used for topics containing artifacts. The topic name is"
            + " expected to be '{prefix}.{artifact_type}'."
        ),
    )
    artifact_types: list[str] = Field(
        ...,
        description=(
            "The artifacts types of interest. Together with the topic prefix, they"
            + " determine the topics to subscribe to."
        ),
    )


def get_artifact_topic(*, artifact_topic_prefix: str, artifact_type: str) -> str:
    """Get the topic name for the given artifact type."""

    return f"{artifact_topic_prefix}.{artifact_type}"


class ArtifactConsumer(EventSubscriberProtocol):
    """Consumes artifact events."""

    def __init__(
        self,
        consume_artifact_func: Callable[[str, Json], None],
        config: ArtifactConsumerConfig,
    ) -> None:
        """Initialize with config.

        Args:
            consume_artifact_func:
                A function that consumes an artifact of one submission. The first
                argument is the artifact type, the second is the artifact content.
            config:
                Config parameters.
        """

        artifact_topics = [
            get_artifact_topic(
                artifact_topic_prefix=config.artifact_topic_prefix,
                artifact_type=artifact_type,
            )
            for artifact_type in config.artifact_types
        ]

        self.topics_of_interest = artifact_topics
        self.types_of_interest = config.artifact_types
        self._consume_artifact_func = consume_artifact_func

    async def _consume_validated(
        self, *, payload: JsonObject, type_: Ascii, topic: Ascii
    ) -> None:
        """Receive and process an event with already validated topic and type.

        Args:
            payload: The data/payload to send with the event.
            type_: The type of the event.
            topic: Name of the topic the event was published to.
        """

        self._consume_artifact_func(type_, payload)


def collect_artifacts_from_fs(
    *, config: ArtifactConsumerConfig
) -> ArtifactResourceDict:
    """Collect artifacts from the file system."""

    artifact_resource_dict: ArtifactResourceDict = defaultdict(list)

    def consume_artifact(artifact_type: str, artifact_content: Json) -> None:
        """Helper function to collect artifacts from the consumer."""

        artifact_resource_dict[artifact_type].append(artifact_content)

    artifact_consumer = ArtifactConsumer(
        consume_artifact_func=consume_artifact, config=config
    )
    event_sub_
