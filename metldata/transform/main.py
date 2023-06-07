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

"""Main logic for running a transformation workflow on submissions."""


import json
from typing import Callable
from build.lib.metldata.submission_registry.event_publisher import EventPublisher
from metldata.custom_types import Json
from metldata.event_handling.models import SubmissionEventPayload
from metldata.transform.handling import WorkflowHandler


def run_workflow_on_submission(
    source_event: SubmissionEventPayload,
    workflow_handler: WorkflowHandler,
    artifact_publisher: Callable[[Json], None],
) -> None:
    """Run a transformation workflow on a source event and publish the artifact using
    the provided artifact publisher.

    Args:
        source_event:
            The source event corresponding to one submission and its cotent.
        workflow_handler:
            The workflow handler preconfigured with a workflow definition, a workflow
            config, and the original model of the source events.
        artifact_publisher: The artifact publisher to use for publishing the artifacts.
    """

    artifacts = workflow_handler.run(
        metadata=source_event.content, annotation=source_event.annotation
    )

    for artifact in artifacts:
        artifact_event = source_event.copy(content=artifact)
        artifact_event_payload = json.loads(artifact_event.json())
        artifact_publisher(artifact_event_payload)


def main():
    """Run a subscriber to hand source events to a transformation workflow and
    run a publisher for publishing artifacts."""

    event_publisher = EventPublisher()
