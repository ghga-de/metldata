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

"""Config Parameter Modeling and Parsing"""

from pathlib import Path

from ghga_service_chassis_lib.config import config_from_yaml
from pydantic import BaseSettings, Field


# Please adapt config prefix and remove unnecessary config bases:
@config_from_yaml(prefix="metldata")
class Config(BaseSettings):
    """Config parameters and their defaults."""

    metadata_model: Path = Field(
        ..., description="The path to the metadata model defined in LinkML."
    )
    submission_store_dir: Path = Field(
        ..., description="The directory where the submission JSONs will be stored."
    )
    source_events_dir: Path = Field(
        ..., description="The directory to which source events are published as JSON."
    )
