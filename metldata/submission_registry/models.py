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

"""Data models"""

from enum import Enum
from typing import Any, Optional

from ghga_service_chassis_lib.utils import DateTimeUTC, now_as_utc
from pydantic import BaseModel, Field


class SubmissionStatus(Enum):
    """Statuses a submission may have."""

    PENDING = "pending"
    IN_REVIEW = "in-review"
    CANCELED = "canceled"
    COMPLETED = "completed"
    DEPRECATED_PREPUBLICATION = "deprecated-prepublication"
    EMPTIED_PREPUBLICATION = "emptyied-prepublication"
    PUBLISHED = "published"
    DEPRECATED_POSTPUBLICATION = "deprecated-postpublication"
    HIDDEN_POSTPUBLICATION = "hidden-postpublication"
    EMPTIED_POSTPUBLICATION = "emptied-postpublication"


class StatusChange(BaseModel):
    """A model for describing status changes of submissions."""

    timestamp: DateTimeUTC
    new_status: SubmissionStatus


class SubmissionCreation(BaseModel):
    """Essential data for creating a submission."""

    title: str = Field(..., description="A descriptive title for this submission.")
    description: Optional[str] = Field(None, description="An optional description.")

    content: dict[str, Any] = Field(
        ..., description="The metadata content of the submission."
    )


class Submission(SubmissionCreation):
    """A model for describing a submission."""

    id: str

    status_history: list[StatusChange] = Field(
        default_factory=lambda: [
            StatusChange(timestamp=now_as_utc(), new_status=SubmissionStatus.PENDING)
        ],
        description="A history of status changes.",
    )