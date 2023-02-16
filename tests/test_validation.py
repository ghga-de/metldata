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

"""Testing the accession handler."""

from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pytest

from metldata.submission_registry.validation import (
    MetadataModelAssumptionError,
    MetadataValidator,
    check_metadata_model_assumption,
)

from .fixtures.metadata_models import INVALID_METADATA_MODELS, VALID_METADATA_MODELS


@pytest.mark.parametrize(
    "model_path, is_valid",
    [(valid_model, True) for valid_model in VALID_METADATA_MODELS]
    + [(invalid_model, False) for invalid_model in INVALID_METADATA_MODELS],
)
def test_metadata_model_assumption_checking(model_path: Path, is_valid: bool):
    """Test the assumptions regarding the metadata model are correctly checked."""

    with nullcontext() if is_valid else pytest.raises(MetadataModelAssumptionError):
        check_metadata_model_assumption(model_path=model_path)


VALID_FILE_EXAMPLES = [
    {
        "alias": "file001",
        "filename": "file001.txt",
        "format": "txt",
        "checksum": "40b971c2b26ffb22db3558d1c27e20f7",
        "size": 15347,
    },
    {
        "alias": "file002",
        "filename": "file002.txt",
        "format": "txt",
        "checksum": "f051753bbb3869485b66b45139fac10b",
        "size": 27653,
    },
]
INVALID_FILE_EXAMPLES = [
    {
        "alias": "file001",
        "filename": "file001.txt",
        "format": "invalid",  # invalid
        "checksum": "40b971c2b26ffb22db3558d1c27e20f7",
        "size": 15347,
    },
    {
        "alias": "file002",
        "filename": "file002.txt",
        "format": "txt",
        "checksum": "f051753bbb3869485b66b45139fac10b",
        "size": 3234.23424,  # invalid
    },
    {
        "alias": "file003",
        # filename missing
        "format": "txt",
        "checksum": "f051753bbb3869485b66b45139fac10b",
        "size": 1123,
    },
    {
        "alias": "file002",
        "filename": "file002.txt",
        "format": "txt",
        "checksum": "f051753bbb3869485b66b45139fac10b",
        "size": 1123,
        "creation_date": "Thu Feb 16 13:15:50 UTC 2023",  # additional field
    },
]

VALID_METADATA_EXAMPLES = [
    {"has_file": [VALID_FILE_EXAMPLES[0]]},
    {"has_file": VALID_FILE_EXAMPLES},
]

INVALID_METADATA_EXAMPLES = [
    {},  # missing field
    {"has_file": VALID_FILE_EXAMPLES[0]},  # single file where list expected
] + [
    {"has_file": [VALID_FILE_EXAMPLES[0], invalid_file]}
    for invalid_file in INVALID_FILE_EXAMPLES
]


@pytest.mark.parametrize(
    "metadata, is_valid",
    [(valid_metadata, True) for valid_metadata in VALID_METADATA_EXAMPLES]
    + [(invalid_metadata, False) for invalid_metadata in INVALID_METADATA_EXAMPLES],
)
def test_validate_against_model(metadata: dict[str, Any], is_valid: bool):
    """Test the validation of metadata against a model."""

    validator = MetadataValidator(model_path=VALID_METADATA_MODELS[0])

    with nullcontext() if is_valid else pytest.raises(
        MetadataValidator.ValidationError
    ):
        validator.validate(metadata)
