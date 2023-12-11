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

"""Example models."""

from schemapack.load import load_schemapack
from schemapack.spec.schemapack import SchemaPack

from tests.schemapack_.fixtures.utils import BASE_DIR

EXAMPLE_MODEL_DIR = BASE_DIR / "example_models"
VALID_MINIMAL_MODEL_EXAMPLE_PATH = EXAMPLE_MODEL_DIR / "minimal_model.yaml"


def _get_example_model(name: str) -> SchemaPack:
    """Get example model."""

    return load_schemapack(EXAMPLE_MODEL_DIR / f"{name}.schemapack.yaml")


VALID_MINIMAL_MODEL = _get_example_model("minimal")
VALID_MODELS = [VALID_MINIMAL_MODEL]
