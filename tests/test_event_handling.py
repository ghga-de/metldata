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

"""Test the event_handling module."""

import json
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


@pytest.mark.asyncio
async def test_pub_sub_workflow(tmp_path: Path):
    """Test a publish subscribe workflow using the FileSystemEventPublisher and
    FileSystemEventSubscriber."""

    # events to publish:
    events_to_publish = [
        Event(topic="topic1", type_="type1", key="key1", payload={"test1": "value1"}),
        # overwrites above event since same key:
        Event(topic="topic1", type_="type2", key="key1", payload={"test2": "value2"}),
        # other key thus will be present:
        Event(topic="topic1", type_="type1", key="key2", payload={"test3": "value3"}),
        # publish to other topic:
        Event(topic="topic2", type_="type1", key="key1", payload={"test4": "value4"}),
    ]

    # expected events to consume in topic1:
    expected_events = {
        ConsumedEvent(
            topic="topic1", type_="type2", payload=json.dumps({"test2": "value2"})
        ),
        ConsumedEvent(
            topic="topic1", type_="type1", payload=json.dumps({"test3": "value3"})
        ),
    }

    class MockSubscriberTranslator(EventSubscriberProtocol):
        """A mock implementation of the EventSubscriberProtocol to track consumed
        events. Only consumes from topic1.

        Consumed events are captured in the consumed_events attribute.
        """

        def __init__(self):
            self.consumed_events: set[ConsumedEvent] = set()
            self.topics_of_interest = {"topic1"}
            self.types_of_interest = {"type1", "type2"}

        async def _consume_validated(
            self, *, payload: JsonObject, type_: Ascii, topic: Ascii
        ) -> None:
            self.consumed_events.add(
                ConsumedEvent(topic=topic, type_=type_, payload=json.dumps(payload))
            )

    # Create a publisher and a subscriber.
    config = FileSystemEventConfig(event_store_path=tmp_path)
    translator = MockSubscriberTranslator()
    publisher = FileSystemEventPublisher(config=config)
    subscriber = FileSystemEventSubscriber(config=config, translator=translator)

    # Publish a set of event:
    for event in events_to_publish:
        await publisher.publish(
            topic=event.topic, type_=event.type_, key=event.key, payload=event.payload
        )

    # consume events from topic1:
    await subscriber.run()

    # check consumed events:
    assert translator.consumed_events == expected_events
