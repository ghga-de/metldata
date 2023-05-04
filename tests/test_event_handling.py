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

import pytest

from tests.fixtures.event_handling import file_system_event_fixture  # noqa: F401
from tests.fixtures.event_handling import ConsumedEvent, Event, FileSystemEventFixture


@pytest.mark.asyncio
async def test_pub_sub_workflow(
    file_system_event_fixture: FileSystemEventFixture,  # noqa: F811
):
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

    await file_system_event_fixture.publish_events(events_to_publish)
    await file_system_event_fixture.expect_events(expected_events)
