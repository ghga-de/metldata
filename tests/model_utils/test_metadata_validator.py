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

"""Testing the metadata validator."""

from contextlib import nullcontext
from typing import Any

import pytest

from metldata.model_utils.metadata_validator import (
    MetadataValidator,
    MetadataValidatorConfig,
)
from tests.fixtures.metadata import INVALID_METADATA_EXAMPLES, VALID_METADATA_EXAMPLES
from tests.fixtures.metadata_models import VALID_METADATA_MODELS


@pytest.mark.parametrize(
    "metadata, is_valid",
    [(valid_metadata, True) for valid_metadata in VALID_METADATA_EXAMPLES]
    + [(invalid_metadata, False) for invalid_metadata in INVALID_METADATA_EXAMPLES],
)
def test_validate_against_model(metadata: dict[str, Any], is_valid: bool):
    """Test the validation of metadata against a model."""

    config = MetadataValidatorConfig(metadata_model=VALID_METADATA_MODELS[0])
    validator = MetadataValidator(config=config)

    with nullcontext() if is_valid else pytest.raises(  # type:ignore
        MetadataValidator.ValidationError
    ):
        validator.validate(metadata)
