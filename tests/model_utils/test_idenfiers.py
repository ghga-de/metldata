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

"""Test the idenifiers module."""

from metldata.model_utils.identifieres import get_class_identifiers
from tests.fixtures.metadata_models import MINIMAL_VALID_METADATA_MODEL


def test_get_class_identifiers_happy():
    """Test the happy path of using the get_class_identifiers function."""

    expected_identifiers = {"File": "alias", "Dataset": "alias"}

    observed_identifiers = get_class_identifiers(model=MINIMAL_VALID_METADATA_MODEL)

    assert observed_identifiers == expected_identifiers
