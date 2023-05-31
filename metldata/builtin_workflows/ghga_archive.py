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

"""A GHGA Archive-specific workflow."""

from metldata.builtin_transformations.delete_slots import SLOT_DELETION_TRANSFORMATION
from metldata.builtin_transformations.infer_references import (
    REFERENCE_INFERENCE_TRANSFORMATION,
)
from metldata.transform.base import WorkflowDefinition, WorkflowStep

GHGA_ARCHIVE_WORKFLOW = WorkflowDefinition(
    description=(
        "A GHGA Archive-specific workflow implementing the steps as defined here:"
        + " https://docs.ghga-dev.de/main/architecture_concepts/ac002_metadata_lifecycl"
        + "e.html"
    ),
    steps={
        "infer_references": WorkflowStep(
            description="A step for inferring references.",
            transformation_definition=REFERENCE_INFERENCE_TRANSFORMATION,
            input=None,
        ),
        "delete_slots": WorkflowStep(
            description="A step for deleting slots.",
            transformation_definition=SLOT_DELETION_TRANSFORMATION,
            input="infer_references",
        ),
    },
    artifacts={
        "inferred_and_restricted": "infer_references",
        "inferred_and_public": "delete_slots",
    },
)
