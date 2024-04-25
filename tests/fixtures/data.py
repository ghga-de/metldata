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

"""Valid and invalid metadata examples using the minimal model."""

from schemapack.load import load_datapack
from schemapack.spec.datapack import DataPack

from tests.fixtures.utils import BASE_DIR

EXAMPLE_DATA_DIR = BASE_DIR / "example_data"


def _get_example_data(name: str) -> DataPack:
    """Get example metadata."""

    return load_datapack(EXAMPLE_DATA_DIR / f"{name}.datapack.yaml")


MINIMAL_DATA = _get_example_data("minimal")
ADVANCED_DATA = _get_example_data("advanced")
INVALID_MINIMAL_DATA = _get_example_data("invalid_minimal")
