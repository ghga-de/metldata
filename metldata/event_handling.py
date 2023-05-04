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

import json
from pathlib import Path
from typing import Iterator
from hexkit.custom_types import JsonObject, Ascii
from hexkit.protocols.eventpub import EventPublisherProtocol
from hexkit.protocols.eventsub import EventSubscriberProtocol
from hexkit.base import InboundProviderBase
from pydantic import BaseModel, BaseSettings, Field


class FileSystemEventConfig(BaseSettings):
    """Config paramters and their defaults."""

    event_store_path: Path = Field(
        ...,
        description=(
            "Path of the directory on the file system where all events are stored."
            + " Each topic is a sub-directory. Each event is stored as a"
            + " JSON file within the event key directory. The file name corresponds to"
            + " the event keys. Event types are stored to gether with the payload in"
            + " the event file."
        ),
    )


class Event(BaseModel):
    """An event."""

    topic: str
    type_: str
    key: str
    payload: JsonObject


def get_topic_path(*, topic: str, event_store_path: Path) -> Path:
    """Get the path of an event topic."""

    return event_store_path / topic


def get_event_path(*, topic: str, key: str, event_store_path: Path) -> Path:
    """Get the path of an event file."""

    return (
        get_topic_path(topic=topic, event_store_path=event_store_path) / f"{key}.json"
    )


def write_event(*, event: Event, event_store_path: Path) -> None:
    """Write an event to the file system."""

    event_path = get_event_path(
        topic=event.topic, key=event.key, event_store_path=event_store_path
    )
    event_content = {"type": event.type_, "payload": event.payload}

    event_path.parent.mkdir(parents=True, exist_ok=True)
    with open(event_path, "w", encoding="utf-8") as event_file:
        json.dump(event_content, event_file)


def read_event_file(event_path: Path) -> Event:
    """Read an event from a file."""

    with open(event_path, "r", encoding="utf-8") as event_file:
        event_content = json.load(event_file)

    return Event(
        topic=event_path.parent.name,
        key=event_path.stem,
        **event_content,
    )


def read_events_from_topic(*, topic: str, event_store_path: Path) -> Iterator[Event]:
    """Read all events for the given topic from the file system."""

    topic_path = get_topic_path(topic=topic, event_store_path=event_store_path)

    topic_path.mkdir(parents=True, exist_ok=True)

    for event_path in topic_path.iterdir():
        yield read_event_file(event_path)


class FileSystemEventPublisher(EventPublisherProtocol):
    """An EventPublisher that stores events on the file system.

    Please note that this the file system based event store mimics the behaviour of a
    compacted topics. Only the last event with a given key are stored."""

    def __init__(self, config: FileSystemEventConfig):
        """Initialize with config."""

        self._config = config

    async def _publish_validated(
        self, *, payload: JsonObject, type_: Ascii, key: Ascii, topic: Ascii
    ) -> None:
        """Publish an event with already validated topic and type.

        Args:
            payload: The payload to ship with the event.
            type_: The event type. ASCII characters only.
            key: The event type. ASCII characters only.
            topic: The event type. ASCII characters only.
        """

        event = Event(
            topic=topic,
            type_=type_,
            key=key,
            payload=payload,
        )
        write_event(
            event=event,
            event_store_path=self._config.event_store_path,
        )


class FileSystemEventSubscriber(InboundProviderBase):
    """An EventSubscriber that reads events on the file system."""

    def __init__(
        self, *, config: FileSystemEventConfig, translator: EventSubscriberProtocol
    ):
        """Initialize with config."""

        self._config = config
        self._translator = translator

        if len(self._translator.topics_of_interest) != 1:
            raise ValueError(
                "FileSystemEventSubscriber only supports a single topic of interest."
            )

    async def run(self, forever: bool = True) -> None:
        """
        Runs the inbound provider.

        Please note, unlike other inbound providers, it exits when no further events
        are available.
        """

        for event in read_events_from_topic(
            topic=self._translator.topics_of_interest[0],
            event_store_path=self._config.event_store_path,
        ):
            await self._translator.consume(
                payload=event.payload, type_=event.type_, topic=event.topic
            )
