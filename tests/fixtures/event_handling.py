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

"""Fixtures for handling events."""

import json
from collections import defaultdict
from pathlib import Path

import pytest
from hexkit.custom_types import Ascii, JsonObject
from hexkit.protocols.eventsub import EventSubscriberProtocol
from pydantic import BaseModel, Field

from metldata.event_handling import (
    Event,
    FileSystemEventConfig,
    FileSystemEventPublisher,
    FileSystemEventSubscriber,
)


class ConsumedEvent(BaseModel):
    """Consumed event without the key."""

    topic: str
    type_: str
    payload: str = Field(..., description="JSON string of the event payload.")

    class Config:
        """Pydantic model configuration."""

        frozen = True


class MockSubscriberTranslator(EventSubscriberProtocol):
    """A mock implementation of the EventSubscriberProtocol to track consumed
    events. Only consumes from topic1.

    Consumed events are captured in the consumed_events attribute.
    """

    def __init__(self, topics_of_interest: set[str], types_of_interest: set[str]):
        self.consumed_events: set[ConsumedEvent] = set()
        self.topics_of_interest = topics_of_interest
        self.types_of_interest = types_of_interest

    async def _consume_validated(
        self, *, payload: JsonObject, type_: Ascii, topic: Ascii
    ) -> None:
        self.consumed_events.add(
            ConsumedEvent(topic=topic, type_=type_, payload=json.dumps(payload))
        )


class EventExpectationMissmatch(RuntimeError):
    """Raised when expected events where not found."""

    def __init__(
        self, expected_events: set[ConsumedEvent], consumed_events: set[ConsumedEvent]
    ):
        message = f"Expected events {expected_events} but got {consumed_events}"
        super().__init__(message)


class FileSystemEventFixture:
    """Returned by file_system_event_fixture."""

    def __init__(self, *, config: FileSystemEventConfig):
        """Initialize with config."""

        self.config = config

    async def expect_events(self, expected_events: set[ConsumedEvent]) -> None:
        """Check if the events expected to be published can be consumed.

        Raises:
            EventExpectationMissmatch: If the expected events are not consumed.
        """

        events_by_topic: dict[str, set[ConsumedEvent]] = defaultdict(set)
        for event in list(expected_events):
            events_by_topic[event.topic].add(event)

        for topic, events in events_by_topic.items():
            types_of_interest = {event.type_ for event in events}
            translator = MockSubscriberTranslator(
                topics_of_interest={topic}, types_of_interest=types_of_interest
            )
            subscriber = FileSystemEventSubscriber(
                config=self.config, translator=translator
            )
            await subscriber.run()

            if translator.consumed_events != events:
                raise EventExpectationMissmatch(
                    expected_events=events, consumed_events=translator.consumed_events
                )

    async def publish_events(self, events: list[Event]) -> None:
        """Publish a list of events."""

        publisher = FileSystemEventPublisher(config=self.config)
        for event in events:
            await publisher.publish(
                topic=event.topic,
                type_=event.type_,
                key=event.key,
                payload=event.payload,
            )


@pytest.fixture
def file_system_event_fixture(tmp_path: Path) -> FileSystemEventFixture:
    """A fixture for handling events on the file system."""

    config = FileSystemEventConfig(
        event_store_path=tmp_path,
    )
    return FileSystemEventFixture(config=config)
