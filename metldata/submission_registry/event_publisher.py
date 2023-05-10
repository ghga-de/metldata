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

"""Logic for the publication of source events."""

import asyncio
import json

from hexkit.protocols.eventpub import EventPublisherProtocol
from pydantic import BaseSettings, Field

from metldata.submission_registry import models


class SourceEventPublisherConfig(BaseSettings):
    """Config parameters and their defaults."""

    source_event_topic: str = Field(
        "source_events",
        description="Name of the topic to which source events are published.",
    )
    source_event_type: str = Field(
        "source_event", description="Name of the event type for source events."
    )


class SourceEventPublisher:
    """Handles publication of source events."""

    def __init__(
        self, *, config: SourceEventPublisherConfig, provider: EventPublisherProtocol
    ):
        """Initialize with config parameters."""

        self._config = config
        self._provider = provider

    def publish_submission(self, submission: models.Submission):
        """Publish the current submission as source event"""

        if submission.content is None:
            raise ValueError("Submission content must be defined.")

        payload = json.loads(submission.json())
        asyncio.run(
            self._provider.publish(
                topic=self._config.source_event_topic,
                type_=self._config.source_event_type,
                key=submission.id,
                payload=payload,
            )
        )
