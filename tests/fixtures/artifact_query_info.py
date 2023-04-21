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

"""Example of ArtifactQueryInfo objects."""

from metldata.artifacts_rest.artifact_info import load_artifact_query_info
from tests.fixtures.workflows import EXAMPLE_ARTIFACT_MODELS

# artifact query infos for the example workflow:
EXAMPLE_ARTIFACT_QUERY_INFOS = [
    load_artifact_query_info(
        name=artifact_name, description=artifact_name, model=artifact_model
    )
    for artifact_name, artifact_model in EXAMPLE_ARTIFACT_MODELS.items()
]
