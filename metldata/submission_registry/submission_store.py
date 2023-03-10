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

"""Logic for storing submission metadata."""

import json
from pathlib import Path
from uuid import uuid4

from pydantic import BaseSettings, Field

from metldata.submission_registry import models
from metldata.submission_registry.utils import save_submission_as_json


class SubmissionStoreConfig(BaseSettings):
    """Config parameters and their defaults."""

    submission_store_dir: Path = Field(
        ..., description="The directory where the submission JSONs will be stored."
    )


class SubmissionStore:
    """A class for storing and retrieving submissions."""

    class SubmissionDoesNotExistError(RuntimeError):
        """Raised when an Submission does not exists."""

        def __init__(self, *, submission_id: str):
            message = (
                "The submission with the following ID does not exist: " + submission_id
            )
            super().__init__(message)

    def __init__(self, *, config: SubmissionStoreConfig):
        """Initialize with config parameters."""

        self._config = config

    def _get_submission_json_path(self, *, submission_id: str) -> Path:
        """Get the path to the JSON file containing the submission with the specified
        ID."""

        return self._config.submission_store_dir / f"{submission_id}.json"

    @staticmethod
    def _generate_new_submission_id():
        """Generate a new submission ID."""

        return str(uuid4())

    def _save(self, *, submission: models.Submission) -> None:
        """Save a submission to a JSON file."""

        json_path = self._get_submission_json_path(submission_id=submission.id)
        save_submission_as_json(submission=submission, json_path=json_path)

    def exists(self, *, submission_id: str) -> bool:
        """Check whether a submission with the specified ID exists."""

        json_path = self._get_submission_json_path(submission_id=submission_id)
        return json_path.exists()

    def _assert_exists(self, *, submission_id: str):
        """Assert that a submission with the specified ID exists.

        Raises:
            SubmissionDoesNotExistError: Raised when the submission does not exist.
        """

        if not self.exists(submission_id=submission_id):
            raise self.SubmissionDoesNotExistError(submission_id=submission_id)

    def get_by_id(self, submission_id: str) -> models.Submission:
        """Get an existing submission by its ID.
        Raises:
            SubmissionDoesNotExistError: Raised when the submission does not exist.
        """

        json_path = self._get_submission_json_path(submission_id=submission_id)

        if not json_path.exists():
            raise self.SubmissionDoesNotExistError(submission_id=submission_id)

        with open(json_path, "r", encoding="utf-8") as file:
            submission_dict = json.load(file)

        return models.Submission(**submission_dict)

    def insert_new(self, *, submission: models.SubmissionCreation) -> models.Submission:
        """Save a new submission. Return submission including its assigned ID."""

        submission_id = self._generate_new_submission_id()
        submission_with_id = models.Submission(id=submission_id, **submission.dict())

        self._save(submission=submission_with_id)

        return submission_with_id

    def update_existing(self, *, submission: models.Submission) -> None:
        """Update an existing submission.

        Raises:
            SubmissionDoesNotExistError: when the submission does not exist.
        """

        self._assert_exists(submission_id=submission.id)
        self._save(submission=submission)
