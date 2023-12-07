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

from collections.abc import Generator
from tempfile import NamedTemporaryFile

import pytest

from metldata.accession_registry.config import Config as AccessionRegistryConfig
from tests.fixtures.metadata_models import VALID_MINIMAL_MODEL_EXAMPLE_PATH

PREFIX_MAPPING = {
    "File": "GHGAF",
    "Experiment": "GHGAE",
    "Sample": "GHGAS",
    "Dataset": "GHGAD",
}


@pytest.fixture
def config_accession_store() -> Generator[AccessionRegistryConfig, None, None]:
    """Generate a test config."""

    with NamedTemporaryFile() as accession_store_path:
        yield AccessionRegistryConfig(
            accession_store_path=accession_store_path.name,
            prefix_mapping=PREFIX_MAPPING,
        )
